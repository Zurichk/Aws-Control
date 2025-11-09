from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('vpc', __name__)

@bp.route('/vpc')
def index():
    return render_template('Redes/vpc/index.html')

@bp.route('/vpc/vpcs')
def vpcs():
    try:
        ec2 = get_aws_client('ec2')
        vpcs = ec2.describe_vpcs()
        vpc_list = []
        for vpc in vpcs['Vpcs']:
            vpc_list.append({
                'id': vpc['VpcId'],
                'state': vpc['State'],
                'cidr': vpc['CidrBlock'],
                'is_default': vpc['IsDefault']
            })
        return render_template('Redes/vpc/vpcs.html', vpcs=vpc_list)
    except Exception as e:
        flash(f'Error obteniendo VPCs: {str(e)}', 'error')
        return render_template('Redes/vpc/vpcs.html', vpcs=[])

@bp.route('/vpc/subnets')
def subnets():
    try:
        ec2 = get_aws_client('ec2')
        subnets = ec2.describe_subnets()
        subnet_list = []
        for subnet in subnets['Subnets']:
            subnet_list.append({
                'id': subnet['SubnetId'],
                'vpc_id': subnet['VpcId'],
                'cidr': subnet['CidrBlock'],
                'availability_zone': subnet['AvailabilityZone'],
                'state': subnet['State'],
                'available_ip_address_count': subnet.get('AvailableIpAddressCount', 'N/A')
            })
        return render_template('Redes/vpc/subnets.html', subnets=subnet_list)
    except Exception as e:
        flash(f'Error obteniendo subnets: {str(e)}', 'error')
        return render_template('Redes/vpc/subnets.html', subnets=[])

@bp.route('/vpc/create_subnet', methods=['GET', 'POST'])
def create_subnet():
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            vpc_id = request.form['vpc_id']
            cidr_block = request.form['cidr_block']
            availability_zone = request.form.get('availability_zone')

            params = {
                'VpcId': vpc_id,
                'CidrBlock': cidr_block
            }
            if availability_zone:
                params['AvailabilityZone'] = availability_zone

            response = ec2.create_subnet(**params)
            subnet_id = response['Subnet']['SubnetId']

            flash(f'Subnet {subnet_id} creada exitosamente', 'success')
            return redirect(url_for('vpc.subnets'))
        except Exception as e:
            flash(f'Error creando subnet: {str(e)}', 'error')

    # GET request - show form
    try:
        ec2 = get_aws_client('ec2')
        vpcs = ec2.describe_vpcs()['Vpcs']
        availability_zones = ec2.describe_availability_zones()['AvailabilityZones']
        return render_template('Redes/vpc/create_subnet.html', vpcs=vpcs, availability_zones=availability_zones)
    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Redes/vpc/create_subnet.html', vpcs=[], availability_zones=[])

@bp.route('/vpc/delete_subnet/<subnet_id>', methods=['POST'])
def delete_subnet(subnet_id):
    try:
        ec2 = get_aws_client('ec2')
        ec2.delete_subnet(SubnetId=subnet_id)
        flash(f'Subnet {subnet_id} eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando subnet: {str(e)}', 'error')
    return redirect(url_for('vpc.subnets'))

@bp.route('/vpc/route_tables')
def route_tables():
    try:
        ec2 = get_aws_client('ec2')
        route_tables = ec2.describe_route_tables()
        rt_list = []
        for rt in route_tables['RouteTables']:
            rt_list.append({
                'id': rt['RouteTableId'],
                'vpc_id': rt['VpcId'],
                'associations': len(rt.get('Associations', [])),
                'routes': len(rt.get('Routes', []))
            })
        return render_template('Redes/vpc/route_tables.html', route_tables=rt_list)
    except Exception as e:
        flash(f'Error obteniendo route tables: {str(e)}', 'error')
        return render_template('Redes/vpc/route_tables.html', route_tables=[])

@bp.route('/vpc/create_route_table', methods=['GET', 'POST'])
def create_route_table():
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            vpc_id = request.form['vpc_id']

            response = ec2.create_route_table(VpcId=vpc_id)
            rt_id = response['RouteTable']['RouteTableId']

            flash(f'Route table {rt_id} creada exitosamente', 'success')
            return redirect(url_for('vpc.route_tables'))
        except Exception as e:
            flash(f'Error creando route table: {str(e)}', 'error')

    # GET request - show form
    try:
        ec2 = get_aws_client('ec2')
        vpcs = ec2.describe_vpcs()['Vpcs']
        return render_template('Redes/vpc/create_route_table.html', vpcs=vpcs)
    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Redes/vpc/create_route_table.html', vpcs=[])

@bp.route('/vpc/internet_gateways')
def internet_gateways():
    try:
        ec2 = get_aws_client('ec2')
        igws = ec2.describe_internet_gateways()
        igw_list = []
        for igw in igws['InternetGateways']:
            igw_list.append({
                'id': igw['InternetGatewayId'],
                'state': igw.get('Attachments', [{}])[0].get('State', 'detached'),
                'vpc_id': igw.get('Attachments', [{}])[0].get('VpcId', 'N/A')
            })
        return render_template('Redes/vpc/internet_gateways.html', internet_gateways=igw_list)
    except Exception as e:
        flash(f'Error obteniendo internet gateways: {str(e)}', 'error')
        return render_template('Redes/vpc/internet_gateways.html', internet_gateways=[])

@bp.route('/vpc/create_internet_gateway', methods=['GET', 'POST'])
def create_internet_gateway():
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            response = ec2.create_internet_gateway()
            igw_id = response['InternetGateway']['InternetGatewayId']

            flash(f'Internet Gateway {igw_id} creado exitosamente', 'success')
            return redirect(url_for('vpc.internet_gateways'))
        except Exception as e:
            flash(f'Error creando internet gateway: {str(e)}', 'error')
            return redirect(url_for('vpc.internet_gateways'))

    return render_template('Redes/vpc/create_internet_gateway.html')

@bp.route('/vpc/attach_internet_gateway/<igw_id>', methods=['GET', 'POST'])
def attach_internet_gateway(igw_id):
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            vpc_id = request.form['vpc_id']

            ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            flash(f'Internet Gateway {igw_id} adjuntado a VPC {vpc_id}', 'success')
            return redirect(url_for('vpc.internet_gateways'))
        except Exception as e:
            flash(f'Error adjuntando internet gateway: {str(e)}', 'error')

    # GET request - show form
    try:
        ec2 = get_aws_client('ec2')
        vpcs = ec2.describe_vpcs()['Vpcs']
        return render_template('Redes/vpc/attach_internet_gateway.html', igw_id=igw_id, vpcs=vpcs)
    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Redes/vpc/attach_internet_gateway.html', igw_id=igw_id, vpcs=[])

@bp.route('/vpc/nat_gateways')
def nat_gateways():
    try:
        ec2 = get_aws_client('ec2')
        nat_gateways = ec2.describe_nat_gateways()
        nat_list = []
        for nat in nat_gateways['NatGateways']:
            nat_list.append({
                'id': nat['NatGatewayId'],
                'state': nat['State'],
                'vpc_id': nat['VpcId'],
                'subnet_id': nat['SubnetId'],
                'connectivity_type': nat.get('ConnectivityType', 'public')
            })
        return render_template('Redes/vpc/nat_gateways.html', nat_gateways=nat_list)
    except Exception as e:
        flash(f'Error obteniendo NAT gateways: {str(e)}', 'error')
        return render_template('Redes/vpc/nat_gateways.html', nat_gateways=[])

@bp.route('/vpc/create_nat_gateway', methods=['GET', 'POST'])
def create_nat_gateway():
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            subnet_id = request.form['subnet_id']
            connectivity_type = request.form.get('connectivity_type', 'public')
            allocation_id = request.form.get('allocation_id')

            params = {
                'SubnetId': subnet_id,
                'ConnectivityType': connectivity_type
            }

            if connectivity_type == 'public' and allocation_id:
                params['AllocationId'] = allocation_id

            response = ec2.create_nat_gateway(**params)
            nat_id = response['NatGateway']['NatGatewayId']

            flash(f'NAT Gateway {nat_id} creado exitosamente', 'success')
            return redirect(url_for('vpc.nat_gateways'))
        except Exception as e:
            flash(f'Error creando NAT gateway: {str(e)}', 'error')

    # GET request - show form
    try:
        ec2 = get_aws_client('ec2')
        subnets = ec2.describe_subnets()['Subnets']
        # Get Elastic IPs for allocation
        elastic_ips = ec2.describe_addresses()['Addresses']
        return render_template('Redes/vpc/create_nat_gateway.html', subnets=subnets, elastic_ips=elastic_ips)
    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Redes/vpc/create_nat_gateway.html', subnets=[], elastic_ips=[])

@bp.route('/vpc/vpc_peerings')
def vpc_peerings():
    try:
        ec2 = get_aws_client('ec2')
        peerings = ec2.describe_vpc_peering_connections()
        peering_list = []
        for peering in peerings['VpcPeeringConnections']:
            peering_list.append({
                'id': peering['VpcPeeringConnectionId'],
                'status': peering['Status']['Code'],
                'requester_vpc': peering['RequesterVpcInfo']['VpcId'],
                'accepter_vpc': peering['AccepterVpcInfo']['VpcId']
            })
        return render_template('Redes/vpc/vpc_peerings.html', vpc_peerings=peering_list)
    except Exception as e:
        flash(f'Error obteniendo VPC peerings: {str(e)}', 'error')
        return render_template('Redes/vpc/vpc_peerings.html', vpc_peerings=[])

@bp.route('/vpc/create_vpc_peering', methods=['GET', 'POST'])
def create_vpc_peering():
    if request.method == 'POST':
        try:
            ec2 = get_aws_client('ec2')
            requester_vpc_id = request.form['requester_vpc_id']
            peer_vpc_id = request.form['peer_vpc_id']
            peer_owner_id = request.form.get('peer_owner_id')

            params = {
                'VpcId': requester_vpc_id,
                'PeerVpcId': peer_vpc_id
            }
            if peer_owner_id:
                params['PeerOwnerId'] = peer_owner_id

            response = ec2.create_vpc_peering_connection(**params)
            peering_id = response['VpcPeeringConnection']['VpcPeeringConnectionId']

            flash(f'VPC Peering {peering_id} creado exitosamente', 'success')
            return redirect(url_for('vpc.vpc_peerings'))
        except Exception as e:
            flash(f'Error creando VPC peering: {str(e)}', 'error')

    # GET request - show form
    try:
        ec2 = get_aws_client('ec2')
        vpcs = ec2.describe_vpcs()['Vpcs']
        return render_template('Redes/vpc/create_vpc_peering.html', vpcs=vpcs)
    except Exception as e:
        flash(f'Error cargando formulario: {str(e)}', 'error')
        return render_template('Redes/vpc/create_vpc_peering.html', vpcs=[])

@bp.route('/vpc/accept_vpc_peering/<peering_id>', methods=['POST'])
def accept_vpc_peering(peering_id):
    try:
        ec2 = get_aws_client('ec2')
        ec2.accept_vpc_peering_connection(VpcPeeringConnectionId=peering_id)
        flash(f'VPC Peering {peering_id} aceptado exitosamente', 'success')
    except Exception as e:
        flash(f'Error aceptando VPC peering: {str(e)}', 'error')
    return redirect(url_for('vpc.vpc_peerings'))