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

            # Guardar en sesión y marcarla como permanente
            session.permanent = True
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


@setup_bp.route('/ai-provider', methods=['GET', 'POST'])
@configuracion_bp.route('/ai-provider', methods=['GET', 'POST'])
def ai_provider():
    """Configurar proveedor de IA"""
    if request.method == 'POST':
        try:
            provider = request.form.get('ai_provider', 'gemini').strip()
            gemini_key = request.form.get('gemini_api_key', '').strip()
            deepseek_key = request.form.get('deepseek_api_key', '').strip()

            # Obtener keys actuales de la sesión
            current_gemini = session.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
            current_deepseek = session.get('deepseek_api_key') or os.environ.get('DEEPSEEK_API_KEY')

            # Si no se proporciona nueva key, mantener la actual
            if not gemini_key and current_gemini:
                gemini_key = current_gemini
            if not deepseek_key and current_deepseek:
                deepseek_key = current_deepseek

            # Validar que se proporcione la API key del proveedor seleccionado
            if provider == 'gemini' and not gemini_key:
                flash('Debes proporcionar la API Key de Gemini o ya tenerla configurada', 'error')
                return render_template('Setup/ai_provider.html', config={
                    'ai_provider': provider,
                    'gemini_api_key': bool(current_gemini),
                    'deepseek_api_key': bool(current_deepseek)
                })
            
            if provider == 'deepseek' and not deepseek_key:
                flash('Debes proporcionar la API Key de DeepSeek o ya tenerla configurada', 'error')
                return render_template('Setup/ai_provider.html', config={
                    'ai_provider': provider,
                    'gemini_api_key': bool(current_gemini),
                    'deepseek_api_key': bool(current_deepseek)
                })

            # Guardar en sesión solo las keys proporcionadas o actualizadas
            session.permanent = True
            session['ai_provider'] = provider
            if gemini_key:
                session['gemini_api_key'] = gemini_key
            if deepseek_key:
                session['deepseek_api_key'] = deepseek_key

            # También actualizar el archivo .env
            try:
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
                
                # Leer contenido actual
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Actualizar valores
                    with open(env_path, 'w', encoding='utf-8') as f:
                        for line in lines:
                            if line.startswith('AI_PROVIDER='):
                                f.write(f'AI_PROVIDER={provider}\n')
                            elif line.startswith('GEMINI_API_KEY=') and gemini_key:
                                f.write(f'GEMINI_API_KEY={gemini_key}\n')
                            elif line.startswith('DEEPSEEK_API_KEY=') and deepseek_key:
                                f.write(f'DEEPSEEK_API_KEY={deepseek_key}\n')
                            else:
                                f.write(line)
                    
                    # Actualizar variables de entorno
                    os.environ['AI_PROVIDER'] = provider
                    if gemini_key:
                        os.environ['GEMINI_API_KEY'] = gemini_key
                    if deepseek_key:
                        os.environ['DEEPSEEK_API_KEY'] = deepseek_key
                
                flash(f'✅ Proveedor de IA configurado: {provider.upper()}', 'success')
                return redirect(url_for('setup.index'))
                
            except Exception as e:
                flash(f'Advertencia: Configuración guardada en sesión pero no en .env: {str(e)}', 'warning')
                return redirect(url_for('setup.index'))

        except Exception as e:
            flash(f'Error guardando configuración: {str(e)}', 'error')

    # GET: Mostrar formulario con valores actuales (sin exponer las keys)
    current_config = {
        'ai_provider': session.get('ai_provider', os.environ.get('AI_PROVIDER', 'gemini')),
        # Solo indicar si la key existe, no mostrar su valor
        'gemini_api_key': bool(session.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')),
        'deepseek_api_key': bool(session.get('deepseek_api_key') or os.environ.get('DEEPSEEK_API_KEY'))
    }

    return render_template('Setup/ai_provider.html', config=current_config)