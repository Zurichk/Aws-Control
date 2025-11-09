from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client
import boto3

bp = Blueprint('eks', __name__)

@bp.route('/')
def index():
    return render_template('Contenedores/eks/index.html')

@bp.route('/clusters')
def clusters():
    try:
        eks = get_aws_client('eks')
        clusters = eks.list_clusters()
        cluster_list = []

        if clusters['clusters']:
            for cluster_name in clusters['clusters']:
                try:
                    # Get detailed cluster information
                    cluster_details = eks.describe_cluster(name=cluster_name)
                    cluster_info = cluster_details['cluster']

                    # Get node groups for this cluster
                    try:
                        nodegroups = eks.list_nodegroups(clusterName=cluster_name)
                        nodegroup_count = len(nodegroups['nodegroups'])
                    except:
                        nodegroup_count = 0

                    # Get Fargate profiles
                    try:
                        fargate_profiles = eks.list_fargate_profiles(clusterName=cluster_name)
                        fargate_count = len(fargate_profiles['fargateProfileNames'])
                    except:
                        fargate_count = 0

                    cluster_list.append({
                        'name': cluster_info['name'],
                        'arn': cluster_info['arn'],
                        'status': cluster_info['status'],
                        'version': cluster_info['version'],
                        'created_at': cluster_info['createdAt'].strftime('%Y-%m-%d %H:%M:%S'),
                        'endpoint': cluster_info.get('endpoint', 'N/A'),
                        'nodegroups': nodegroup_count,
                        'fargate_profiles': fargate_count,
                        'vpc_id': cluster_info.get('resourcesVpcConfig', {}).get('vpcId', 'N/A')
                    })
                except Exception as e:
                    # If we can't get details, add basic info
                    cluster_list.append({
                        'name': cluster_name,
                        'arn': 'N/A',
                        'status': 'Unknown',
                        'version': 'N/A',
                        'created_at': 'N/A',
                        'endpoint': 'N/A',
                        'nodegroups': 0,
                        'fargate_profiles': 0,
                        'vpc_id': 'N/A'
                    })

        return render_template('Contenedores/eks/clusters.html', clusters=cluster_list)
    except Exception as e:
        flash(f'Error obteniendo clusters EKS: {str(e)}', 'error')
        return render_template('Contenedores/eks/clusters.html', clusters=[])

@bp.route('/cluster/<cluster_name>')
def cluster_detail(cluster_name):
    try:
        eks = get_aws_client('eks')

        # Get cluster details
        cluster_details = eks.describe_cluster(name=cluster_name)
        cluster = cluster_details['cluster']

        # Get node groups
        try:
            nodegroups_response = eks.list_nodegroups(clusterName=cluster_name)
            nodegroups = []
            for ng_name in nodegroups_response['nodegroups']:
                ng_details = eks.describe_nodegroup(
                    clusterName=cluster_name,
                    nodegroupName=ng_name
                )
                nodegroups.append(ng_details['nodegroup'])
        except:
            nodegroups = []

        # Get Fargate profiles
        try:
            fargate_response = eks.list_fargate_profiles(clusterName=cluster_name)
            fargate_profiles = []
            for fp_name in fargate_response['fargateProfileNames']:
                fp_details = eks.describe_fargate_profile(
                    clusterName=cluster_name,
                    fargateProfileName=fp_name
                )
                fargate_profiles.append(fp_details['fargateProfile'])
        except:
            fargate_profiles = []

        return render_template('Contenedores/eks/cluster_detail.html',
                             cluster=cluster, nodegroups=nodegroups, fargate_profiles=fargate_profiles)
    except Exception as e:
        flash(f'Error obteniendo detalles del cluster: {str(e)}', 'error')
        return redirect(url_for('eks.clusters'))

@bp.route('/create-cluster', methods=['GET', 'POST'])
def create_cluster():
    if request.method == 'POST':
        cluster_name = request.form.get('cluster_name')
        kubernetes_version = request.form.get('kubernetes_version', '1.28')
        vpc_id = request.form.get('vpc_id')
        subnet_ids = request.form.getlist('subnet_ids[]')

        try:
            eks = get_aws_client('eks')

            # Create cluster configuration
            cluster_config = {
                'name': cluster_name,
                'version': kubernetes_version,
                'roleArn': request.form.get('role_arn'),
                'resourcesVpcConfig': {
                    'subnetIds': subnet_ids,
                    'endpointPublicAccess': True,
                    'endpointPrivateAccess': False
                }
            }

            if vpc_id:
                cluster_config['resourcesVpcConfig']['vpcId'] = vpc_id

            response = eks.create_cluster(**cluster_config)
            flash(f'Cluster EKS "{cluster_name}" está siendo creado. Esto puede tomar varios minutos.', 'success')
            return redirect(url_for('eks.clusters'))
        except Exception as e:
            flash(f'Error creando cluster EKS: {str(e)}', 'error')
    return render_template('Contenedores/eks/create_cluster.html')

@bp.route('/delete-cluster/<cluster_name>', methods=['POST'])
def delete_cluster(cluster_name):
    try:
        eks = get_aws_client('eks')
        eks.delete_cluster(name=cluster_name)
        flash(f'Cluster EKS "{cluster_name}" está siendo eliminado. Esto puede tomar varios minutos.', 'success')
    except Exception as e:
        flash(f'Error eliminando cluster EKS: {str(e)}', 'error')
    return redirect(url_for('eks.clusters'))

@bp.route('/cluster/<cluster_name>/nodegroups')
def nodegroups(cluster_name):
    try:
        eks = get_aws_client('eks')
        nodegroups_response = eks.list_nodegroups(clusterName=cluster_name)
        nodegroups_list = []

        for ng_name in nodegroups_response['nodegroups']:
            ng_details = eks.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=ng_name
            )
            nodegroups_list.append(ng_details['nodegroup'])

        return render_template('Contenedores/eks/nodegroups.html',
                             cluster_name=cluster_name, nodegroups=nodegroups_list)
    except Exception as e:
        flash(f'Error obteniendo node groups: {str(e)}', 'error')
        return redirect(url_for('eks.cluster_detail', cluster_name=cluster_name))

@bp.route('/cluster/<cluster_name>/create-nodegroup', methods=['GET', 'POST'])
def create_nodegroup(cluster_name):
    if request.method == 'POST':
        ng_name = request.form.get('nodegroup_name')
        instance_type = request.form.get('instance_type', 't3.medium')
        min_size = int(request.form.get('min_size', 1))
        max_size = int(request.form.get('max_size', 3))
        desired_size = int(request.form.get('desired_size', 2))
        subnet_ids = request.form.getlist('subnet_ids[]')

        try:
            eks = get_aws_client('eks')

            nodegroup_config = {
                'clusterName': cluster_name,
                'nodegroupName': ng_name,
                'subnets': subnet_ids,
                'nodeRole': request.form.get('node_role_arn'),
                'instanceTypes': [instance_type],
                'scalingConfig': {
                    'minSize': min_size,
                    'maxSize': max_size,
                    'desiredSize': desired_size
                }
            }

            eks.create_nodegroup(**nodegroup_config)
            flash(f'Node group "{ng_name}" está siendo creado.', 'success')
            return redirect(url_for('eks.nodegroups', cluster_name=cluster_name))
        except Exception as e:
            flash(f'Error creando node group: {str(e)}', 'error')
    return render_template('Contenedores/eks/create_nodegroup.html', cluster_name=cluster_name)