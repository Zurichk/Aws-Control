from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('autoscaling_bp', __name__)

@bp.route('/')
def index():
    return render_template('Gestion/index.html')

@bp.route('/groups')
def groups():
    try:
        autoscaling_client = get_aws_client('autoscaling')
        response = autoscaling_client.describe_auto_scaling_groups()
        groups = []
        for group in response['AutoScalingGroups']:
            groups.append({
                'name': group['AutoScalingGroupName'],
                'min_size': group['MinSize'],
                'max_size': group['MaxSize'],
                'desired_capacity': group['DesiredCapacity'],
                'instances': len(group.get('Instances', [])),
                'launch_template': group.get('LaunchTemplate', {}).get('LaunchTemplateName', 'N/A'),
                'availability_zones': group.get('AvailabilityZones', [])
            })
        return render_template('Gestion/autoscaling_service/groups.html', groups=groups)
    except Exception as e:
        flash(f'Error obteniendo grupos de Auto Scaling: {str(e)}', 'error')
        return render_template('Gestion/autoscaling_service/groups.html', groups=[])

@bp.route('/update-group/<group_name>', methods=['GET', 'POST'])
def update_group(group_name):
    """Actualizar un grupo de Auto Scaling"""
    if request.method == 'POST':
        try:
            min_size = int(request.form.get('min_size'))
            max_size = int(request.form.get('max_size'))
            desired_capacity = int(request.form.get('desired_capacity'))

            autoscaling_client = get_aws_client('autoscaling')
            autoscaling_client.update_auto_scaling_group(
                AutoScalingGroupName=group_name,
                MinSize=min_size,
                MaxSize=max_size,
                DesiredCapacity=desired_capacity
            )

            flash(f'Grupo de Auto Scaling "{group_name}" actualizado exitosamente', 'success')
            return redirect(url_for('autoscaling_bp.groups'))
        except Exception as e:
            flash(f'Error actualizando grupo de Auto Scaling: {str(e)}', 'error')

    # GET: mostrar formulario con valores actuales
    try:
        autoscaling_client = get_aws_client('autoscaling')
        response = autoscaling_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[group_name]
        )
        if not response['AutoScalingGroups']:
            flash(f'Grupo de Auto Scaling "{group_name}" no encontrado', 'error')
            return redirect(url_for('autoscaling_bp.groups'))

        group = response['AutoScalingGroups'][0]
        return render_template('Gestion/autoscaling_service/update_group.html',
                             group_name=group_name,
                             current_min=group['MinSize'],
                             current_max=group['MaxSize'],
                             current_desired=group['DesiredCapacity'])
    except Exception as e:
        flash(f'Error obteniendo grupo de Auto Scaling: {str(e)}', 'error')
        return redirect(url_for('autoscaling_bp.groups'))

@bp.route('/delete-group/<group_name>', methods=['POST'])
def delete_group(group_name):
    """Eliminar un grupo de Auto Scaling"""
    try:
        autoscaling_client = get_aws_client('autoscaling')
        autoscaling_client.delete_auto_scaling_group(
            AutoScalingGroupName=group_name,
            ForceDelete=True
        )
        flash(f'Grupo de Auto Scaling "{group_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando grupo de Auto Scaling: {str(e)}', 'error')

    return redirect(url_for('autoscaling_bp.groups'))

@bp.route('/policies')
def policies():
    try:
        autoscaling_client = get_aws_client('autoscaling')
        response = autoscaling_client.describe_policies()
        policies = []
        for policy in response['ScalingPolicies']:
            policies.append({
                'name': policy['PolicyName'],
                'group_name': policy['AutoScalingGroupName'],
                'policy_type': policy['PolicyType'],
                'adjustment_type': policy.get('AdjustmentType', 'N/A'),
                'scaling_adjustment': policy.get('ScalingAdjustment', 'N/A'),
                'cooldown': policy.get('Cooldown', 'N/A')
            })
        return render_template('Gestion/autoscaling_service/policies.html', policies=policies)
    except Exception as e:
        flash(f'Error obteniendo políticas de escalado: {str(e)}', 'error')
        return render_template('Gestion/autoscaling_service/policies.html', policies=[])

@bp.route('/create-policy', methods=['GET', 'POST'])
def create_policy():
    """Crear una nueva política de escalado"""
    if request.method == 'POST':
        try:
            policy_name = request.form.get('policy_name')
            group_name = request.form.get('group_name')
            policy_type = request.form.get('policy_type')
            adjustment_type = request.form.get('adjustment_type')
            scaling_adjustment = int(request.form.get('scaling_adjustment'))
            cooldown = int(request.form.get('cooldown', 300))

            autoscaling_client = get_aws_client('autoscaling')
            autoscaling_client.put_scaling_policy(
                AutoScalingGroupName=group_name,
                PolicyName=policy_name,
                PolicyType=policy_type,
                AdjustmentType=adjustment_type,
                ScalingAdjustment=scaling_adjustment,
                Cooldown=cooldown
            )

            flash(f'Política de escalado "{policy_name}" creada exitosamente', 'success')
            return redirect(url_for('autoscaling_bp.policies'))
        except Exception as e:
            flash(f'Error creando política de escalado: {str(e)}', 'error')

    # GET: mostrar formulario
    try:
        autoscaling_client = get_aws_client('autoscaling')
        response = autoscaling_client.describe_auto_scaling_groups()
        groups = [group['AutoScalingGroupName'] for group in response['AutoScalingGroups']]
        return render_template('Gestion/autoscaling_service/create_policy.html', groups=groups)
    except Exception as e:
        flash(f'Error obteniendo grupos de Auto Scaling: {str(e)}', 'error')
        return render_template('Gestion/autoscaling_service/create_policy.html', groups=[])

@bp.route('/delete-policy/<group_name>/<policy_name>', methods=['POST'])
def delete_policy(group_name, policy_name):
    """Eliminar una política de escalado"""
    try:
        autoscaling_client = get_aws_client('autoscaling')
        autoscaling_client.delete_policy(
            AutoScalingGroupName=group_name,
            PolicyName=policy_name
        )
        flash(f'Política de escalado "{policy_name}" eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando política de escalado: {str(e)}', 'error')

    return redirect(url_for('autoscaling_bp.policies'))

@bp.route('/create-group', methods=['GET', 'POST'])
def create_group():
    """Crear un nuevo grupo de Auto Scaling"""
    if request.method == 'POST':
        try:
            group_name = request.form.get('group_name')
            launch_template_id = request.form.get('launch_template_id')
            launch_template_name = request.form.get('launch_template_name')
            min_size = int(request.form.get('min_size', 1))
            max_size = int(request.form.get('max_size', 3))
            desired_capacity = int(request.form.get('desired_capacity', 1))
            availability_zones = request.form.getlist('availability_zones')

            autoscaling_client = get_aws_client('autoscaling')

            # Preparar parámetros del launch template
            launch_template = {}
            if launch_template_id:
                launch_template['LaunchTemplateId'] = launch_template_id
            elif launch_template_name:
                launch_template['LaunchTemplateName'] = launch_template_name

            # Crear el grupo de Auto Scaling
            autoscaling_client.create_auto_scaling_group(
                AutoScalingGroupName=group_name,
                LaunchTemplate=launch_template,
                MinSize=min_size,
                MaxSize=max_size,
                DesiredCapacity=desired_capacity,
                AvailabilityZones=availability_zones
            )

            flash(f'Grupo de Auto Scaling "{group_name}" creado exitosamente', 'success')
            return redirect(url_for('autoscaling_bp.groups'))

        except Exception as e:
            flash(f'Error creando grupo de Auto Scaling: {str(e)}', 'error')

    # GET request - mostrar formulario
    try:
        ec2_client = get_aws_client('ec2')

        # Obtener launch templates disponibles
        launch_templates_response = ec2_client.describe_launch_templates()
        launch_templates = launch_templates_response.get('LaunchTemplates', [])

        # Obtener availability zones
        az_response = ec2_client.describe_availability_zones()
        availability_zones = [az['ZoneName'] for az in az_response.get('AvailabilityZones', [])]

        return render_template('Gestion/autoscaling_service/create_group.html',
                             launch_templates=launch_templates,
                             availability_zones=availability_zones)

    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Gestion/autoscaling_service/create_group.html',
                             launch_templates=[],
                             availability_zones=[])