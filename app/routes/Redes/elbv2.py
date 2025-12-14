from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('elbv2', __name__)

@bp.route('/')
def index():
    return render_template('Redes/elbv2/index.html')

@bp.route('/load-balancers')
def load_balancers():
    try:
        elbv2 = get_aws_client('elbv2')
        lbs = elbv2.describe_load_balancers()
        lb_list = []
        for lb in lbs['LoadBalancers']:
            lb_list.append({
                'name': lb['LoadBalancerName'],
                'arn': lb['LoadBalancerArn'],
                'dns_name': lb['DNSName'],
                'state': lb['State']['Code'],
                'type': lb['Type']
            })
        return render_template('Redes/elbv2/load_balancers.html', load_balancers=lb_list)
    except Exception as e:
        flash(f'Error obteniendo load balancers: {str(e)}', 'error')
        return render_template('Redes/elbv2/load_balancers.html', load_balancers=[])

@bp.route('/create-load-balancer', methods=['GET', 'POST'])
def create_load_balancer():
    if request.method == 'POST':
        try:
            elbv2 = get_aws_client('elbv2')
            ec2 = get_aws_client('ec2')

            # Obtener datos del formulario
            name = request.form.get('name')
            subnets = request.form.getlist('subnets')
            security_groups = request.form.getlist('security_groups')
            scheme = request.form.get('scheme', 'internet-facing')
            lb_type = request.form.get('type', 'application')

            # Crear load balancer
            response = elbv2.create_load_balancer(
                Name=name,
                Subnets=subnets,
                SecurityGroups=security_groups,
                Scheme=scheme,
                Type=lb_type
            )

            flash(f'Load Balancer creado exitosamente: {response["LoadBalancers"][0]["LoadBalancerArn"]}', 'success')
            return redirect(url_for('elbv2.load_balancers'))

        except Exception as e:
            flash(f'Error creando load balancer: {str(e)}', 'error')
            return redirect(url_for('elbv2.create_load_balancer'))

    # GET request - mostrar formulario
    try:
        ec2 = get_aws_client('ec2')
        # Obtener subnets disponibles
        subnets_response = ec2.describe_subnets()
        subnets = [{'id': s['SubnetId'], 'cidr': s['CidrBlock'], 'az': s['AvailabilityZone']} for s in subnets_response['Subnets']]

        # Obtener security groups disponibles
        sg_response = ec2.describe_security_groups()
        security_groups = [{'id': sg['GroupId'], 'name': sg['GroupName']} for sg in sg_response['SecurityGroups']]

        return render_template('Redes/elbv2/create_load_balancer.html', subnets=subnets, security_groups=security_groups)
    except Exception as e:
        flash(f'Error obteniendo datos para el formulario: {str(e)}', 'error')
        return render_template('Redes/elbv2/create_load_balancer.html', subnets=[], security_groups=[])

@bp.route('/delete-load-balancer/<load_balancer_arn>', methods=['POST'])
def delete_load_balancer(load_balancer_arn):
    try:
        elbv2 = get_aws_client('elbv2')
        elbv2.delete_load_balancer(LoadBalancerArn=load_balancer_arn)
        flash('Load Balancer eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando load balancer: {str(e)}', 'error')
    return redirect(url_for('elbv2.load_balancers'))

@bp.route('/target-groups')
def target_groups():
    try:
        elbv2 = get_aws_client('elbv2')
        tgs = elbv2.describe_target_groups()
        tg_list = []
        for tg in tgs['TargetGroups']:
            tg_list.append({
                'name': tg['TargetGroupName'],
                'arn': tg['TargetGroupArn'],
                'protocol': tg['Protocol'],
                'port': tg['Port'],
                'vpc_id': tg['VpcId'],
                'health_check_path': tg.get('HealthCheckPath', '/')
            })
        return render_template('Redes/elbv2/target_groups.html', target_groups=tg_list)
    except Exception as e:
        flash(f'Error obteniendo target groups: {str(e)}', 'error')
        return render_template('Redes/elbv2/target_groups.html', target_groups=[])

@bp.route('/create-target-group', methods=['GET', 'POST'])
def create_target_group():
    if request.method == 'POST':
        try:
            elbv2 = get_aws_client('elbv2')

            # Obtener datos del formulario
            name = request.form.get('name')
            protocol = request.form.get('protocol', 'HTTP')
            port = int(request.form.get('port', '80'))
            vpc_id = request.form.get('vpc_id')
            health_check_path = request.form.get('health_check_path', '/')

            # Crear target group
            response = elbv2.create_target_group(
                Name=name,
                Protocol=protocol,
                Port=port,
                VpcId=vpc_id,
                HealthCheckPath=health_check_path
            )

            flash(f'Target Group creado exitosamente: {response["TargetGroups"][0]["TargetGroupArn"]}', 'success')
            return redirect(url_for('elbv2.target_groups'))

        except Exception as e:
            flash(f'Error creando target group: {str(e)}', 'error')
            return redirect(url_for('elbv2.create_target_group'))

    # GET request - mostrar formulario
    try:
        ec2 = get_aws_client('ec2')
        # Obtener VPCs disponibles
        vpcs_response = ec2.describe_vpcs()
        vpcs = [{'id': vpc['VpcId'], 'cidr': vpc['CidrBlock']} for vpc in vpcs_response['Vpcs']]

        return render_template('Redes/elbv2/create_target_group.html', vpcs=vpcs)
    except Exception as e:
        flash(f'Error obteniendo datos para el formulario: {str(e)}', 'error')
        return render_template('Redes/elbv2/create_target_group.html', vpcs=[])

@bp.route('/delete-target-group/<target_group_arn>', methods=['POST'])
def delete_target_group(target_group_arn):
    try:
        elbv2 = get_aws_client('elbv2')
        elbv2.delete_target_group(TargetGroupArn=target_group_arn)
        flash('Target Group eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando target group: {str(e)}', 'error')
    return redirect(url_for('elbv2.target_groups'))