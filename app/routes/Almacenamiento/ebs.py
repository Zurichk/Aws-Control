from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('ebs', __name__)

@bp.route('/')
def index():
    """Página principal de EBS"""
    return render_template('Almacenamiento/ebs/index.html')

@bp.route('/volumes')
def volumes():
    """Lista todos los volúmenes EBS"""
    try:
        ec2 = get_aws_client('ec2')
        response = ec2.describe_volumes()
        volumes_list = response['Volumes']
    except Exception as e:
        flash(f'Error obteniendo volúmenes EBS: {str(e)}', 'error')
        volumes_list = []

    return render_template('Almacenamiento/ebs/volumes.html', volumes=volumes_list)

@bp.route('/volume/<volume_id>')
def volume_detail(volume_id):
    """Detalle de un volumen EBS específico"""
    try:
        ec2 = get_aws_client('ec2')
        response = ec2.describe_volumes(VolumeIds=[volume_id])
        volume = response['Volumes'][0] if response['Volumes'] else None

        # Obtener snapshots de este volumen
        if volume:
            snapshots_response = ec2.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [volume_id]}])
            snapshots = snapshots_response['Snapshots']
        else:
            snapshots = []
    except Exception as e:
        flash(f'Error obteniendo detalle del volumen: {str(e)}', 'error')
        volume = None
        snapshots = []

    return render_template('Almacenamiento/ebs/volume_detail.html', volume=volume, snapshots=snapshots)

@bp.route('/volumes/create', methods=['GET', 'POST'])
def create_volume():
    """Crear un nuevo volumen EBS"""
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')

            # Parámetros del formulario
            availability_zone = request.form.get('availability_zone')
            size = int(request.form.get('size'))
            volume_type = request.form.get('volume_type', 'gp3')
            iops = request.form.get('iops')
            throughput = request.form.get('throughput')

            # Crear el volumen
            params = {
                'AvailabilityZone': availability_zone,
                'Size': size,
                'VolumeType': volume_type
            }

            if iops and volume_type in ['io1', 'io2', 'gp3']:
                params['Iops'] = int(iops)

            if throughput and volume_type == 'gp3':
                params['Throughput'] = int(throughput)

            response = ec2.create_volume(**params)

            flash(f'Volumen EBS {response["VolumeId"]} creado exitosamente', 'success')
            return redirect(url_for('ebs.volumes'))

        except Exception as e:
            flash(f'Error creando volumen EBS: {str(e)}', 'error')

    # GET: mostrar formulario
    try:
        ec2 = get_aws_client('ec2')
        zones_response = ec2.describe_availability_zones()
        availability_zones = [zone['ZoneName'] for zone in zones_response['AvailabilityZones']]
    except Exception:
        availability_zones = []

    return render_template('Almacenamiento/ebs/create_volume.html', availability_zones=availability_zones)

@bp.route('/volume/<volume_id>/delete', methods=['POST'])
def delete_volume(volume_id):
    """Eliminar un volumen EBS"""
    try:
        ec2 = get_aws_client('ec2')
        ec2.delete_volume(VolumeId=volume_id)
        flash(f'Volumen EBS {volume_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando volumen EBS: {str(e)}', 'error')

    return redirect(url_for('ebs.volumes'))

@bp.route('/volume/<volume_id>/attach', methods=['GET', 'POST'])
def attach_volume(volume_id):
    """Adjuntar un volumen EBS a una instancia"""
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')

            instance_id = request.form.get('instance_id')
            device = request.form.get('device')

            ec2.attach_volume(
                VolumeId=volume_id,
                InstanceId=instance_id,
                Device=device
            )

            flash(f'Volumen EBS {volume_id} adjuntado exitosamente a instancia {instance_id}', 'success')
            return redirect(url_for('ebs.volume_detail', volume_id=volume_id))

        except Exception as e:
            flash(f'Error adjuntando volumen EBS: {str(e)}', 'error')

    # GET: mostrar formulario
    try:
        ec2 = get_aws_client('ec2')
        instances_response = ec2.describe_instances()
        instances = []
        for reservation in instances_response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'AvailabilityZone': instance['Placement']['AvailabilityZone']
                })
    except Exception:
        instances = []

    return render_template('Almacenamiento/ebs/attach_volume.html', volume_id=volume_id, instances=instances)

@bp.route('/volume/<volume_id>/detach', methods=['POST'])
def detach_volume(volume_id):
    """Desadjuntar un volumen EBS de una instancia"""
    try:
        ec2 = get_aws_client('ec2')
        ec2.detach_volume(VolumeId=volume_id)
        flash(f'Volumen EBS {volume_id} desadjuntado exitosamente', 'success')
    except Exception as e:
        flash(f'Error desadjuntando volumen EBS: {str(e)}', 'error')

    return redirect(url_for('ebs.volume_detail', volume_id=volume_id))

@bp.route('/snapshots')
def snapshots():
    """Lista todos los snapshots EBS"""
    try:
        ec2 = get_aws_client('ec2')
        response = ec2.describe_snapshots(OwnerIds=['self'])
        snapshots_list = response['Snapshots']
    except Exception as e:
        flash(f'Error obteniendo snapshots EBS: {str(e)}', 'error')
        snapshots_list = []

    return render_template('Almacenamiento/ebs/snapshots.html', snapshots=snapshots_list)

@bp.route('/snapshots/create', methods=['GET', 'POST'])
def create_snapshot():
    """Crear un snapshot de un volumen EBS"""
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')

            volume_id = request.form.get('volume_id')
            description = request.form.get('description', '')

            params = {'VolumeId': volume_id}
            if description:
                params['Description'] = description

            response = ec2.create_snapshot(**params)

            flash(f'Snapshot EBS {response["SnapshotId"]} creado exitosamente', 'success')
            return redirect(url_for('ebs.snapshots'))

        except Exception as e:
            flash(f'Error creando snapshot EBS: {str(e)}', 'error')

    # GET: mostrar formulario
    try:
        ec2 = get_aws_client('ec2')
        volumes_response = ec2.describe_volumes()
        volumes = volumes_response['Volumes']
    except Exception:
        volumes = []

    return render_template('Almacenamiento/ebs/create_snapshot.html', volumes=volumes)

@bp.route('/snapshot/<snapshot_id>/delete', methods=['POST'])
def delete_snapshot(snapshot_id):
    """Eliminar un snapshot EBS"""
    try:
        ec2 = get_aws_client('ec2')
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        flash(f'Snapshot EBS {snapshot_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando snapshot EBS: {str(e)}', 'error')

    return redirect(url_for('ebs.snapshots'))