from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import boto3
import logging
import os

logger = logging.getLogger(__name__)

bp = Blueprint('ec2', __name__)

def get_all_active_instances(ec2_client):
    """Obtiene todas las instancias activas (no terminadas)"""
    paginator = ec2_client.get_paginator('describe_instances')
    active_instances = []
    try:
        for page in paginator.paginate():
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance.get('State', {}).get('Name') != 'terminated':
                        active_instances.append(instance.get('InstanceId'))
    except Exception as e:
        logger.exception('Error al obtener instancias activas: %s', e)
        raise
    return active_instances

def get_instances_with_environment_tag(ec2_client):
    """Obtiene IDs de instancias que tienen la etiqueta Environment"""
    paginator = ec2_client.get_paginator('describe_instances')
    filters = [{'Name': 'tag-key', 'Values': ['Environment']}]
    tagged_ids = []
    try:
        for page in paginator.paginate(Filters=filters):
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance.get('State', {}).get('Name') != 'terminated':
                        tagged_ids.append(instance.get('InstanceId'))
    except Exception as e:
        logger.exception('Error al obtener instancias con etiqueta Environment: %s', e)
        raise
    return tagged_ids

def get_instance_details(ec2_client, instance_ids):
    """Obtiene detalles completos de las instancias especificadas"""
    if not instance_ids:
        return []
    instance_list = []
    try:
        # describe_instances accepts up to 100 instance IDs; paginate if needed
        # We'll chunk the list to be safe
        for i in range(0, len(instance_ids), 100):
            chunk = instance_ids[i:i+100]
            instances_details = ec2_client.describe_instances(InstanceIds=chunk)
            for reservation in instances_details.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_list.append({
                        'id': instance.get('InstanceId'),
                        'state': instance.get('State', {}).get('Name'),
                        'type': instance.get('InstanceType'),
                        'public_ip': instance.get('PublicIpAddress', 'N/A'),
                        'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                        'launch_time': instance.get('LaunchTime').strftime('%Y-%m-%d %H:%M:%S') if instance.get('LaunchTime') else 'N/A',
                        'tags': instance.get('Tags', [])
                    })
    except Exception as e:
        logger.exception('Error al obtener detalles de instancias: %s', e)
        raise
    return instance_list

@bp.route('/ec2')
def index():
    return render_template('Computo/index.html')

@bp.route('/ec2/instances')
def instances():
    try:
        ec2 = get_aws_client('ec2')
        instances = ec2.describe_instances()
        instance_list = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_list.append({
                    'id': instance['InstanceId'],
                    'state': instance['State']['Name'],
                    'type': instance['InstanceType'],
                    'public_ip': instance.get('PublicIpAddress', 'N/A'),
                    'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                    'launch_time': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'tags': instance.get('Tags', [])
                })
        return render_template('Computo/instances.html', instances=instance_list)
    except Exception as e:
        flash(f'Error obteniendo instancias EC2: {str(e)}', 'error')
        return render_template('Computo/instances.html', instances=[])

@bp.route('/ec2/start/<instance_id>', methods=['POST'])
def start_instance(instance_id):
    try:
        ec2 = get_aws_client('ec2')
        ec2.start_instances(InstanceIds=[instance_id])
        flash(f'Instancia {instance_id} iniciada exitosamente', 'success')
    except Exception as e:
        flash(f'Error iniciando instancia: {str(e)}', 'error')
    return redirect(url_for('ec2.instances'))

@bp.route('/ec2/stop/<instance_id>', methods=['POST'])
def stop_instance(instance_id):
    logger.info(f'🛑 Petición recibida para detener instancia: {instance_id}')
    try:
        ec2 = get_aws_client('ec2')
        logger.info(f'Cliente EC2 creado para detener instancia {instance_id}')
        ec2.stop_instances(InstanceIds=[instance_id])
        logger.info(f'✅ Instancia {instance_id} detenida exitosamente')
        flash(f'Instancia {instance_id} detenida exitosamente', 'success')
    except Exception as e:
        logger.exception(f'❌ Error deteniendo instancia {instance_id}: {e}')
        flash(f'Error deteniendo instancia: {str(e)}', 'error')
    return redirect(url_for('ec2.instances'))

@bp.route('/ec2/tags')
def tags():
    return render_template('Computo/tags.html')

@bp.route('/ec2/tag-compliance')
def tag_compliance():
    try:
        ec2 = get_aws_client('ec2')
        
        # Obtener todas las instancias activas
        all_instance_ids = get_all_active_instances(ec2)
        
        # Obtener instancias con etiqueta Environment
        tagged_instance_ids = get_instances_with_environment_tag(ec2)
        
        # Encontrar instancias sin la etiqueta Environment
        untagged_instance_ids = [id for id in all_instance_ids if id not in tagged_instance_ids]
        
        # Obtener detalles de las instancias sin tag
        untagged_instances = get_instance_details(ec2, untagged_instance_ids)
        
        return render_template('Computo/tag_compliance.html', 
                             untagged_instances=untagged_instances,
                             total_instances=len(all_instance_ids),
                             tagged_instances=len(tagged_instance_ids),
                             untagged_count=len(untagged_instances))
                             
    except Exception as e:
        flash(f'Error obteniendo información de compliance de tags: {str(e)}', 'error')
        return render_template('Computo/tag_compliance.html', 
                             untagged_instances=[],
                             total_instances=0,
                             tagged_instances=0,
                             untagged_count=0)

@bp.route('/ec2/terminate-untagged', methods=['POST'])
def terminate_untagged():
    """Termina instancias sin la etiqueta Environment (política Tag or Terminate)"""
    logger.info('=== INICIANDO PROCESO DE TERMINACIÓN ===')

    try:
        # Usar configuración
        ec2 = boto3.client(
            'ec2',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )
        logger.info('Cliente EC2 creado para región: %s', ec2.meta.region_name)

        # Obtener todas las instancias
        instances = ec2.describe_instances()
        
        # Obtener instancias activas
        active_instances = []
        for reservation in instances.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                if instance.get('State', {}).get('Name') != 'terminated':
                    active_instances.append(instance.get('InstanceId'))

        logger.info('Instancias activas encontradas: %d', len(active_instances))

        # Buscar instancias con tag Environment 
        tagged_response = ec2.describe_instances(
            Filters=[{'Name': 'tag-key', 'Values': ['Environment']}]
        )
        tagged_instances = []
        for reservation in tagged_response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                if instance.get('State', {}).get('Name') != 'terminated':
                    tagged_instances.append(instance.get('InstanceId'))

        logger.info('Instancias con tag Environment: %d', len(tagged_instances))

        untagged = [iid for iid in active_instances if iid not in tagged_instances]
        logger.info('Instancias sin tag Environment: %d', len(untagged))

        if not untagged:
            flash('No se encontraron instancias no conformes para terminar', 'info')
            return redirect(url_for('ec2.tag_compliance'))

        # Terminar instancias 
        logger.info('🔄 Terminando instancias: %s', untagged)
        
        response = ec2.terminate_instances(InstanceIds=untagged)
        terminated = response.get('TerminatingInstances', [])
        
        logger.info('✅ Terminación exitosa. Instancias: %s', terminated)
        flash(f'Se inició la terminación de {len(terminated)} instancias no conformes.', 'success')

    except Exception as e:
        logger.exception('❌ Error en terminación: %s', e)
        flash(f'Error terminando instancias: {str(e)}', 'error')

    logger.info('=== FIN DEL PROCESO DE TERMINACIÓN ===')
    return redirect(url_for('ec2.tag_compliance'))

@bp.route('/ec2/create')
def create_instance():
    """Página para crear nueva instancia EC2"""
    try:
        ec2 = get_aws_client('ec2')

        # Obtener AMIs disponibles (Amazon Linux 2, Ubuntu, Windows)
        images_response = ec2.describe_images(
            Owners=['amazon'],
            Filters=[
                {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        amis = images_response.get('Images', [])[:10]  # Limitar a 10 AMIs recientes

        # Obtener tipos de instancia disponibles
        instance_types = [
            't2.micro', 't2.small', 't2.medium',
            't3.micro', 't3.small', 't3.medium',
            'm5.large', 'm5.xlarge', 'm5.2xlarge',
            'c5.large', 'c5.xlarge'
        ]

        # Obtener VPCs disponibles
        vpcs_response = ec2.describe_vpcs()
        vpcs = vpcs_response.get('Vpcs', [])

        # Obtener security groups
        sgs_response = ec2.describe_security_groups()
        security_groups = sgs_response.get('SecurityGroups', [])

        # Obtener key pairs
        key_pairs_response = ec2.describe_key_pairs()
        key_pairs = key_pairs_response.get('KeyPairs', [])

        return render_template('Computo/create.html',
                             amis=amis,
                             instance_types=instance_types,
                             vpcs=vpcs,
                             security_groups=security_groups,
                             key_pairs=key_pairs)

    except Exception as e:
        flash(f'Error cargando formulario de creación: {str(e)}', 'error')
        return redirect(url_for('ec2.index'))

@bp.route('/ec2/create', methods=['POST'])
def create_instance_post():
    """Crear nueva instancia EC2"""
    try:
        ec2 = get_aws_client('ec2')

        # Obtener datos del formulario
        image_id = request.form.get('image_id')
        instance_type = request.form.get('instance_type')
        key_name = request.form.get('key_name')
        security_group_ids = request.form.getlist('security_group_ids')
        vpc_id = request.form.get('vpc_id')
        subnet_id = request.form.get('subnet_id')
        instance_name = request.form.get('instance_name')
        user_data = request.form.get('user_data', '')

        # Validar campos requeridos
        if not all([image_id, instance_type, key_name]):
            flash('Los campos AMI, tipo de instancia y key pair son obligatorios.', 'error')
            return redirect(url_for('ec2.create_instance'))

        # Preparar configuración de red
        network_interfaces = []
        if vpc_id and subnet_id:
            network_interfaces = [{
                'DeviceIndex': 0,
                'SubnetId': subnet_id,
                'Groups': security_group_ids if security_group_ids else []
            }]

        # Crear instancia
        run_instances_params = {
            'ImageId': image_id,
            'MinCount': 1,
            'MaxCount': 1,
            'InstanceType': instance_type,
            'KeyName': key_name
        }

        if network_interfaces:
            run_instances_params['NetworkInterfaces'] = network_interfaces
        elif security_group_ids:
            run_instances_params['SecurityGroupIds'] = security_group_ids

        if user_data:
            run_instances_params['UserData'] = user_data

        response = ec2.run_instances(**run_instances_params)

        instance_id = response['Instances'][0]['InstanceId']

        # Agregar tag de nombre si se proporcionó
        if instance_name:
            ec2.create_tags(
                Resources=[instance_id],
                Tags=[{'Key': 'Name', 'Value': instance_name}]
            )

        flash(f'Instancia EC2 {instance_id} creada exitosamente.', 'success')
        return redirect(url_for('ec2.instances'))

    except Exception as e:
        flash(f'Error creando instancia EC2: {str(e)}', 'error')
        return redirect(url_for('ec2.create_instance'))

@bp.route('/ec2/launch-instance', methods=['POST'])
def launch_instance():
    """API endpoint para lanzar una nueva instancia EC2 desde el modal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
        
        ami_id = data.get('ami_id')
        instance_type = data.get('instance_type')
        key_name = data.get('key_name')
        security_group = data.get('security_group')
        user_data = data.get('user_data')
        assign_public_ip = data.get('assign_public_ip', True)
        
        if not ami_id or not instance_type:
            return jsonify({'success': False, 'error': 'AMI ID y Tipo de Instancia son requeridos'}), 400
        
        ec2 = get_aws_client('ec2')
        
        # Preparar parámetros para run_instances
        run_instances_params = {
            'ImageId': ami_id,
            'MinCount': 1,
            'MaxCount': 1,
            'InstanceType': instance_type
        }
        
        # Agregar KeyName si se proporcionó
        if key_name:
            run_instances_params['KeyName'] = key_name
        
        # Agregar SecurityGroup si se proporcionó
        if security_group:
            # Intentar determinar si es ID o nombre
            if security_group.startswith('sg-'):
                run_instances_params['SecurityGroupIds'] = [security_group]
            else:
                run_instances_params['SecurityGroups'] = [security_group]
        
        # Configurar IP pública
        if assign_public_ip:
            run_instances_params['NetworkInterfaces'] = [{
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': run_instances_params.pop('SecurityGroupIds', []) or None
            }]
            # Si usamos NetworkInterfaces, no podemos usar SecurityGroups
            if 'SecurityGroups' in run_instances_params:
                del run_instances_params['SecurityGroups']
        
        # Agregar UserData si se proporcionó
        if user_data:
            import base64
            run_instances_params['UserData'] = base64.b64encode(user_data.encode()).decode()
        
        # Lanzar la instancia
        response = ec2.run_instances(**run_instances_params)
        instance_id = response['Instances'][0]['InstanceId']
        
        logger.info(f'✅ Instancia EC2 {instance_id} lanzada exitosamente')
        
        return jsonify({
            'success': True, 
            'instance_id': instance_id,
            'message': f'Instancia {instance_id} lanzada exitosamente'
        })
        
    except Exception as e:
        logger.exception(f'❌ Error lanzando instancia EC2: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/ec2/key-pairs')
def key_pairs():
    """Página para gestionar key pairs"""
    try:
        ec2 = get_aws_client('ec2')
        response = ec2.describe_key_pairs()
        key_pairs_list = response.get('KeyPairs', [])
        return render_template('Computo/key_pairs.html', key_pairs=key_pairs_list)
    except Exception as e:
        flash(f'Error obteniendo key pairs: {str(e)}', 'error')
        return render_template('Computo/key_pairs.html', key_pairs=[])

@bp.route('/ec2/create-key-pair', methods=['POST'])
def create_key_pair():
    """Crear un nuevo key pair"""
    try:
        key_name = request.form.get('key_name')
        if not key_name:
            flash('El nombre del key pair es requerido', 'error')
            return redirect(url_for('ec2.key_pairs'))
        
        ec2 = get_aws_client('ec2')
        response = ec2.create_key_pair(KeyName=key_name)
        
        # Guardar el key material en un archivo si se solicita
        save_to_file = request.form.get('save_to_file')
        if save_to_file:
            try:
                # Crear directorio si no existe
                key_dir = os.path.join(os.getcwd(), 'keys')
                os.makedirs(key_dir, exist_ok=True)
                
                key_file = os.path.join(key_dir, f'{key_name}.pem')
                with open(key_file, 'w') as f:
                    f.write(response['KeyMaterial'])
                
                flash(f'Key pair "{key_name}" creado exitosamente. Archivo guardado en: {key_file}', 'success')
            except Exception as file_error:
                logger.warning(f'No se pudo guardar el archivo del key pair: {file_error}')
                flash(f'Key pair "{key_name}" creado exitosamente, pero no se pudo guardar el archivo. Key material: {response["KeyMaterial"][:50]}...', 'warning')
        else:
            flash(f'Key pair "{key_name}" creado exitosamente. Key material: {response["KeyMaterial"][:50]}...', 'success')
        
        return redirect(url_for('ec2.key_pairs'))
    except Exception as e:
        flash(f'Error creando key pair: {str(e)}', 'error')
        return redirect(url_for('ec2.key_pairs'))

@bp.route('/ec2/delete-key-pair/<key_name>', methods=['POST'])
def delete_key_pair(key_name):
    """Eliminar un key pair"""
    try:
        ec2 = get_aws_client('ec2')
        ec2.delete_key_pair(KeyName=key_name)
        flash(f'Key pair "{key_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando key pair: {str(e)}', 'error')
    return redirect(url_for('ec2.key_pairs'))

@bp.route('/ec2/instance-types')
def instance_types():
    """Página para ver tipos de instancia disponibles"""
    try:
        ec2 = get_aws_client('ec2')
        # Obtener tipos de instancia disponibles en la región
        response = ec2.describe_instance_types()
        instance_types_list = response.get('InstanceTypes', [])
        
        # Ordenar por familia y tamaño
        instance_types_list.sort(key=lambda x: (x['InstanceType'][:2], x['InstanceType']))
        
        return render_template('Computo/instance_types.html', instance_types=instance_types_list)
    except Exception as e:
        flash(f'Error obteniendo tipos de instancia: {str(e)}', 'error')
        return render_template('Computo/instance_types.html', instance_types=[])

@bp.route('/ec2/modify-instance/<instance_id>', methods=['GET', 'POST'])
def modify_instance(instance_id):
    """Modificar atributos de una instancia"""
    try:
        ec2 = get_aws_client('ec2')
        
        if request.method == 'POST':
            # Procesar la modificación
            action = request.form.get('action')
            
            if action == 'change_instance_type':
                new_instance_type = request.form.get('instance_type')
                if not new_instance_type:
                    flash('El tipo de instancia es requerido', 'error')
                    return redirect(url_for('ec2.modify_instance', instance_id=instance_id))
                
                # Detener la instancia si está corriendo
                instance_state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']
                was_running = instance_state == 'running'
                
                if was_running:
                    ec2.stop_instances(InstanceIds=[instance_id])
                    # Esperar a que se detenga
                    ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])
                
                # Cambiar el tipo de instancia
                ec2.modify_instance_attribute(
                    InstanceId=instance_id,
                    InstanceType={'Value': new_instance_type}
                )
                
                # Reiniciar si estaba corriendo
                if was_running:
                    ec2.start_instances(InstanceIds=[instance_id])
                
                flash(f'Tipo de instancia cambiado a {new_instance_type} exitosamente', 'success')
                return redirect(url_for('ec2.instances'))
            
            elif action == 'change_security_groups':
                security_group_ids = request.form.getlist('security_groups')
                ec2.modify_instance_attribute(
                    InstanceId=instance_id,
                    Groups=security_group_ids
                )
                flash('Grupos de seguridad actualizados exitosamente', 'success')
                return redirect(url_for('ec2.instances'))
        
        # GET: Mostrar formulario de modificación
        # Obtener detalles de la instancia
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        # Obtener security groups disponibles
        sg_response = ec2.describe_security_groups()
        security_groups = sg_response.get('SecurityGroups', [])
        
        return render_template('Computo/modify_instance.html', 
                             instance=instance, 
                             security_groups=security_groups)
                             
    except Exception as e:
        flash(f'Error modificando instancia: {str(e)}', 'error')
        return redirect(url_for('ec2.instances'))