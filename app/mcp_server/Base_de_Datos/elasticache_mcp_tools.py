"""
Herramientas MCP para AWS ElastiCache
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class ElastiCacheMCPTools:
    """Herramientas MCP para gestión de clusters ElastiCache (Redis y Memcached)"""

    def __init__(self):
        self.elasticache = None

    def _get_client(self):
        """Obtiene el cliente de ElastiCache"""
        if self.elasticache is None:
            self.elasticache = get_aws_client('elasticache')
        return self.elasticache

    def list_cache_clusters(self, engine: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista todos los clusters de ElastiCache, opcionalmente filtrados por engine

        Args:
            engine: 'redis' o 'memcached' para filtrar por tipo de engine

        Returns:
            Dict con lista de clusters
        """
        try:
            client = self._get_client()
            response = client.describe_cache_clusters(ShowCacheNodeInfo=True)

            clusters = []
            for cluster in response['CacheClusters']:
                if engine and cluster['Engine'] != engine:
                    continue

                cluster_info = {
                    'cluster_id': cluster['CacheClusterId'],
                    'status': cluster['CacheClusterStatus'],
                    'engine': cluster['Engine'],
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'cache_node_type': cluster.get('CacheNodeType', 'N/A'),
                    'num_cache_nodes': cluster.get('NumCacheNodes', 0),
                    'region': cluster.get('PreferredAvailabilityZone', 'N/A').split('-')[0] if cluster.get('PreferredAvailabilityZone') else 'N/A'
                }

                # Información específica de Redis
                if cluster['Engine'] == 'redis':
                    cluster_info['transit_encryption'] = cluster.get('TransitEncryptionEnabled', False)
                    cluster_info['at_rest_encryption'] = cluster.get('AtRestEncryptionEnabled', False)
                    if cluster.get('CacheNodes'):
                        node = cluster['CacheNodes'][0]
                        cluster_info['endpoint'] = node.get('Endpoint', {}).get('Address', 'N/A')
                        cluster_info['port'] = node.get('Endpoint', {}).get('Port', 'N/A')

                # Información específica de Memcached
                elif cluster['Engine'] == 'memcached':
                    cluster_info['az_mode'] = cluster.get('AZMode', 'N/A')
                    if cluster.get('ConfigurationEndpoint'):
                        cluster_info['endpoint'] = cluster['ConfigurationEndpoint'].get('Address', 'N/A')
                        cluster_info['port'] = cluster['ConfigurationEndpoint'].get('Port', 'N/A')

                clusters.append(cluster_info)

            return {
                'success': True,
                'clusters': clusters,
                'total_count': len(clusters)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'clusters': []
            }

    def create_cache_cluster(self, cluster_id: str, engine: str = 'redis',
                           cache_node_type: str = 'cache.t3.micro',
                           num_cache_nodes: int = 1,
                           engine_version: Optional[str] = None,
                           security_group_ids: Optional[List[str]] = None,
                           subnet_group_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea un nuevo cluster de ElastiCache

        Args:
            cluster_id: ID único del cluster
            engine: 'redis' o 'memcached'
            cache_node_type: Tipo de nodo (ej: cache.t3.micro)
            num_cache_nodes: Número de nodos
            engine_version: Versión del engine (opcional)
            security_group_ids: Lista de security groups (opcional)
            subnet_group_name: Nombre del subnet group (opcional)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            create_params = {
                'CacheClusterId': cluster_id,
                'Engine': engine,
                'CacheNodeType': cache_node_type,
                'NumCacheNodes': num_cache_nodes
            }

            if engine_version:
                create_params['EngineVersion'] = engine_version

            if security_group_ids:
                create_params['SecurityGroupIds'] = security_group_ids

            if subnet_group_name:
                create_params['CacheSubnetGroupName'] = subnet_group_name

            # Para Redis, limitar a 1 nodo si no se especifica replication group
            if engine == 'redis' and num_cache_nodes > 1:
                create_params['NumCacheNodes'] = 1

            response = client.create_cache_cluster(**create_params)

            return {
                'success': True,
                'cluster_id': cluster_id,
                'status': 'creating',
                'message': f'Cluster {cluster_id} creado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_cache_cluster(self, cluster_id: str, create_final_snapshot: bool = False,
                           final_snapshot_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Elimina un cluster de ElastiCache

        Args:
            cluster_id: ID del cluster a eliminar
            create_final_snapshot: Si crear snapshot final
            final_snapshot_identifier: Nombre del snapshot final (requerido si create_final_snapshot=True)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            delete_params = {'CacheClusterId': cluster_id}

            if create_final_snapshot:
                if not final_snapshot_identifier:
                    return {
                        'success': False,
                        'error': 'final_snapshot_identifier es requerido cuando create_final_snapshot=True'
                    }
                delete_params['FinalSnapshotIdentifier'] = final_snapshot_identifier
            else:
                delete_params['FinalSnapshotIdentifier'] = None

            response = client.delete_cache_cluster(**delete_params)

            return {
                'success': True,
                'cluster_id': cluster_id,
                'status': 'deleting',
                'message': f'Cluster {cluster_id} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def reboot_cache_cluster(self, cluster_id: str, cache_node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Reinicia nodos específicos de un cluster ElastiCache

        Args:
            cluster_id: ID del cluster
            cache_node_ids: Lista de IDs de nodos a reiniciar (opcional, reinicia todos si no se especifica)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            # Si no se especifican nodos, obtener todos los nodos del cluster
            if not cache_node_ids:
                cluster_info = client.describe_cache_clusters(
                    CacheClusterId=cluster_id,
                    ShowCacheNodeInfo=True
                )
                cache_node_ids = [
                    node['CacheNodeId']
                    for node in cluster_info['CacheClusters'][0].get('CacheNodes', [])
                ]

            if not cache_node_ids:
                return {
                    'success': False,
                    'error': 'No se encontraron nodos para reiniciar'
                }

            response = client.reboot_cache_cluster(
                CacheClusterId=cluster_id,
                CacheNodeIdsToReboot=cache_node_ids
            )

            return {
                'success': True,
                'cluster_id': cluster_id,
                'rebooted_nodes': cache_node_ids,
                'message': f'Cluster {cluster_id} reiniciado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def describe_cache_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de un cluster específico

        Args:
            cluster_id: ID del cluster

        Returns:
            Dict con información detallada del cluster
        """
        try:
            client = self._get_client()
            response = client.describe_cache_clusters(
                CacheClusterId=cluster_id,
                ShowCacheNodeInfo=True
            )

            if not response['CacheClusters']:
                return {
                    'success': False,
                    'error': f'Cluster {cluster_id} no encontrado'
                }

            cluster = response['CacheClusters'][0]

            cluster_info = {
                'cluster_id': cluster['CacheClusterId'],
                'status': cluster['CacheClusterStatus'],
                'engine': cluster['Engine'],
                'engine_version': cluster.get('EngineVersion', 'N/A'),
                'cache_node_type': cluster.get('CacheNodeType', 'N/A'),
                'num_cache_nodes': cluster.get('NumCacheNodes', 0),
                'preferred_az': cluster.get('PreferredAvailabilityZone', 'N/A'),
                'security_groups': [
                    sg['SecurityGroupId']
                    for sg in cluster.get('SecurityGroups', [])
                ],
                'subnet_group_name': cluster.get('CacheSubnetGroupName', 'N/A'),
                'maintenance_window': cluster.get('PreferredMaintenanceWindow', 'N/A'),
                'snapshot_window': cluster.get('SnapshotWindow', 'N/A'),
                'snapshot_retention_limit': cluster.get('SnapshotRetentionLimit', 0)
            }

            # Información específica por engine
            if cluster['Engine'] == 'redis':
                cluster_info.update({
                    'transit_encryption': cluster.get('TransitEncryptionEnabled', False),
                    'at_rest_encryption': cluster.get('AtRestEncryptionEnabled', False),
                    'auth_token_enabled': cluster.get('AuthTokenEnabled', False)
                })
                if cluster.get('CacheNodes'):
                    node = cluster['CacheNodes'][0]
                    cluster_info['endpoint'] = node.get('Endpoint', {}).get('Address', 'N/A')
                    cluster_info['port'] = node.get('Endpoint', {}).get('Port', 'N/A')

            elif cluster['Engine'] == 'memcached':
                cluster_info['az_mode'] = cluster.get('AZMode', 'N/A')
                if cluster.get('ConfigurationEndpoint'):
                    cluster_info['endpoint'] = cluster['ConfigurationEndpoint'].get('Address', 'N/A')
                    cluster_info['port'] = cluster['ConfigurationEndpoint'].get('Port', 'N/A')

            return {
                'success': True,
                'cluster': cluster_info
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para ElastiCache"""
        return [
            {
                'name': 'elasticache_list_cache_clusters',
                'description': 'Lista todos los clusters de ElastiCache, opcionalmente filtrados por engine (redis/memcached)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'engine': {
                            'type': 'string',
                            'description': 'Filtrar por engine: "redis" o "memcached"',
                            'enum': ['redis', 'memcached']
                        }
                    }
                },
                'function': self.list_cache_clusters
            },
            {
                'name': 'elasticache_create_cache_cluster',
                'description': 'Crea un nuevo cluster de ElastiCache (Redis o Memcached)',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_id', 'engine'],
                    'properties': {
                        'cluster_id': {
                            'type': 'string',
                            'description': 'ID único del cluster'
                        },
                        'engine': {
                            'type': 'string',
                            'description': 'Engine del cluster',
                            'enum': ['redis', 'memcached']
                        },
                        'cache_node_type': {
                            'type': 'string',
                            'description': 'Tipo de nodo (ej: cache.t3.micro)',
                            'default': 'cache.t3.micro'
                        },
                        'num_cache_nodes': {
                            'type': 'integer',
                            'description': 'Número de nodos',
                            'default': 1,
                            'minimum': 1,
                            'maximum': 20
                        },
                        'engine_version': {
                            'type': 'string',
                            'description': 'Versión del engine'
                        },
                        'security_group_ids': {
                            'type': 'array',
                            'description': 'Lista de security group IDs',
                            'items': {'type': 'string'}
                        },
                        'subnet_group_name': {
                            'type': 'string',
                            'description': 'Nombre del subnet group'
                        }
                    }
                },
                'function': self.create_cache_cluster
            },
            {
                'name': 'elasticache_delete_cache_cluster',
                'description': 'Elimina un cluster de ElastiCache',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_id'],
                    'properties': {
                        'cluster_id': {
                            'type': 'string',
                            'description': 'ID del cluster a eliminar'
                        },
                        'create_final_snapshot': {
                            'type': 'boolean',
                            'description': 'Crear snapshot final antes de eliminar',
                            'default': False
                        },
                        'final_snapshot_identifier': {
                            'type': 'string',
                            'description': 'Nombre del snapshot final (requerido si create_final_snapshot=true)'
                        }
                    }
                },
                'function': self.delete_cache_cluster
            },
            {
                'name': 'elasticache_reboot_cache_cluster',
                'description': 'Reinicia nodos específicos de un cluster ElastiCache',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_id'],
                    'properties': {
                        'cluster_id': {
                            'type': 'string',
                            'description': 'ID del cluster a reiniciar'
                        },
                        'cache_node_ids': {
                            'type': 'array',
                            'description': 'Lista de IDs de nodos a reiniciar (opcional, reinicia todos si no se especifica)',
                            'items': {'type': 'string'}
                        }
                    }
                },
                'function': self.reboot_cache_cluster
            },
            {
                'name': 'elasticache_describe_cache_cluster',
                'description': 'Obtiene información detallada de un cluster específico',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_id'],
                    'properties': {
                        'cluster_id': {
                            'type': 'string',
                            'description': 'ID del cluster'
                        }
                    }
                },
                'function': self.describe_cache_cluster
            }
        ]