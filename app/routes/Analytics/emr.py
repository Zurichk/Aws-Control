from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.mcp_server.Analytics.emr_mcp_tools import EMRMCPTools
import logging

logger = logging.getLogger(__name__)

emr_bp = Blueprint('emr', __name__, url_prefix='/emr')

# Initialize EMR MCP tools
emr_tools = EMRMCPTools()

@emr_bp.route('/')
def index():
    """EMR dashboard"""
    try:
        result = emr_tools.list_emr_clusters()

        if result['success']:
            clusters = result['clusters']
            return render_template('emr/index.html', clusters=clusters)
        else:
            flash(f'Error listing EMR clusters: {result["error"]}', 'error')
            return render_template('emr/index.html', clusters=[])

    except Exception as e:
        logger.error(f"Unexpected error in EMR index: {e}")
        flash('Unexpected error occurred', 'error')
        return render_template('emr/index.html', clusters=[])

@emr_bp.route('/clusters')
def clusters():
    """List all EMR clusters"""
    try:
        result = emr_tools.list_emr_clusters()

        if result['success']:
            clusters = result['clusters']
            return render_template('emr/clusters.html', clusters=clusters)
        else:
            flash(f'Error listing EMR clusters: {result["error"]}', 'error')
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
            cluster_name = request.form.get('cluster_name')
            instance_count = int(request.form.get('instance_count', 3))
            instance_type = request.form.get('instance_type', 'm5.xlarge')
            release_label = request.form.get('release_label', 'emr-6.4.0')

            result = emr_tools.create_emr_cluster(
                cluster_name=cluster_name,
                instance_count=instance_count,
                instance_type=instance_type,
                release_label=release_label
            )

            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('emr.index'))
            else:
                flash(f'Error creating EMR cluster: {result["error"]}', 'error')
                return redirect(url_for('emr.create_cluster'))

        except Exception as e:
            logger.error(f"Unexpected error creating EMR cluster: {e}")
            flash('Unexpected error occurred while creating cluster', 'error')
            return redirect(url_for('emr.create_cluster'))

    return render_template('emr/create_cluster.html')

    return render_template('emr/create.html')

@emr_bp.route('/terminate/<cluster_id>', methods=['POST'])
def terminate_cluster(cluster_id):
    """Terminate an EMR cluster"""
    try:
        result = emr_tools.terminate_emr_cluster(cluster_id=cluster_id)

        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('emr.index'))
        else:
            flash(f'Error terminating EMR cluster: {result["error"]}', 'error')
            return redirect(url_for('emr.index'))

    except Exception as e:
        logger.error(f"Unexpected error terminating EMR cluster {cluster_id}: {e}")
        flash('Unexpected error occurred while terminating cluster', 'error')
        return redirect(url_for('emr.index'))