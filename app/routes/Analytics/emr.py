from flask import Blueprint, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

emr_bp = Blueprint('emr', __name__, url_prefix='/emr')

def get_emr_client():
    """Get EMR client with error handling"""
    try:
        return boto3.client('emr', region_name='us-east-1')
    except Exception as e:
        logger.error(f"Error creating EMR client: {e}")
        return None

@emr_bp.route('/')
def index():
    """EMR dashboard"""
    try:
        client = get_emr_client()
        if not client:
            flash('Error connecting to EMR service', 'error')
            return render_template('emr/index.html', clusters=[])

        # Get all clusters
        response = client.list_clusters()
        clusters = response.get('Clusters', [])

        # Get detailed information for each cluster
        detailed_clusters = []
        for cluster in clusters:
            try:
                cluster_detail = client.describe_cluster(ClusterId=cluster['Id'])
                detailed_clusters.append(cluster_detail['Cluster'])
            except ClientError as e:
                logger.error(f"Error getting cluster details for {cluster['Id']}: {e}")
                detailed_clusters.append(cluster)

        return render_template('emr/index.html', clusters=detailed_clusters)

    except ClientError as e:
        logger.error(f"Error listing EMR clusters: {e}")
        flash(f'Error listing EMR clusters: {e}', 'error')
        return render_template('emr/index.html', clusters=[])
    except Exception as e:
        logger.error(f"Unexpected error in EMR index: {e}")
        flash('Unexpected error occurred', 'error')
        return render_template('emr/index.html', clusters=[])

@emr_bp.route('/clusters')
def clusters():
    """List all EMR clusters"""
    try:
        client = get_emr_client()
        if not client:
            flash('Error connecting to EMR service', 'error')
            return render_template('emr/clusters.html', clusters=[])

        response = client.list_clusters()
        clusters = response.get('Clusters', [])

        return render_template('emr/clusters.html', clusters=clusters)

    except ClientError as e:
        logger.error(f"Error listing EMR clusters: {e}")
        flash(f'Error listing EMR clusters: {e}', 'error')
        return render_template('emr/clusters.html', clusters=[])
    except Exception as e:
        logger.error(f"Unexpected error in EMR clusters: {e}")
        flash('Unexpected error occurred', 'error')
        return render_template('emr/clusters.html', clusters=[])

@emr_bp.route('/create', methods=['GET', 'POST'])
def create_cluster():
    """Create a new EMR cluster"""
    if request.method == 'POST':
        try:
            client = get_emr_client()
            if not client:
                flash('Error connecting to EMR service', 'error')
                return redirect(url_for('emr.clusters'))

            cluster_name = request.form.get('cluster_name')
            instance_count = int(request.form.get('instance_count', 3))
            instance_type = request.form.get('instance_type', 'm5.xlarge')
            release_label = request.form.get('release_label', 'emr-6.4.0')

            if not cluster_name:
                flash('Cluster name is required', 'error')
                return redirect(url_for('emr.create_cluster'))

            # Create the cluster
            response = client.run_job_flow(
                Name=cluster_name,
                ReleaseLabel=release_label,
                Instances={
                    'MasterInstanceType': instance_type,
                    'SlaveInstanceType': instance_type,
                    'InstanceCount': instance_count,
                    'KeepJobFlowAliveWhenNoSteps': True,
                    'TerminationProtected': False
                },
                ServiceRole='EMR_DefaultRole',
                JobFlowRole='EMR_EC2_DefaultRole',
                Steps=[]
            )

            cluster_id = response['JobFlowId']
            flash(f'EMR cluster "{cluster_name}" created successfully with ID: {cluster_id}', 'success')
            return redirect(url_for('emr.clusters'))

        except ClientError as e:
            logger.error(f"Error creating EMR cluster: {e}")
            flash(f'Error creating EMR cluster: {e}', 'error')
            return redirect(url_for('emr.create_cluster'))
        except Exception as e:
            logger.error(f"Unexpected error creating EMR cluster: {e}")
            flash('Unexpected error occurred while creating cluster', 'error')
            return redirect(url_for('emr.create_cluster'))

    return render_template('emr/create.html')

@emr_bp.route('/terminate/<cluster_id>', methods=['POST'])
def terminate_cluster(cluster_id):
    """Terminate an EMR cluster"""
    try:
        client = get_emr_client()
        if not client:
            flash('Error connecting to EMR service', 'error')
            return redirect(url_for('emr.clusters'))

        # Terminate the cluster
        client.terminate_job_flows(JobFlowIds=[cluster_id])

        flash(f'EMR cluster {cluster_id} termination initiated', 'success')
        return redirect(url_for('emr.clusters'))

    except ClientError as e:
        logger.error(f"Error terminating EMR cluster {cluster_id}: {e}")
        flash(f'Error terminating EMR cluster: {e}', 'error')
        return redirect(url_for('emr.clusters'))
    except Exception as e:
        logger.error(f"Unexpected error terminating EMR cluster {cluster_id}: {e}")
        flash('Unexpected error occurred while terminating cluster', 'error')
        return redirect(url_for('emr.clusters'))