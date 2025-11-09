"""
Rutas para Amazon DocumentDB (compatible con MongoDB)
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('documentdb', __name__)

@bp.route('/')
def index():
    """Página principal de DocumentDB"""
    return render_template('Base_de_Datos/documentdb/index.html')

@bp.route('/clusters')
def clusters():
    """Lista clusters de DocumentDB"""
    try:
        docdb = get_aws_client('docdb')
        response = docdb.describe_db_clusters()
        
        clusters = []
        for cluster in response['DBClusters']:
            # Filtrar solo clusters de DocumentDB
            if cluster['Engine'] == 'docdb':
                clusters.append({
                    'identifier': cluster['DBClusterIdentifier'],
                    'engine': cluster['Engine'],
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'status': cluster['Status'],
                    'endpoint': cluster.get('Endpoint', 'N/A'),
                    'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                    'port': cluster.get('Port', 27017),
                    'multi_az': cluster.get('MultiAZ', False),
                    'members': len(cluster.get('DBClusterMembers', [])),
                    'storage_encrypted': cluster.get('StorageEncrypted', False)
                })
        
        return render_template('Base_de_Datos/documentdb/clusters.html', clusters=clusters)
    
    except Exception as e:
        flash(f'Error listando clusters de DocumentDB: {str(e)}', 'danger')
        return render_template('Base_de_Datos/documentdb/clusters.html', clusters=[])


@bp.route('/cluster/create', methods=['POST'])
def create_cluster():
    """Crea un cluster de DocumentDB"""
    try:
        docdb = get_aws_client('docdb')
        
        cluster_id = request.form.get('cluster_identifier')
        instance_class = request.form.get('instance_class', 'db.t3.medium')
        engine_version = request.form.get('engine_version', '5.0.0')
        
        # Crear cluster
        docdb.create_db_cluster(
            DBClusterIdentifier=cluster_id,
            Engine='docdb',
            EngineVersion=engine_version,
            MasterUsername='docdbadmin',
            MasterUserPassword=request.form.get('master_password'),
            StorageEncrypted=True,
            Port=27017
        )
        
        # Crear instancia primaria en el cluster
        docdb.create_db_instance(
            DBInstanceIdentifier=f"{cluster_id}-instance-1",
            DBInstanceClass=instance_class,
            Engine='docdb',
            DBClusterIdentifier=cluster_id
        )
        
        flash(f'Cluster DocumentDB "{cluster_id}" creado exitosamente', 'success')
    
    except Exception as e:
        flash(f'Error creando cluster DocumentDB: {str(e)}', 'danger')
    
    return redirect(url_for('documentdb.clusters'))


@bp.route('/cluster/<cluster_id>/delete', methods=['POST'])
def delete_cluster(cluster_id):
    """Elimina un cluster de DocumentDB"""
    try:
        docdb = get_aws_client('docdb')
        
        # Primero eliminar las instancias del cluster
        response = docdb.describe_db_clusters(DBClusterIdentifier=cluster_id)
        cluster = response['DBClusters'][0]
        
        for member in cluster.get('DBClusterMembers', []):
            instance_id = member['DBInstanceIdentifier']
            try:
                docdb.delete_db_instance(
                    DBInstanceIdentifier=instance_id,
                    SkipFinalSnapshot=True
                )
            except Exception as e:
                flash(f'Error eliminando instancia {instance_id}: {str(e)}', 'warning')
        
        # Luego eliminar el cluster
        docdb.delete_db_cluster(
            DBClusterIdentifier=cluster_id,
            SkipFinalSnapshot=True
        )
        
        flash(f'Cluster DocumentDB "{cluster_id}" eliminado exitosamente', 'success')
    
    except Exception as e:
        flash(f'Error eliminando cluster DocumentDB: {str(e)}', 'danger')
    
    return redirect(url_for('documentdb.clusters'))
