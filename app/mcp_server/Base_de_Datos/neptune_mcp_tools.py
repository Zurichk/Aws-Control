"""
Herramientas MCP para AWS Neptune
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class NeptuneMCPTools:
    """Herramientas MCP para gestión de clusters Neptune"""

    def __init__(self):
        self.neptune = None

    def _get_client(self):
        """Obtiene el cliente de Neptune"""
        if self.neptune is None:
            self.neptune = get_aws_client('neptune')
        return self.neptune

    def list_db_clusters(self) -> Dict[str, Any]:
        """
        Lista todos los clusters de Neptune

        Returns:
            Dict con lista de clusters
        """
        try:
            client = self._get_client()
            response = client.describe_db_clusters()

            clusters = []
            for cluster in response['DBClusters']:
                # Filtrar solo clusters de Neptune
                if cluster['Engine'] == 'neptune':
                    cluster_info = {
                        'cluster_identifier': cluster['DBClusterIdentifier'],
                        'status': cluster['Status'],
                        'engine': cluster['Engine'],
                        'engine_version': cluster['EngineVersion'],
                        'port': cluster.get('Port', 'N/A'),
                        'endpoint': cluster.get('Endpoint', 'N/A'),
                        'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                        'multi_az': cluster.get('MultiAZ', False),
                        'backup_retention_period': cluster.get('BackupRetentionPeriod', 0),
                        'preferred_backup_window': cluster.get('PreferredBackupWindow', 'N/A'),
                        'preferred_maintenance_window': cluster.get('PreferredMaintenanceWindow', 'N/A'),
                        'db_cluster_members': len(cluster.get('DBClusterMembers', [])),
                        'vpc_security_groups': [
                            sg['VpcSecurityGroupId']
                            for sg in cluster.get('VpcSecurityGroups', [])
                        ],
                        'db_subnet_group_name': cluster.get('DBSubnetGroupName', 'N/A'),
                        'storage_encrypted': cluster.get('StorageEncrypted', False),
                        'kms_key_id': cluster.get('KmsKeyId', 'N/A'),
                        'cluster_create_time': cluster.get('ClusterCreateTime', 'N/A'),
                        'latest_restorable_time': cluster.get('LatestRestorableTime', 'N/A'),
                        'enabled_cloudwatch_logs_exports': cluster.get('EnabledCloudwatchLogsExports', [])
                    }
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

    def create_db_cluster(self, cluster_identifier: str, master_username: str,
                         master_password: str, db_instance_class: str = 'db.t3.medium',
                         engine_version: str = '1.2.0.1',
                         vpc_security_group_ids: Optional[List[str]] = None,
                         db_subnet_group_name: Optional[str] = None,
                         storage_encrypted: bool = True) -> Dict[str, Any]:
        """
        Crea un nuevo cluster de Neptune

        Args:
            cluster_identifier: ID único del cluster
            master_username: Nombre del usuario maestro
            master_password: Contraseña del usuario maestro
            db_instance_class: Clase de instancia para la instancia primaria
            engine_version: Versión del engine Neptune
            vpc_security_group_ids: Lista de security groups
            db_subnet_group_name: Nombre del subnet group
            storage_encrypted: Si el almacenamiento debe estar encriptado

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            create_params = {
                'DBClusterIdentifier': cluster_identifier,
                'Engine': 'neptune',
                'EngineVersion': engine_version,
                'MasterUsername': master_username,
                'MasterUserPassword': master_password,
                'StorageEncrypted': storage_encrypted
            }

            if vpc_security_group_ids:
                create_params['VpcSecurityGroupIds'] = vpc_security_group_ids

            if db_subnet_group_name:
                create_params['DBSubnetGroupName'] = db_subnet_group_name

            # Crear el cluster
            cluster_response = client.create_db_cluster(**create_params)

            # Crear instancia primaria en el cluster
            instance_id = f"{cluster_identifier}-instance-1"
            instance_params = {
                'DBInstanceIdentifier': instance_id,
                'DBInstanceClass': db_instance_class,
                'Engine': 'neptune',
                'DBClusterIdentifier': cluster_identifier
            }

            instance_response = client.create_db_instance(**instance_params)

            return {
                'success': True,
                'cluster_identifier': cluster_identifier,
                'instance_identifier': instance_id,
                'status': 'creating',
                'message': f'Cluster Neptune {cluster_identifier} y instancia primaria creados exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_db_cluster(self, cluster_identifier: str, skip_final_snapshot: bool = True,
                         final_snapshot_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Elimina un cluster de Neptune

        Args:
            cluster_identifier: ID del cluster a eliminar
            skip_final_snapshot: Si omitir la creación de snapshot final
            final_snapshot_identifier: Nombre del snapshot final (requerido si skip_final_snapshot=False)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            # Primero obtener las instancias del cluster
            cluster_response = client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)
            if not cluster_response['DBClusters']:
                return {
                    'success': False,
                    'error': f'Cluster {cluster_identifier} no encontrado'
                }

            cluster = cluster_response['DBClusters'][0]

            # Eliminar todas las instancias del cluster primero
            for member in cluster.get('DBClusterMembers', []):
                instance_id = member['DBInstanceIdentifier']
                try:
                    client.delete_db_instance(
                        DBInstanceIdentifier=instance_id,
                        SkipFinalSnapshot=True
                    )
                except Exception as e:
                    # Log del error pero continuar
                    print(f"Error eliminando instancia {instance_id}: {str(e)}")

            # Luego eliminar el cluster
            delete_params = {
                'DBClusterIdentifier': cluster_identifier,
                'SkipFinalSnapshot': skip_final_snapshot
            }

            if not skip_final_snapshot and final_snapshot_identifier:
                delete_params['FinalDBSnapshotIdentifier'] = final_snapshot_identifier

            client.delete_db_cluster(**delete_params)

            return {
                'success': True,
                'cluster_identifier': cluster_identifier,
                'status': 'deleting',
                'message': f'Cluster Neptune {cluster_identifier} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def describe_db_cluster(self, cluster_identifier: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de un cluster Neptune específico

        Args:
            cluster_identifier: ID del cluster

        Returns:
            Dict con información detallada del cluster
        """
        try:
            client = self._get_client()
            response = client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)

            if not response['DBClusters']:
                return {
                    'success': False,
                    'error': f'Cluster {cluster_identifier} no encontrado'
                }

            cluster = response['DBClusters'][0]

            # Obtener instancias del cluster
            instances_response = client.describe_db_instances(
                Filters=[
                    {
                        'Name': 'db-cluster-id',
                        'Values': [cluster_identifier]
                    }
                ]
            )

            instances = []
            for instance in instances_response['DBInstances']:
                instance_info = {
                    'db_instance_identifier': instance['DBInstanceIdentifier'],
                    'db_instance_status': instance['DBInstanceStatus'],
                    'db_instance_class': instance['DBInstanceClass'],
                    'engine': instance['Engine'],
                    'endpoint': instance.get('Endpoint', {}),
                    'availability_zone': instance.get('AvailabilityZone', 'N/A'),
                    'backup_retention_period': instance.get('BackupRetentionPeriod', 0),
                    'preferred_backup_window': instance.get('PreferredBackupWindow', 'N/A'),
                    'preferred_maintenance_window': instance.get('PreferredMaintenanceWindow', 'N/A'),
                    'read_replica_db_instance_identifiers': instance.get('ReadReplicaDBInstanceIdentifiers', []),
                    'vpc_security_groups': [
                        sg['VpcSecurityGroupId']
                        for sg in instance.get('VpcSecurityGroups', [])
                    ]
                }
                instances.append(instance_info)

            cluster_info = {
                'cluster_identifier': cluster['DBClusterIdentifier'],
                'status': cluster['Status'],
                'engine': cluster['Engine'],
                'engine_version': cluster['EngineVersion'],
                'port': cluster.get('Port', 'N/A'),
                'endpoint': cluster.get('Endpoint', 'N/A'),
                'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                'multi_az': cluster.get('MultiAZ', False),
                'backup_retention_period': cluster.get('BackupRetentionPeriod', 0),
                'preferred_backup_window': cluster.get('PreferredBackupWindow', 'N/A'),
                'preferred_maintenance_window': cluster.get('PreferredMaintenanceWindow', 'N/A'),
                'db_cluster_members': cluster.get('DBClusterMembers', []),
                'vpc_security_groups': [
                    sg['VpcSecurityGroupId']
                    for sg in cluster.get('VpcSecurityGroups', [])
                ],
                'db_subnet_group_name': cluster.get('DBSubnetGroupName', 'N/A'),
                'storage_encrypted': cluster.get('StorageEncrypted', False),
                'kms_key_id': cluster.get('KmsKeyId', 'N/A'),
                'cluster_create_time': cluster.get('ClusterCreateTime', 'N/A'),
                'latest_restorable_time': cluster.get('LatestRestorableTime', 'N/A'),
                'enabled_cloudwatch_logs_exports': cluster.get('EnabledCloudwatchLogsExports', []),
                'instances': instances
            }

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
        """Retorna la lista de herramientas disponibles para Neptune"""
        return [
            {
                'name': 'neptune_list_db_clusters',
                'description': 'Lista todos los clusters de Neptune',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                },
                'function': self.list_db_clusters
            },
            {
                'name': 'neptune_create_db_cluster',
                'description': 'Crea un nuevo cluster de Neptune con instancia primaria',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_identifier', 'master_username', 'master_password'],
                    'properties': {
                        'cluster_identifier': {
                            'type': 'string',
                            'description': 'ID único del cluster'
                        },
                        'master_username': {
                            'type': 'string',
                            'description': 'Nombre del usuario maestro'
                        },
                        'master_password': {
                            'type': 'string',
                            'description': 'Contraseña del usuario maestro'
                        },
                        'db_instance_class': {
                            'type': 'string',
                            'description': 'Clase de instancia para la instancia primaria',
                            'default': 'db.t3.medium'
                        },
                        'engine_version': {
                            'type': 'string',
                            'description': 'Versión del engine Neptune',
                            'default': '1.2.0.1'
                        },
                        'vpc_security_group_ids': {
                            'type': 'array',
                            'description': 'Lista de security group IDs',
                            'items': {'type': 'string'}
                        },
                        'db_subnet_group_name': {
                            'type': 'string',
                            'description': 'Nombre del subnet group'
                        },
                        'storage_encrypted': {
                            'type': 'boolean',
                            'description': 'Si el almacenamiento debe estar encriptado',
                            'default': True
                        }
                    }
                },
                'function': self.create_db_cluster
            },
            {
                'name': 'neptune_delete_db_cluster',
                'description': 'Elimina un cluster de Neptune y todas sus instancias',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_identifier'],
                    'properties': {
                        'cluster_identifier': {
                            'type': 'string',
                            'description': 'ID del cluster a eliminar'
                        },
                        'skip_final_snapshot': {
                            'type': 'boolean',
                            'description': 'Omitir creación de snapshot final',
                            'default': True
                        },
                        'final_snapshot_identifier': {
                            'type': 'string',
                            'description': 'Nombre del snapshot final (requerido si skip_final_snapshot=false)'
                        }
                    }
                },
                'function': self.delete_db_cluster
            },
            {
                'name': 'neptune_describe_db_cluster',
                'description': 'Obtiene información detallada de un cluster Neptune específico',
                'parameters': {
                    'type': 'object',
                    'required': ['cluster_identifier'],
                    'properties': {
                        'cluster_identifier': {
                            'type': 'string',
                            'description': 'ID del cluster'
                        }
                    }
                },
                'function': self.describe_db_cluster
            }
        ]