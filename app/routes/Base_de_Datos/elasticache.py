from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('elasticache', __name__)

@bp.route('/')
def index():
    return render_template('Base_de_Datos/elasticache/index.html')

@bp.route('/redis')
def redis_clusters():
    """Lista clusters Redis"""
    try:
        elasticache = get_aws_client('elasticache')
        clusters = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
        
        cluster_list = []
        for cluster in clusters['CacheClusters']:
            # Solo clusters Redis
            if cluster['Engine'] == 'redis':
                cluster_list.append({
                    'cluster_id': cluster['CacheClusterId'],
                    'status': cluster['CacheClusterStatus'],
                    'engine': cluster['Engine'],
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'cache_node_type': cluster.get('CacheNodeType', 'N/A'),
                    'num_cache_nodes': cluster.get('NumCacheNodes', 0),
                    'endpoint': cluster.get('CacheNodes', [{}])[0].get('Endpoint', {}).get('Address', 'N/A') if cluster.get('CacheNodes') else 'N/A',
                    'port': cluster.get('CacheNodes', [{}])[0].get('Endpoint', {}).get('Port', 'N/A') if cluster.get('CacheNodes') else 'N/A',
                    'encryption': cluster.get('TransitEncryptionEnabled', False)
                })
        
        return render_template('Base_de_Datos/elasticache/redis.html', clusters=cluster_list)
    except Exception as e:
        flash(f'Error obteniendo clusters Redis: {str(e)}', 'error')
        return render_template('Base_de_Datos/elasticache/redis.html', clusters=[])

@bp.route('/memcached')
def memcached_clusters():
    """Lista clusters Memcached"""
    try:
        elasticache = get_aws_client('elasticache')
        clusters = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
        
        cluster_list = []
        for cluster in clusters['CacheClusters']:
            # Solo clusters Memcached
            if cluster['Engine'] == 'memcached':
                cluster_list.append({
                    'cluster_id': cluster['CacheClusterId'],
                    'status': cluster['CacheClusterStatus'],
                    'engine': cluster['Engine'],
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'cache_node_type': cluster.get('CacheNodeType', 'N/A'),
                    'num_cache_nodes': cluster.get('NumCacheNodes', 0),
                    'endpoint': cluster.get('ConfigurationEndpoint', {}).get('Address', 'N/A'),
                    'port': cluster.get('ConfigurationEndpoint', {}).get('Port', 'N/A')
                })
        
        return render_template('Base_de_Datos/elasticache/memcached.html', clusters=cluster_list)
    except Exception as e:
        flash(f'Error obteniendo clusters Memcached: {str(e)}', 'error')
        return render_template('Base_de_Datos/elasticache/memcached.html', clusters=[])

@bp.route('/cluster/create', methods=['POST'])
def create_cluster():
    """Crea un cluster de ElastiCache"""
    try:
        elasticache = get_aws_client('elasticache')
        
        cluster_id = request.form.get('cluster_id')
        engine = request.form.get('engine', 'redis')  # redis o memcached
        node_type = request.form.get('node_type', 'cache.t3.micro')
        num_nodes = int(request.form.get('num_nodes', 1))
        engine_version = request.form.get('engine_version')
        
        create_params = {
            'CacheClusterId': cluster_id,
            'Engine': engine,
            'CacheNodeType': node_type,
            'NumCacheNodes': num_nodes
        }
        
        if engine_version:
            create_params['EngineVersion'] = engine_version
        
        # Para Redis, se puede especificar replication group
        if engine == 'redis':
            create_params['NumCacheNodes'] = 1  # Redis usa replication groups para múltiples nodos
        
        elasticache.create_cache_cluster(**create_params)
        flash(f'Cluster {cluster_id} creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error creando cluster: {str(e)}', 'error')
    
    return redirect(url_for('elasticache.redis_clusters' if engine == 'redis' else 'elasticache.memcached_clusters'))

@bp.route('/cluster/<cluster_id>/delete', methods=['POST'])
def delete_cluster(cluster_id):
    """Elimina un cluster de ElastiCache"""
    try:
        elasticache = get_aws_client('elasticache')
        
        elasticache.delete_cache_cluster(
            CacheClusterId=cluster_id,
            FinalSnapshotIdentifier=None  # No crear snapshot final
        )
        
        flash(f'Cluster {cluster_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando cluster: {str(e)}', 'error')
    
    return redirect(url_for('elasticache.index'))

@bp.route('/cluster/<cluster_id>/reboot', methods=['POST'])
def reboot_cluster(cluster_id):
    """Reinicia un cluster de ElastiCache"""
    try:
        elasticache = get_aws_client('elasticache')
        
        # Obtener información del cluster para reboot de nodos
        cluster = elasticache.describe_cache_clusters(
            CacheClusterId=cluster_id,
            ShowCacheNodeInfo=True
        )['CacheClusters'][0]
        
        node_ids = [node['CacheNodeId'] for node in cluster.get('CacheNodes', [])]
        
        elasticache.reboot_cache_cluster(
            CacheClusterId=cluster_id,
            CacheNodeIdsToReboot=node_ids
        )
        
        flash(f'Cluster {cluster_id} reiniciado exitosamente', 'success')
    except Exception as e:
        flash(f'Error reiniciando cluster: {str(e)}', 'error')
    
    return redirect(url_for('elasticache.index'))
