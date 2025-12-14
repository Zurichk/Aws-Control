from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('route53', __name__)

@bp.route('/')
def index():
    return render_template('Redes/route53/index.html')

@bp.route('/hosted-zones')
def hosted_zones():
    try:
        r53 = get_aws_client('route53')
        zones = r53.list_hosted_zones()
        zone_list = []
        for zone in zones['HostedZones']:
            zone_list.append({
                'id': zone['Id'],
                'name': zone['Name'],
                'private': zone['Config']['PrivateZone']
            })
        return render_template('Redes/route53/hosted_zones.html', zones=zone_list)
    except Exception as e:
        flash(f'Error obteniendo zonas hospedadas de Route 53: {str(e)}', 'error')
        return render_template('Redes/route53/hosted_zones.html', zones=[])

@bp.route('/create-hosted-zone', methods=['GET', 'POST'])
def create_hosted_zone():
    """Crear una nueva zona hospedada"""
    try:
        r53 = get_aws_client('route53')

        if request.method == 'POST':
            # Obtener datos del formulario
            domain_name = request.form.get('domain_name')
            comment = request.form.get('comment', '')
            private_zone = request.form.get('private_zone') == 'on'
            vpc_id = request.form.get('vpc_id') if private_zone else None

            # Crear la zona hospedada
            params = {
                'Name': domain_name,
                'CallerReference': str(hash(domain_name + str(request.form.get('caller_reference', '')))),
                'HostedZoneConfig': {
                    'Comment': comment,
                    'PrivateZone': private_zone
                }
            }

            if private_zone and vpc_id:
                params['VPCs'] = [{
                    'VPCRegion': request.form.get('vpc_region', 'us-east-1'),
                    'VPCId': vpc_id
                }]

            response = r53.create_hosted_zone(**params)

            flash(f'Zona hospedada {domain_name} creada exitosamente', 'success')
            return redirect(url_for('route53.hosted_zones'))

        # GET: Mostrar formulario
        # Obtener VPCs disponibles para zonas privadas
        ec2 = get_aws_client('ec2')
        vpcs_response = ec2.describe_vpcs()
        vpcs = vpcs_response.get('Vpcs', [])

        return render_template('Redes/route53/create_hosted_zone.html', vpcs=vpcs)

    except Exception as e:
        flash(f'Error creando zona hospedada: {str(e)}', 'error')
        return redirect(url_for('route53.hosted_zones'))

@bp.route('/delete-hosted-zone/<zone_id>', methods=['POST'])
def delete_hosted_zone(zone_id):
    """Eliminar una zona hospedada"""
    try:
        r53 = get_aws_client('route53')

        # Verificar que la zona existe
        zones = r53.list_hosted_zones()
        zone = next((z for z in zones['HostedZones'] if z['Id'] == zone_id), None)

        if not zone:
            flash('Zona hospedada no encontrada', 'error')
            return redirect(url_for('route53.hosted_zones'))

        # Eliminar la zona hospedada
        r53.delete_hosted_zone(Id=zone_id)

        flash(f'Zona hospedada {zone["Name"]} eliminada exitosamente', 'success')
        return redirect(url_for('route53.hosted_zones'))

    except Exception as e:
        flash(f'Error eliminando zona hospedada: {str(e)}', 'error')
        return redirect(url_for('route53.hosted_zones'))

@bp.route('/zone/<zone_id>/records')
def list_resource_record_sets(zone_id):
    """Listar registros de una zona hospedada"""
    try:
        r53 = get_aws_client('route53')

        # Obtener información de la zona
        zones = r53.list_hosted_zones()
        zone = next((z for z in zones['HostedZones'] if z['Id'] == zone_id), None)

        if not zone:
            flash('Zona hospedada no encontrada', 'error')
            return redirect(url_for('route53.hosted_zones'))

        # Obtener registros
        records = r53.list_resource_record_sets(HostedZoneId=zone_id)

        record_list = []
        for record in records.get('ResourceRecordSets', []):
            record_list.append({
                'name': record['Name'],
                'type': record['Type'],
                'ttl': record.get('TTL'),
                'value': record.get('ResourceRecords', [{}])[0].get('Value', '') if record.get('ResourceRecords') else '',
                'alias_target': record.get('AliasTarget', {}),
                'set_identifier': record.get('SetIdentifier')
            })

        return render_template('Redes/route53/records.html',
                             zone=zone,
                             records=record_list)

    except Exception as e:
        flash(f'Error obteniendo registros: {str(e)}', 'error')
        return redirect(url_for('route53.hosted_zones'))

@bp.route('/zone/<zone_id>/create-record', methods=['GET', 'POST'])
def create_record(zone_id):
    """Crear un nuevo registro DNS"""
    try:
        r53 = get_aws_client('route53')

        # Obtener información de la zona
        zones = r53.list_hosted_zones()
        zone = next((z for z in zones['HostedZones'] if z['Id'] == zone_id), None)

        if not zone:
            flash('Zona hospedada no encontrada', 'error')
            return redirect(url_for('route53.hosted_zones'))

        if request.method == 'POST':
            # Obtener datos del formulario
            name = request.form.get('name')
            record_type = request.form.get('record_type')
            value = request.form.get('value')
            ttl = int(request.form.get('ttl', 300))

            # Crear el registro
            change_batch = {
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [{'Value': value}]
                    }
                }]
            }

            r53.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=change_batch
            )

            flash(f'Registro {name} ({record_type}) creado exitosamente', 'success')
            return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

        # GET: Mostrar formulario
        return render_template('Redes/route53/create_record.html', zone=zone)

    except Exception as e:
        flash(f'Error creando registro: {str(e)}', 'error')
        return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

@bp.route('/zone/<zone_id>/delete-record', methods=['POST'])
def delete_record(zone_id):
    """Eliminar un registro DNS"""
    try:
        r53 = get_aws_client('route53')

        # Obtener datos del formulario
        name = request.form.get('name')
        record_type = request.form.get('record_type')
        value = request.form.get('value')
        ttl = int(request.form.get('ttl', 300))

        # Eliminar el registro
        change_batch = {
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': name,
                    'Type': record_type,
                    'TTL': ttl,
                    'ResourceRecords': [{'Value': value}]
                }
            }]
        }

        r53.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=change_batch
        )

        flash(f'Registro {name} ({record_type}) eliminado exitosamente', 'success')
        return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

    except Exception as e:
        flash(f'Error eliminando registro: {str(e)}', 'error')
        return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

@bp.route('/zone/<zone_id>/update-record', methods=['GET', 'POST'])
def update_record(zone_id):
    """Actualizar un registro DNS existente"""
    try:
        r53 = get_aws_client('route53')

        # Obtener información de la zona
        zones = r53.list_hosted_zones()
        zone = next((z for z in zones['HostedZones'] if z['Id'] == zone_id), None)

        if not zone:
            flash('Zona hospedada no encontrada', 'error')
            return redirect(url_for('route53.hosted_zones'))

        if request.method == 'POST':
            # Obtener datos del formulario
            old_name = request.form.get('old_name')
            old_type = request.form.get('old_type')
            old_value = request.form.get('old_value')
            old_ttl = int(request.form.get('old_ttl', 300))

            new_name = request.form.get('new_name')
            new_type = request.form.get('new_type')
            new_value = request.form.get('new_value')
            new_ttl = int(request.form.get('new_ttl', 300))

            # Actualizar el registro (DELETE + CREATE)
            change_batch = {
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': old_name,
                            'Type': old_type,
                            'TTL': old_ttl,
                            'ResourceRecords': [{'Value': old_value}]
                        }
                    },
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': new_name,
                            'Type': new_type,
                            'TTL': new_ttl,
                            'ResourceRecords': [{'Value': new_value}]
                        }
                    }
                ]
            }

            r53.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=change_batch
            )

            flash(f'Registro {new_name} ({new_type}) actualizado exitosamente', 'success')
            return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

        # GET: Mostrar formulario con registro existente
        record_name = request.args.get('name')
        record_type = request.args.get('type')

        if not record_name or not record_type:
            flash('Parámetros de registro faltantes', 'error')
            return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

        # Buscar el registro existente
        records = r53.list_resource_record_sets(HostedZoneId=zone_id)
        record = None
        for r in records.get('ResourceRecordSets', []):
            if r['Name'] == record_name and r['Type'] == record_type:
                record = r
                break

        if not record:
            flash('Registro no encontrado', 'error')
            return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))

        return render_template('Redes/route53/update_record.html',
                             zone=zone,
                             record=record)

    except Exception as e:
        flash(f'Error actualizando registro: {str(e)}', 'error')
        return redirect(url_for('route53.list_resource_record_sets', zone_id=zone_id))