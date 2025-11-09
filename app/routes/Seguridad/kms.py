"""
Rutas para AWS Key Management Service (KMS)
"""
import boto3
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.aws_client import get_aws_client

kms_bp = Blueprint('kms', __name__, url_prefix='/kms')


@kms_bp.route('/')
def index():
    """Página principal de KMS"""
    try:
        kms = get_aws_client('kms')
        keys = kms.list_keys(Limit=50)

        # Obtener detalles de cada clave
        key_details = []
        for key in keys.get('Keys', []):
            try:
                key_info = kms.describe_key(KeyId=key['KeyId'])
                aliases = kms.list_aliases(KeyId=key['KeyId'])

                key_details.append({
                    'key_id': key['KeyId'],
                    'key_arn': key_info['KeyMetadata']['Arn'],
                    'description': key_info['KeyMetadata'].get('Description', ''),
                    'key_state': key_info['KeyMetadata']['KeyState'],
                    'key_usage': key_info['KeyMetadata']['KeyUsage'],
                    'key_spec': key_info['KeyMetadata']['KeySpec'],
                    'origin': key_info['KeyMetadata']['Origin'],
                    'creation_date': key_info['KeyMetadata']['CreationDate'],
                    'enabled': key_info['KeyMetadata']['Enabled'],
                    'aliases': [alias['AliasName'] for alias in aliases.get('Aliases', []) if not alias['AliasName'].startswith('alias/aws/')]
                })
            except Exception as e:
                # Si hay error obteniendo detalles de una clave, continuar con las demás
                key_details.append({
                    'key_id': key['KeyId'],
                    'error': str(e)
                })

        return render_template('Seguridad/kms/index.html', keys=key_details)
    except Exception as e:
        flash(f'Error al listar claves KMS: {str(e)}', 'error')
        return render_template('Seguridad/kms/index.html', keys=[])


@kms_bp.route('/create', methods=['GET', 'POST'])
def create_key():
    """Crear una nueva clave KMS"""
    if request.method == 'POST':
        try:
            kms = get_aws_client('kms')

            # Parámetros de la clave
            description = request.form.get('description', '')
            key_usage = request.form.get('key_usage', 'ENCRYPT_DECRYPT')
            key_spec = request.form.get('key_spec', 'SYMMETRIC_DEFAULT')
            alias = request.form.get('alias', '')

            # Crear la clave
            create_params = {
                'Description': description,
                'KeyUsage': key_usage,
                'KeySpec': key_spec
            }

            response = kms.create_key(**create_params)
            key_id = response['KeyMetadata']['KeyId']

            # Crear alias si se especificó
            if alias:
                try:
                    kms.create_alias(
                        AliasName=f'alias/{alias}',
                        TargetKeyId=key_id
                    )
                except Exception as e:
                    flash(f'Clave creada pero error al crear alias: {str(e)}', 'warning')

            flash(f'Clave KMS creada exitosamente. ID: {key_id}', 'success')
            return redirect(url_for('kms.index'))

        except Exception as e:
            flash(f'Error al crear clave KMS: {str(e)}', 'error')
            return redirect(url_for('kms.create_key'))

    return render_template('Seguridad/kms/create_key.html')


@kms_bp.route('/<key_id>/disable', methods=['POST'])
def disable_key(key_id):
    """Deshabilitar una clave KMS"""
    try:
        kms = get_aws_client('kms')
        kms.disable_key(KeyId=key_id)
        flash(f'Clave KMS {key_id} deshabilitada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al deshabilitar clave KMS: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/enable', methods=['POST'])
def enable_key(key_id):
    """Habilitar una clave KMS"""
    try:
        kms = get_aws_client('kms')
        kms.enable_key(KeyId=key_id)
        flash(f'Clave KMS {key_id} habilitada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al habilitar clave KMS: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/schedule-deletion', methods=['POST'])
def schedule_deletion(key_id):
    """Programar eliminación de una clave KMS"""
    try:
        kms = get_aws_client('kms')
        pending_days = int(request.form.get('pending_days', 7))

        kms.schedule_key_deletion(
            KeyId=key_id,
            PendingWindowInDays=pending_days
        )

        flash(f'Eliminación de clave KMS {key_id} programada para {pending_days} días', 'success')
    except Exception as e:
        flash(f'Error al programar eliminación: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/cancel-deletion', methods=['POST'])
def cancel_deletion(key_id):
    """Cancelar eliminación programada de una clave KMS"""
    try:
        kms = get_aws_client('kms')
        kms.cancel_key_deletion(KeyId=key_id)
        flash(f'Eliminación programada de clave KMS {key_id} cancelada', 'success')
    except Exception as e:
        flash(f'Error al cancelar eliminación: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/enable-rotation', methods=['POST'])
def enable_key_rotation(key_id):
    """Habilitar rotación automática de clave KMS"""
    try:
        kms = get_aws_client('kms')
        kms.enable_key_rotation(KeyId=key_id)
        flash(f'Rotación automática habilitada para clave KMS {key_id}', 'success')
    except Exception as e:
        flash(f'Error al habilitar rotación: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/disable-rotation', methods=['POST'])
def disable_key_rotation(key_id):
    """Deshabilitar rotación automática de clave KMS"""
    try:
        kms = get_aws_client('kms')
        kms.disable_key_rotation(KeyId=key_id)
        flash(f'Rotación automática deshabilitada para clave KMS {key_id}', 'success')
    except Exception as e:
        flash(f'Error al deshabilitar rotación: {str(e)}', 'error')

    return redirect(url_for('kms.index'))


@kms_bp.route('/<key_id>/encrypt', methods=['GET', 'POST'])
def encrypt_data(key_id):
    """Encriptar datos con una clave KMS"""
    if request.method == 'POST':
        try:
            kms = get_aws_client('kms')
            plaintext = request.form.get('plaintext', '')

            if not plaintext:
                flash('Debe proporcionar datos para encriptar', 'error')
                return redirect(url_for('kms.encrypt_data', key_id=key_id))

            # Encriptar los datos
            response = kms.encrypt(
                KeyId=key_id,
                Plaintext=plaintext.encode('utf-8')
            )

            ciphertext = response['CiphertextBlob']

            return render_template('Seguridad/kms/encrypt_result.html',
                                 key_id=key_id,
                                 plaintext=plaintext,
                                 ciphertext=ciphertext.hex())

        except Exception as e:
            flash(f'Error al encriptar datos: {str(e)}', 'error')
            return redirect(url_for('kms.encrypt_data', key_id=key_id))

    return render_template('Seguridad/kms/encrypt_data.html', key_id=key_id)


@kms_bp.route('/<key_id>/decrypt', methods=['GET', 'POST'])
def decrypt_data(key_id):
    """Desencriptar datos con una clave KMS"""
    if request.method == 'POST':
        try:
            kms = get_aws_client('kms')
            ciphertext_hex = request.form.get('ciphertext', '')

            if not ciphertext_hex:
                flash('Debe proporcionar datos encriptados', 'error')
                return redirect(url_for('kms.decrypt_data', key_id=key_id))

            # Convertir de hex a bytes
            ciphertext = bytes.fromhex(ciphertext_hex)

            # Desencriptar los datos
            response = kms.decrypt(
                KeyId=key_id,
                CiphertextBlob=ciphertext
            )

            plaintext = response['Plaintext'].decode('utf-8')

            return render_template('Seguridad/kms/decrypt_result.html',
                                 key_id=key_id,
                                 ciphertext=ciphertext_hex,
                                 plaintext=plaintext)

        except Exception as e:
            flash(f'Error al desencriptar datos: {str(e)}', 'error')
            return redirect(url_for('kms.decrypt_data', key_id=key_id))

    return render_template('Seguridad/kms/decrypt_data.html', key_id=key_id)


@kms_bp.route('/<key_id>/generate-data-key', methods=['GET', 'POST'])
def generate_data_key(key_id):
    """Generar una clave de datos encriptada"""
    if request.method == 'POST':
        try:
            kms = get_aws_client('kms')
            key_spec = request.form.get('key_spec', 'AES_256')

            response = kms.generate_data_key(
                KeyId=key_id,
                KeySpec=key_spec
            )

            plaintext_key = response['Plaintext']
            encrypted_key = response['CiphertextBlob']

            return render_template('Seguridad/kms/data_key_result.html',
                                 key_id=key_id,
                                 key_spec=key_spec,
                                 plaintext_key=plaintext_key.hex(),
                                 encrypted_key=encrypted_key.hex())

        except Exception as e:
            flash(f'Error al generar clave de datos: {str(e)}', 'error')
            return redirect(url_for('kms.generate_data_key', key_id=key_id))

    return render_template('Seguridad/kms/generate_data_key.html', key_id=key_id)