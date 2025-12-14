"""
Rutas web para configuración de la aplicación (credenciales AWS, etc.)
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import os
import boto3
from app.utils.aws_client import get_aws_client

setup_bp = Blueprint('setup', __name__, url_prefix='/setup')
# Blueprint adicional con rutas en español
configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/configuracion')


@setup_bp.route('/')
@configuracion_bp.route('/')
def index():
    """Página principal de configuración de la aplicación"""
    return render_template('Setup/index.html')


@setup_bp.route('/aws-credentials', methods=['GET', 'POST'])
@configuracion_bp.route('/aws-credentials', methods=['GET', 'POST'])
def aws_credentials():
    """Configurar credenciales AWS"""
    if request.method == 'POST':
        try:
            # Obtener credenciales del formulario
            access_key = request.form.get('aws_access_key_id', '').strip()
            secret_key = request.form.get('aws_secret_access_key', '').strip()
            session_token = request.form.get('aws_session_token', '').strip()
            region = request.form.get('aws_default_region', 'us-east-1').strip()

            # Validar campos requeridos
            if not access_key or not secret_key:
                flash('Access Key ID y Secret Access Key son requeridos', 'error')
                return render_template('Setup/aws_credentials.html')

            # Guardar en sesión
            session['aws_access_key_id'] = access_key
            session['aws_secret_access_key'] = secret_key
            session['aws_session_token'] = session_token if session_token else None
            session['aws_default_region'] = region

            # Probar conexión
            try:
                sts = boto3.client(
                    'sts',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=session_token if session_token else None,
                    region_name=region
                )
                identity = sts.get_caller_identity()
                account_id = identity.get('Account')

                flash(f'✅ Credenciales configuradas correctamente. Cuenta: {account_id}', 'success')

                # Redirigir a la página principal
                return redirect(url_for('index'))

            except Exception as e:
                flash(f'❌ Error de conexión: {str(e)}', 'error')
                return render_template('Setup/aws_credentials.html')

        except Exception as e:
            flash(f'Error guardando configuración: {str(e)}', 'error')

    # GET: Mostrar formulario con valores actuales
    current_config = {
        'aws_access_key_id': session.get('aws_access_key_id', ''),
        'aws_secret_access_key': session.get('aws_secret_access_key', ''),
        'aws_session_token': session.get('aws_session_token', ''),
        'aws_default_region': session.get('aws_default_region', 'us-east-1')
    }

    return render_template('Setup/aws_credentials.html', config=current_config)


@setup_bp.route('/test-connection')
@configuracion_bp.route('/test-connection')
def test_connection():
    """Probar conexión con las credenciales actuales"""
    try:
        sts = get_aws_client('sts')
        identity = sts.get_caller_identity()

        return {
            'success': True,
            'account_id': identity.get('Account'),
            'user_arn': identity.get('Arn'),
            'region': session.get('aws_default_region', 'us-east-1')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@setup_bp.route('/clear-credentials')
@configuracion_bp.route('/clear-credentials')
def clear_credentials():
    """Limpiar credenciales de la sesión"""
    session.pop('aws_access_key_id', None)
    session.pop('aws_secret_access_key', None)
    session.pop('aws_session_token', None)
    session.pop('aws_default_region', None)

    flash('Credenciales limpiadas de la sesión', 'info')
    return redirect(url_for('setup.aws_credentials'))