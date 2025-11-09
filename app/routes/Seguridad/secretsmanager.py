"""
Rutas para AWS Secrets Manager
"""
import boto3
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

secretsmanager_bp = Blueprint('secretsmanager', __name__, url_prefix='/secretsmanager')


@secretsmanager_bp.route('/')
def index():
    """Página principal de Secrets Manager"""
    try:
        sm = get_aws_client('secretsmanager')
        secrets = sm.list_secrets()

        secret_list = []
        for secret in secrets.get('SecretList', []):
            secret_list.append({
                'name': secret['Name'],
                'arn': secret['ARN'],
                'description': secret.get('Description', ''),
                'created_date': secret['CreatedDate'],
                'last_changed_date': secret.get('LastChangedDate'),
                'primary_region': secret.get('PrimaryRegion', ''),
                'secret_versions_to_stages': secret.get('SecretVersionsToStages', {}),
                'tags': secret.get('Tags', [])
            })

        return render_template('Seguridad/secretsmanager/index.html', secrets=secret_list)
    except Exception as e:
        flash(f'Error obteniendo secretos: {str(e)}', 'error')
        return render_template('Seguridad/secretsmanager/index.html', secrets=[])


@secretsmanager_bp.route('/create', methods=['GET', 'POST'])
def create_secret():
    """Crear un nuevo secreto"""
    if request.method == 'POST':
        try:
            sm = get_aws_client('secretsmanager')

            name = request.form.get('name')
            secret_string = request.form.get('secret_string')
            description = request.form.get('description', '')
            kms_key_id = request.form.get('kms_key_id', '')

            # Crear el secreto
            params = {
                'Name': name,
                'SecretString': secret_string,
                'Description': description
            }

            if kms_key_id:
                params['KmsKeyId'] = kms_key_id

            response = sm.create_secret(**params)

            flash(f'Secreto "{name}" creado exitosamente', 'success')
            return redirect(url_for('secretsmanager.index'))

        except Exception as e:
            flash(f'Error creando secreto: {str(e)}', 'error')
            return redirect(url_for('secretsmanager.create_secret'))

    return render_template('Seguridad/secretsmanager/create_secret.html')


@secretsmanager_bp.route('/<secret_name>/delete', methods=['POST'])
def delete_secret(secret_name):
    """Eliminar un secreto"""
    try:
        sm = get_aws_client('secretsmanager')

        # Verificar si debe eliminarse inmediatamente o programarse
        force_delete = request.form.get('force_delete', 'false').lower() == 'true'

        if force_delete:
            sm.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True
            )
            flash(f'Secreto "{secret_name}" eliminado permanentemente', 'success')
        else:
            # Programar eliminación (por defecto 7 días)
            recovery_window = int(request.form.get('recovery_window', 7))
            sm.delete_secret(
                SecretId=secret_name,
                RecoveryWindowInDays=recovery_window
            )
            flash(f'Eliminación de secreto "{secret_name}" programada para {recovery_window} días', 'success')

    except Exception as e:
        flash(f'Error eliminando secreto: {str(e)}', 'error')

    return redirect(url_for('secretsmanager.index'))


@secretsmanager_bp.route('/<secret_name>/restore', methods=['POST'])
def restore_secret(secret_name):
    """Restaurar un secreto eliminado"""
    try:
        sm = get_aws_client('secretsmanager')
        sm.restore_secret(SecretId=secret_name)
        flash(f'Secreto "{secret_name}" restaurado exitosamente', 'success')
    except Exception as e:
        flash(f'Error restaurando secreto: {str(e)}', 'error')

    return redirect(url_for('secretsmanager.index'))


@secretsmanager_bp.route('/<secret_name>/value', methods=['GET', 'POST'])
def get_secret_value(secret_name):
    """Obtener el valor de un secreto"""
    if request.method == 'POST':
        try:
            sm = get_aws_client('secretsmanager')

            # Obtener el valor del secreto
            response = sm.get_secret_value(SecretId=secret_name)
            secret_value = response.get('SecretString', 'No se pudo obtener el valor')

            return render_template('Seguridad/secretsmanager/secret_value.html',
                                 secret_name=secret_name,
                                 secret_value=secret_value)

        except Exception as e:
            flash(f'Error obteniendo valor del secreto: {str(e)}', 'error')
            return redirect(url_for('secretsmanager.index'))

    return render_template('Seguridad/secretsmanager/get_secret_value.html', secret_name=secret_name)


@secretsmanager_bp.route('/<secret_name>/update', methods=['GET', 'POST'])
def update_secret(secret_name):
    """Actualizar un secreto"""
    if request.method == 'POST':
        try:
            sm = get_aws_client('secretsmanager')

            secret_string = request.form.get('secret_string')
            description = request.form.get('description', '')
            kms_key_id = request.form.get('kms_key_id', '')

            # Actualizar el secreto
            params = {
                'SecretId': secret_name,
                'SecretString': secret_string
            }

            if description:
                params['Description'] = description
            if kms_key_id:
                params['KmsKeyId'] = kms_key_id

            sm.update_secret(**params)

            flash(f'Secreto "{secret_name}" actualizado exitosamente', 'success')
            return redirect(url_for('secretsmanager.index'))

        except Exception as e:
            flash(f'Error actualizando secreto: {str(e)}', 'error')
            return redirect(url_for('secretsmanager.update_secret', secret_name=secret_name))

    # GET: Obtener información actual del secreto
    try:
        sm = get_aws_client('secretsmanager')
        secret = sm.describe_secret(SecretId=secret_name)

        return render_template('Seguridad/secretsmanager/update_secret.html',
                             secret_name=secret_name,
                             current_description=secret.get('Description', ''))

    except Exception as e:
        flash(f'Error obteniendo información del secreto: {str(e)}', 'error')
        return redirect(url_for('secretsmanager.index'))


@secretsmanager_bp.route('/<secret_name>/rotate', methods=['GET', 'POST'])
def rotate_secret(secret_name):
    """Rotar un secreto"""
    if request.method == 'POST':
        try:
            sm = get_aws_client('secretsmanager')

            # Iniciar rotación
            sm.rotate_secret(
                SecretId=secret_name,
                RotationRules={
                    'AutomaticallyAfterDays': int(request.form.get('rotation_days', 30))
                }
            )

            flash(f'Rotación de secreto "{secret_name}" iniciada exitosamente', 'success')
            return redirect(url_for('secretsmanager.index'))

        except Exception as e:
            flash(f'Error rotando secreto: {str(e)}', 'error')
            return redirect(url_for('secretsmanager.rotate_secret', secret_name=secret_name))

    return render_template('Seguridad/secretsmanager/rotate_secret.html', secret_name=secret_name)