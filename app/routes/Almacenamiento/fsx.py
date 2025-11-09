from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('fsx', __name__)

@bp.route('/fsx')
def index():
    """Página principal de FSx"""
    return render_template('Almacenamiento/fsx/index.html')

@bp.route('/fsx/file-systems')
def file_systems():
    """Lista todos los file systems FSx"""
    try:
        fsx = get_aws_client('fsx')
        response = fsx.describe_file_systems()
        file_systems_list = response['FileSystems']
    except Exception as e:
        flash(f'Error obteniendo file systems FSx: {str(e)}', 'error')
        file_systems_list = []

    return render_template('Almacenamiento/fsx/file_systems.html', file_systems=file_systems_list)

@bp.route('/fsx/file-system/<file_system_id>')
def file_system_detail(file_system_id):
    """Detalle de un file system FSx específico"""
    try:
        fsx = get_aws_client('fsx')
        response = fsx.describe_file_systems(FileSystemIds=[file_system_id])
        file_system = response['FileSystems'][0] if response['FileSystems'] else None
    except Exception as e:
        flash(f'Error obteniendo detalle del file system: {str(e)}', 'error')
        file_system = None

    return render_template('Almacenamiento/fsx/file_system_detail.html', file_system=file_system)

@bp.route('/fsx/file-systems/create', methods=['GET', 'POST'])
def create_file_system():
    """Crear un nuevo file system FSx"""
    if request.method == 'POST':
        try:
            fsx = get_aws_client('fsx')

            # Parámetros del formulario
            file_system_type = request.form.get('file_system_type', 'LUSTRE')
            storage_capacity = int(request.form.get('storage_capacity', 1200))
            subnet_ids = request.form.getlist('subnet_ids')
            security_group_ids = request.form.getlist('security_group_ids')

            # Crear el file system
            params = {
                'FileSystemType': file_system_type,
                'StorageCapacity': storage_capacity
            }

            if subnet_ids:
                params['SubnetIds'] = subnet_ids

            if security_group_ids:
                params['SecurityGroupIds'] = security_group_ids

            # Parámetros específicos por tipo
            if file_system_type == 'LUSTRE':
                deployment_type = request.form.get('deployment_type', 'PERSISTENT_1')
                per_unit_storage_throughput = int(request.form.get('per_unit_storage_throughput', 50))
                params['LustreConfiguration'] = {
                    'DeploymentType': deployment_type,
                    'PerUnitStorageThroughput': per_unit_storage_throughput
                }

            response = fsx.create_file_system(**params)
            file_system_id = response['FileSystem']['FileSystemId']

            flash(f'File system FSx {file_system_id} creado exitosamente', 'success')
            return redirect(url_for('fsx.file_system_detail', file_system_id=file_system_id))

        except Exception as e:
            flash(f'Error creando file system FSx: {str(e)}', 'error')

    # Obtener subnets y security groups disponibles para el formulario
    try:
        ec2 = get_aws_client('ec2')
        subnets_response = ec2.describe_subnets()
        subnets = subnets_response['Subnets']

        security_groups_response = ec2.describe_security_groups()
        security_groups = security_groups_response['SecurityGroups']
    except Exception:
        subnets = []
        security_groups = []

    return render_template('Almacenamiento/fsx/create_file_system.html',
                         subnets=subnets, security_groups=security_groups)

@bp.route('/fsx/file-system/<file_system_id>/delete', methods=['POST'])
def delete_file_system(file_system_id):
    """Eliminar un file system FSx"""
    try:
        fsx = get_aws_client('fsx')
        fsx.delete_file_system(FileSystemId=file_system_id)
        flash(f'File system FSx {file_system_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando file system FSx: {str(e)}', 'error')

    return redirect(url_for('fsx.file_systems'))