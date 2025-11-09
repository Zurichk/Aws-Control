from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('efs', __name__)

@bp.route('/efs')
def index():
    """Página principal de EFS"""
    return render_template('Almacenamiento/efs/index.html')

@bp.route('/efs/file-systems')
def file_systems():
    """Lista todos los file systems EFS"""
    try:
        efs = get_aws_client('efs')
        response = efs.describe_file_systems()
        file_systems_list = response['FileSystems']
    except Exception as e:
        flash(f'Error obteniendo file systems EFS: {str(e)}', 'error')
        file_systems_list = []

    return render_template('Almacenamiento/efs/file_systems.html', file_systems=file_systems_list)

@bp.route('/efs/file-system/<file_system_id>')
def file_system_detail(file_system_id):
    """Detalle de un file system EFS específico"""
    try:
        efs = get_aws_client('efs')
        response = efs.describe_file_systems(FileSystemId=file_system_id)
        file_system = response['FileSystems'][0] if response['FileSystems'] else None

        # Obtener mount targets
        if file_system:
            mount_targets_response = efs.describe_mount_targets(FileSystemId=file_system_id)
            mount_targets = mount_targets_response['MountTargets']
        else:
            mount_targets = []
    except Exception as e:
        flash(f'Error obteniendo detalle del file system: {str(e)}', 'error')
        file_system = None
        mount_targets = []

    return render_template('Almacenamiento/efs/file_system_detail.html',
                         file_system=file_system, mount_targets=mount_targets)

@bp.route('/efs/file-systems/create', methods=['GET', 'POST'])
def create_file_system():
    """Crear un nuevo file system EFS"""
    if request.method == 'POST':
        try:
            efs = get_aws_client('efs')

            # Parámetros del formulario
            creation_token = request.form.get('creation_token')
            performance_mode = request.form.get('performance_mode', 'generalPurpose')
            throughput_mode = request.form.get('throughput_mode', 'bursting')
            provisioned_throughput = request.form.get('provisioned_throughput')

            # Crear el file system
            params = {
                'CreationToken': creation_token,
                'PerformanceMode': performance_mode,
                'ThroughputMode': throughput_mode
            }

            if throughput_mode == 'provisioned' and provisioned_throughput:
                params['ProvisionedThroughputInMibps'] = float(provisioned_throughput)

            response = efs.create_file_system(**params)
            file_system_id = response['FileSystemId']

            flash(f'File system EFS {file_system_id} creado exitosamente', 'success')
            return redirect(url_for('efs.file_system_detail', file_system_id=file_system_id))

        except Exception as e:
            flash(f'Error creando file system EFS: {str(e)}', 'error')

    return render_template('Almacenamiento/efs/create_file_system.html')

@bp.route('/efs/file-system/<file_system_id>/delete', methods=['POST'])
def delete_file_system(file_system_id):
    """Eliminar un file system EFS"""
    try:
        efs = get_aws_client('efs')
        efs.delete_file_system(FileSystemId=file_system_id)
        flash(f'File system EFS {file_system_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando file system EFS: {str(e)}', 'error')

    return redirect(url_for('efs.file_systems'))

@bp.route('/efs/file-system/<file_system_id>/create-mount-target', methods=['GET', 'POST'])
def create_mount_target(file_system_id):
    """Crear un mount target para un file system EFS"""
    if request.method == 'POST':
        try:
            efs = get_aws_client('efs')

            # Parámetros del formulario
            subnet_id = request.form.get('subnet_id')
            security_groups = request.form.getlist('security_groups')
            ip_address = request.form.get('ip_address')

            # Crear el mount target
            params = {
                'FileSystemId': file_system_id,
                'SubnetId': subnet_id
            }

            if security_groups:
                params['SecurityGroups'] = security_groups

            if ip_address:
                params['IpAddress'] = ip_address

            response = efs.create_mount_target(**params)
            mount_target_id = response['MountTargetId']

            flash(f'Mount target {mount_target_id} creado exitosamente', 'success')
            return redirect(url_for('efs.file_system_detail', file_system_id=file_system_id))

        except Exception as e:
            flash(f'Error creando mount target: {str(e)}', 'error')

    # Obtener subnets disponibles para el formulario
    try:
        ec2 = get_aws_client('ec2')
        subnets_response = ec2.describe_subnets()
        subnets = subnets_response['Subnets']

        # Obtener security groups
        security_groups_response = ec2.describe_security_groups()
        security_groups = security_groups_response['SecurityGroups']
    except Exception:
        subnets = []
        security_groups = []

    return render_template('Almacenamiento/efs/create_mount_target.html',
                         file_system_id=file_system_id, subnets=subnets, security_groups=security_groups)

@bp.route('/efs/mount-target/<mount_target_id>/delete', methods=['POST'])
def delete_mount_target(mount_target_id):
    """Eliminar un mount target EFS"""
    file_system_id = request.form.get('file_system_id')
    try:
        efs = get_aws_client('efs')
        efs.delete_mount_target(MountTargetId=mount_target_id)
        flash(f'Mount target {mount_target_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando mount target: {str(e)}', 'error')

    return redirect(url_for('efs.file_system_detail', file_system_id=file_system_id))