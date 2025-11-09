from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import boto3
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('security_groups', __name__)

@bp.route('/security-groups')
def index():
    """Página principal de Security Groups"""
    return render_template('Seguridad/security_groups/index.html')

@bp.route('/security-groups/list')
def list_security_groups():
    """Listar todos los security groups"""
    try:
        ec2 = get_aws_client('ec2')
        response = ec2.describe_security_groups()

        security_groups = []
        for sg in response.get('SecurityGroups', []):
            security_groups.append({
                'id': sg['GroupId'],
                'name': sg.get('GroupName', 'N/A'),
                'description': sg.get('GroupDescription', 'N/A'),
                'vpc_id': sg.get('VpcId', 'N/A'),
                'owner_id': sg.get('OwnerId', 'N/A'),
                'ingress_rules': len(sg.get('IpPermissions', [])),
                'egress_rules': len(sg.get('IpPermissionsEgress', [])),
                'tags': sg.get('Tags', [])
            })

        return render_template('Seguridad/security_groups/list.html',
                             security_groups=security_groups)

    except Exception as e:
        flash(f'Error obteniendo security groups: {str(e)}', 'error')
        return render_template('Seguridad/security_groups/list.html',
                             security_groups=[])

@bp.route('/security-groups/delete/<group_id>', methods=['POST'])
def delete_security_group(group_id):
    """Eliminar un security group"""
    try:
        ec2 = get_aws_client('ec2')

        # Verificar que el security group existe
        response = ec2.describe_security_groups(GroupIds=[group_id])
        sg = response['SecurityGroups'][0]

        # Eliminar el security group
        ec2.delete_security_group(GroupId=group_id)

        flash(f'Security Group {sg.get("GroupName", group_id)} eliminado exitosamente', 'success')
        return redirect(url_for('security_groups.list_security_groups'))

    except Exception as e:
        flash(f'Error eliminando security group: {str(e)}', 'error')
        return redirect(url_for('security_groups.list_security_groups'))

@bp.route('/security-groups/<group_id>/authorize-ingress', methods=['GET', 'POST'])
def authorize_ingress(group_id):
    """Autorizar reglas de entrada (ingress)"""
    try:
        ec2 = get_aws_client('ec2')

        if request.method == 'POST':
            # Obtener datos del formulario
            rule_type = request.form.get('rule_type')
            protocol = request.form.get('protocol')
            port_range_from = request.form.get('port_range_from')
            port_range_to = request.form.get('port_range_to')
            source_type = request.form.get('source_type')
            source_value = request.form.get('source_value')

            # Construir la regla de entrada
            ip_permissions = [{
                'IpProtocol': protocol,
                'FromPort': int(port_range_from) if port_range_from else None,
                'ToPort': int(port_range_to) if port_range_to else None,
            }]

            # Agregar fuente (CIDR o security group)
            if source_type == 'cidr':
                ip_permissions[0]['IpRanges'] = [{'CidrIp': source_value}]
            elif source_type == 'security_group':
                ip_permissions[0]['UserIdGroupPairs'] = [{
                    'GroupId': source_value,
                    'Description': request.form.get('description', '')
                }]

            # Autorizar la regla
            ec2.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )

            flash('Regla de entrada autorizada exitosamente', 'success')
            return redirect(url_for('security_groups.list_security_groups'))

        # GET: Mostrar formulario
        # Obtener detalles del security group
        response = ec2.describe_security_groups(GroupIds=[group_id])
        security_group = response['SecurityGroups'][0]

        # Obtener otros security groups para referencias
        all_sgs_response = ec2.describe_security_groups()
        other_security_groups = [
            sg for sg in all_sgs_response.get('SecurityGroups', [])
            if sg['GroupId'] != group_id
        ]

        return render_template('Seguridad/security_groups/authorize_ingress.html',
                             security_group=security_group,
                             other_security_groups=other_security_groups)

    except Exception as e:
        flash(f'Error autorizando regla de entrada: {str(e)}', 'error')
        return redirect(url_for('security_groups.list_security_groups'))

@bp.route('/security-groups/<group_id>/revoke-ingress', methods=['GET', 'POST'])
def revoke_ingress(group_id):
    """Revocar reglas de entrada (ingress)"""
    try:
        ec2 = get_aws_client('ec2')

        if request.method == 'POST':
            # Obtener datos del formulario
            rule_index = int(request.form.get('rule_index'))

            # Obtener reglas actuales del security group
            response = ec2.describe_security_groups(GroupIds=[group_id])
            security_group = response['SecurityGroups'][0]
            ingress_rules = security_group.get('IpPermissions', [])

            if 0 <= rule_index < len(ingress_rules):
                # Revocar la regla específica
                ec2.revoke_security_group_ingress(
                    GroupId=group_id,
                    IpPermissions=[ingress_rules[rule_index]]
                )

                flash('Regla de entrada revocada exitosamente', 'success')
            else:
                flash('Índice de regla inválido', 'error')

            return redirect(url_for('security_groups.list_security_groups'))

        # GET: Mostrar formulario con reglas existentes
        # Obtener detalles del security group
        response = ec2.describe_security_groups(GroupIds=[group_id])
        security_group = response['SecurityGroups'][0]

        return render_template('Seguridad/security_groups/revoke_ingress.html',
                             security_group=security_group)

    except Exception as e:
        flash(f'Error revocando regla de entrada: {str(e)}', 'error')
        return redirect(url_for('security_groups.list_security_groups'))

@bp.route('/security-groups/<group_id>/authorize-egress', methods=['GET', 'POST'])
def authorize_egress(group_id):
    """Autorizar reglas de salida (egress)"""
    try:
        ec2 = get_aws_client('ec2')

        if request.method == 'POST':
            # Obtener datos del formulario
            rule_type = request.form.get('rule_type')
            protocol = request.form.get('protocol')
            port_range_from = request.form.get('port_range_from')
            port_range_to = request.form.get('port_range_to')
            destination_type = request.form.get('destination_type')
            destination_value = request.form.get('destination_value')

            # Construir la regla de salida
            ip_permissions = [{
                'IpProtocol': protocol,
                'FromPort': int(port_range_from) if port_range_from else None,
                'ToPort': int(port_range_to) if port_range_to else None,
            }]

            # Agregar destino (CIDR o security group)
            if destination_type == 'cidr':
                ip_permissions[0]['IpRanges'] = [{'CidrIp': destination_value}]
            elif destination_type == 'security_group':
                ip_permissions[0]['UserIdGroupPairs'] = [{
                    'GroupId': destination_value,
                    'Description': request.form.get('description', '')
                }]

            # Autorizar la regla
            ec2.authorize_security_group_egress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )

            flash('Regla de salida autorizada exitosamente', 'success')
            return redirect(url_for('security_groups.list_security_groups'))

        # GET: Mostrar formulario
        # Obtener detalles del security group
        response = ec2.describe_security_groups(GroupIds=[group_id])
        security_group = response['SecurityGroups'][0]

        # Obtener otros security groups para referencias
        all_sgs_response = ec2.describe_security_groups()
        other_security_groups = [
            sg for sg in all_sgs_response.get('SecurityGroups', [])
            if sg['GroupId'] != group_id
        ]

        return render_template('Seguridad/security_groups/authorize_egress.html',
                             security_group=security_group,
                             other_security_groups=other_security_groups)

    except Exception as e:
        flash(f'Error autorizando regla de salida: {str(e)}', 'error')
        return redirect(url_for('security_groups.list_security_groups'))

@bp.route('/security-groups/<group_id>/revoke-egress', methods=['GET', 'POST'])
def revoke_egress(group_id):
    """Revocar reglas de salida (egress)"""
    try:
        ec2 = get_aws_client('ec2')

        if request.method == 'POST':
            # Obtener datos del formulario
            rule_index = int(request.form.get('rule_index'))

            # Obtener reglas actuales del security group
            response = ec2.describe_security_groups(GroupIds=[group_id])
            security_group = response['SecurityGroups'][0]
            egress_rules = security_group.get('IpPermissionsEgress', [])

            if 0 <= rule_index < len(egress_rules):
                # Revocar la regla específica
                ec2.revoke_security_group_egress(
                    GroupId=group_id,
                    IpPermissions=[egress_rules[rule_index]]
                )

                flash('Regla de salida revocada exitosamente', 'success')
            else:
                flash('Índice de regla inválido', 'error')

            return redirect(url_for('security_groups.list_security_groups'))

        # GET: Mostrar formulario con reglas existentes
        # Obtener detalles del security group
        response = ec2.describe_security_groups(GroupIds=[group_id])
        security_group = response['SecurityGroups'][0]

        return render_template('Seguridad/security_groups/revoke_egress.html',
                             security_group=security_group)

    except Exception as e:
        flash(f'Error revocando regla de salida: {str(e)}', 'error')
        return redirect(url_for('security_groups.list_security_groups'))