from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client
import boto3
import json

bp = Blueprint('s3', __name__)

@bp.route('/s3')
def index():
    return render_template('Almacenamiento/s3/index.html')

@bp.route('/s3/buckets')
def buckets():
    try:
        s3 = get_aws_client('s3')
        buckets = s3.list_buckets()
        bucket_list = []
        for bucket in buckets['Buckets']:
            bucket_list.append({
                'name': bucket['Name'],
                'creation_date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('Almacenamiento/s3/buckets.html', buckets=bucket_list)
    except Exception as e:
        flash(f'Error obteniendo buckets S3: {str(e)}', 'error')
        return render_template('Almacenamiento/s3/buckets.html', buckets=[])

@bp.route('/s3/bucket/<bucket_name>')
def bucket_detail(bucket_name):
    try:
        s3 = get_aws_client('s3')
        objects = s3.list_objects_v2(Bucket=bucket_name)
        object_list = []
        if 'Contents' in objects:
            for obj in objects['Contents']:
                object_list.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                })
        return render_template('Almacenamiento/s3/bucket_detail.html', bucket_name=bucket_name, objects=object_list)
    except Exception as e:
        flash(f'Error obteniendo objetos del bucket: {str(e)}', 'error')
        return render_template('Almacenamiento/s3/bucket_detail.html', bucket_name=bucket_name, objects=[])

@bp.route('/s3/bucket/<bucket_name>/delete', methods=['POST'])
def delete_bucket(bucket_name):
    """Elimina un bucket S3"""
    try:
        s3 = get_aws_client('s3')
        force = request.form.get('force', 'false').lower() == 'true'
        
        # Si force=True, eliminar todos los objetos primero
        if force:
            try:
                # Eliminar todos los objetos
                paginator = s3.get_paginator('list_objects_v2')
                for page in paginator.paginate(Bucket=bucket_name):
                    if 'Contents' in page:
                        objects = [{'Key': obj['Key']} for obj in page['Contents']]
                        if objects:
                            s3.delete_objects(
                                Bucket=bucket_name,
                                Delete={'Objects': objects}
                            )
                
                # Eliminar versiones si el versionado está habilitado
                version_paginator = s3.get_paginator('list_object_versions')
                for page in version_paginator.paginate(Bucket=bucket_name):
                    versions = []
                    if 'Versions' in page:
                        versions.extend([{'Key': v['Key'], 'VersionId': v['VersionId']} 
                                       for v in page['Versions']])
                    if 'DeleteMarkers' in page:
                        versions.extend([{'Key': d['Key'], 'VersionId': d['VersionId']} 
                                       for d in page['DeleteMarkers']])
                    
                    if versions:
                        s3.delete_objects(
                            Bucket=bucket_name,
                            Delete={'Objects': versions}
                        )
            except Exception as e:
                flash(f'Advertencia eliminando objetos: {str(e)}', 'warning')
        
        # Eliminar el bucket
        s3.delete_bucket(Bucket=bucket_name)
        flash(f'Bucket {bucket_name} eliminado exitosamente', 'success')
        
    except Exception as e:
        error_msg = str(e)
        if 'BucketNotEmpty' in error_msg:
            flash(f'Error: El bucket {bucket_name} no está vacío. Activa "force" para eliminar todos los objetos primero.', 'error')
        else:
            flash(f'Error eliminando bucket: {error_msg}', 'error')
    
    return redirect(url_for('s3.buckets'))

@bp.route('/s3/bucket/<bucket_name>/upload', methods=['GET', 'POST'])
def upload_object(bucket_name):
    """Subir un objeto a un bucket S3"""
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            object_key = request.form.get('object_key')
            content_type = request.form.get('content_type', 'application/octet-stream')

            if not file or not object_key:
                flash('Archivo y clave del objeto son requeridos', 'error')
                return redirect(request.url)

            s3 = get_aws_client('s3')

            # Subir el archivo
            s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=file.read(),
                ContentType=content_type
            )

            flash(f'Objeto "{object_key}" subido exitosamente al bucket {bucket_name}', 'success')
            return redirect(url_for('s3.bucket_detail', bucket_name=bucket_name))

        except Exception as e:
            flash(f'Error subiendo objeto: {str(e)}', 'error')

    return render_template('Almacenamiento/s3/upload_object.html', bucket_name=bucket_name)

@bp.route('/s3/bucket/<bucket_name>/object/<path:object_key>/delete', methods=['POST'])
def delete_object(bucket_name, object_key):
    """Eliminar un objeto de un bucket S3"""
    try:
        s3 = get_aws_client('s3')
        s3.delete_object(Bucket=bucket_name, Key=object_key)
        flash(f'Objeto "{object_key}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando objeto: {str(e)}', 'error')

    return redirect(url_for('s3.bucket_detail', bucket_name=bucket_name))

@bp.route('/s3/bucket/<bucket_name>/policy')
def get_bucket_policy(bucket_name):
    """Obtener la política del bucket"""
    try:
        s3 = get_aws_client('s3')
        policy = s3.get_bucket_policy(Bucket=bucket_name)
        policy_document = json.loads(policy['Policy'])
        return render_template('Almacenamiento/s3/bucket_policy.html',
                             bucket_name=bucket_name,
                             policy=policy_document)
    except Exception as e:
        if 'NoSuchBucketPolicy' in str(e):
            return render_template('Almacenamiento/s3/bucket_policy.html',
                                 bucket_name=bucket_name,
                                 policy=None)
        flash(f'Error obteniendo política del bucket: {str(e)}', 'error')
        return render_template('Almacenamiento/s3/bucket_policy.html',
                             bucket_name=bucket_name,
                             policy=None)

@bp.route('/s3/bucket/<bucket_name>/policy/edit', methods=['GET', 'POST'])
def put_bucket_policy(bucket_name):
    """Establecer la política del bucket"""
    if request.method == 'POST':
        try:
            policy_text = request.form.get('policy')
            if not policy_text:
                flash('La política no puede estar vacía', 'error')
                return redirect(request.url)

            # Validar JSON
            policy_document = json.loads(policy_text)

            s3 = get_aws_client('s3')
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy_document)
            )

            flash('Política del bucket actualizada exitosamente', 'success')
            return redirect(url_for('s3.get_bucket_policy', bucket_name=bucket_name))

        except json.JSONDecodeError:
            flash('La política debe ser un JSON válido', 'error')
        except Exception as e:
            flash(f'Error actualizando política del bucket: {str(e)}', 'error')

    # GET: mostrar formulario con política actual
    try:
        s3 = get_aws_client('s3')
        policy = s3.get_bucket_policy(Bucket=bucket_name)
        current_policy = json.dumps(json.loads(policy['Policy']), indent=2)
    except Exception:
        current_policy = ''

    return render_template('Almacenamiento/s3/edit_bucket_policy.html',
                         bucket_name=bucket_name,
                         current_policy=current_policy)

@bp.route('/s3/bucket/<bucket_name>/lifecycle')
def get_bucket_lifecycle(bucket_name):
    """Obtener la configuración de lifecycle del bucket"""
    try:
        s3 = get_aws_client('s3')
        lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return render_template('Almacenamiento/s3/bucket_lifecycle.html',
                             bucket_name=bucket_name,
                             lifecycle=lifecycle.get('Rules', []))
    except Exception as e:
        if 'NoSuchLifecycleConfiguration' in str(e):
            return render_template('Almacenamiento/s3/bucket_lifecycle.html',
                                 bucket_name=bucket_name,
                                 lifecycle=[])
        flash(f'Error obteniendo configuración de lifecycle: {str(e)}', 'error')
        return render_template('Almacenamiento/s3/bucket_lifecycle.html',
                             bucket_name=bucket_name,
                             lifecycle=[])

@bp.route('/s3/bucket/<bucket_name>/lifecycle/edit', methods=['GET', 'POST'])
def put_bucket_lifecycle(bucket_name):
    """Establecer la configuración de lifecycle del bucket"""
    if request.method == 'POST':
        try:
            lifecycle_text = request.form.get('lifecycle')
            if not lifecycle_text:
                flash('La configuración de lifecycle no puede estar vacía', 'error')
                return redirect(request.url)

            # Validar JSON
            lifecycle_config = json.loads(lifecycle_text)

            s3 = get_aws_client('s3')
            s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )

            flash('Configuración de lifecycle actualizada exitosamente', 'success')
            return redirect(url_for('s3.get_bucket_lifecycle', bucket_name=bucket_name))

        except json.JSONDecodeError:
            flash('La configuración debe ser un JSON válido', 'error')
        except Exception as e:
            flash(f'Error actualizando configuración de lifecycle: {str(e)}', 'error')

    # GET: mostrar formulario con configuración actual
    try:
        s3 = get_aws_client('s3')
        lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        current_lifecycle = json.dumps(lifecycle.get('Rules', []), indent=2)
    except Exception:
        current_lifecycle = '[]'

    return render_template('Almacenamiento/s3/edit_bucket_lifecycle.html',
                         bucket_name=bucket_name,
                         current_lifecycle=current_lifecycle)

@bp.route('/s3/bucket/<bucket_name>/versioning', methods=['GET', 'POST'])
def enable_bucket_versioning(bucket_name):
    """Habilitar/deshabilitar versionado del bucket"""
    if request.method == 'POST':
        try:
            status = request.form.get('status')
            if status not in ['Enabled', 'Suspended']:
                flash('Estado de versionado inválido', 'error')
                return redirect(request.url)

            s3 = get_aws_client('s3')
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': status}
            )

            flash(f'Versionado del bucket {"habilitado" if status == "Enabled" else "deshabilitado"} exitosamente', 'success')
            return redirect(url_for('s3.bucket_detail', bucket_name=bucket_name))

        except Exception as e:
            flash(f'Error cambiando versionado del bucket: {str(e)}', 'error')

    # GET: mostrar estado actual
    try:
        s3 = get_aws_client('s3')
        versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        current_status = versioning.get('Status', 'Suspended')
    except Exception as e:
        flash(f'Error obteniendo estado de versionado: {str(e)}', 'error')
        current_status = 'Suspended'

    return render_template('Almacenamiento/s3/bucket_versioning.html',
                         bucket_name=bucket_name,
                         current_status=current_status)

@bp.route('/s3/bucket/<bucket_name>/cors')
def get_bucket_cors(bucket_name):
    """Obtener la configuración CORS del bucket"""
    try:
        s3 = get_aws_client('s3')
        cors = s3.get_bucket_cors(Bucket=bucket_name)
        return render_template('Almacenamiento/s3/bucket_cors.html',
                             bucket_name=bucket_name,
                             cors=cors.get('CORSRules', []))
    except Exception as e:
        if 'NoSuchCORSConfiguration' in str(e):
            return render_template('Almacenamiento/s3/bucket_cors.html',
                                 bucket_name=bucket_name,
                                 cors=[])
        flash(f'Error obteniendo configuración CORS: {str(e)}', 'error')
        return render_template('Almacenamiento/s3/bucket_cors.html',
                             bucket_name=bucket_name,
                             cors=[])

@bp.route('/s3/bucket/<bucket_name>/cors/edit', methods=['GET', 'POST'])
def put_bucket_cors(bucket_name):
    """Establecer la configuración CORS del bucket"""
    if request.method == 'POST':
        try:
            cors_text = request.form.get('cors')
            if not cors_text:
                flash('La configuración CORS no puede estar vacía', 'error')
                return redirect(request.url)

            # Validar JSON
            cors_config = json.loads(cors_text)

            s3 = get_aws_client('s3')
            s3.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_config
            )

            flash('Configuración CORS actualizada exitosamente', 'success')
            return redirect(url_for('s3.get_bucket_cors', bucket_name=bucket_name))

        except json.JSONDecodeError:
            flash('La configuración debe ser un JSON válido', 'error')
        except Exception as e:
            flash(f'Error actualizando configuración CORS: {str(e)}', 'error')

    # GET: mostrar formulario con configuración actual
    try:
        s3 = get_aws_client('s3')
        cors = s3.get_bucket_cors(Bucket=bucket_name)
        current_cors = json.dumps(cors.get('CORSRules', []), indent=2)
    except Exception:
        current_cors = '[]'

    return render_template('Almacenamiento/s3/edit_bucket_cors.html',
                         bucket_name=bucket_name,
                         current_cors=current_cors)
