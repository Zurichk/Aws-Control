"""
Rutas para Amazon Neptune (Graph Database)
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('neptune', __name__)

@bp.route('/')
def index():
    """Página principal de Neptune"""
    return render_template('Base_de_Datos/neptune/index.html')

@bp.route('/clusters')
def clusters():
    """Lista clusters de Neptune"""
    try:
        neptune = get_aws_client('neptune')
        response = neptune.describe_db_clusters()
        
        clusters = []
        for cluster in response['DBClusters']:
            # Filtrar solo clusters de Neptune
            if cluster['Engine'] == 'neptune':
                clusters.append({
                    'identifier': cluster['DBClusterIdentifier'],
                    'engine': cluster['Engine'],
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'status': cluster['Status'],
                    'endpoint': cluster.get('Endpoint', 'N/A'),
                    'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                    'multi_az': cluster.get('MultiAZ', False),
                    'members': len(cluster.get('DBClusterMembers', [])),
                    'storage_encrypted': cluster.get('StorageEncrypted', False)
                })
        
        return render_template('Base_de_Datos/neptune/clusters.html', clusters=clusters)
    
    except Exception as e:
        flash(f'Error listando clusters de Neptune: {str(e)}', 'danger')
        return render_template('Base_de_Datos/neptune/clusters.html', clusters=[])


@bp.route('/cluster/create', methods=['POST'])
def create_cluster():
    """Crea un cluster de Neptune"""
    try:
        neptune = get_aws_client('neptune')
        
        cluster_id = request.form.get('cluster_identifier')
        instance_class = request.form.get('instance_class', 'db.t3.medium')
        engine_version = request.form.get('engine_version', '1.2.1.0')
        
        # Crear cluster
        neptune.create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine='neptune',
            EngineVersion=engine_version,
            MasterUsername='admin',
            MasterUserPassword=request.form.get('master_password'),
            StorageEncrypted=True
        )
        
        # Crear instancia primaria en el cluster
        neptune.create_db_instance(
            DBInstanceIdentifier=f"{cluster_id}-instance-1",
            DBInstanceClass=instance_class,
            Engine='neptune',
            DBClusterIdentifier=cluster_id
        )
        
        flash(f'Cluster Neptune "{cluster_id}" creado exitosamente', 'success')
    
    except Exception as e:
        flash(f'Error creando cluster Neptune: {str(e)}', 'danger')
    
    return redirect(url_for('neptune.clusters'))


@bp.route('/cluster/<cluster_id>/delete', methods=['POST'])
def delete_cluster(cluster_id):
    """Elimina un cluster de Neptune"""
    try:
        neptune = get_aws_client('neptune')
        
        # Primero eliminar las instancias del cluster
        response = neptune.describe_db_clusters(DBClusterIdentifier=cluster_id)
        cluster = response['DBClusters'][0]
        
        for member in cluster.get('DBClusterMembers', []):
            instance_id = member['DBInstanceIdentifier']
            try:
                neptune.delete_db_instance(
                    DBInstanceIdentifier=instance_id,
                    SkipFinalSnapshot=True
                )
            except Exception as e:
                flash(f'Error eliminando instancia {instance_id}: {str(e)}', 'warning')
        
        # Luego eliminar el cluster
        neptune.delete_db_cluster(
            DBClusterIdentifier=cluster_id,
            SkipFinalSnapshot=True
        )
        
        flash(f'Cluster Neptune "{cluster_id}" eliminado exitosamente', 'success')
    
    except Exception as e:
        flash(f'Error eliminando cluster Neptune: {str(e)}', 'danger')
    
    return redirect(url_for('neptune.clusters'))
