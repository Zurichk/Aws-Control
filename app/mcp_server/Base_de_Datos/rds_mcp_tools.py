"""
MCP Tools para Amazon RDS
Herramientas para gestión de bases de datos relacionales
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class RDSMCPTools:
    """Herramientas MCP para operaciones con Amazon RDS"""

    # Constantes para descripciones
    DESC_MAX_RECORDS = 'Número máximo de registros'
    DESC_DB_INSTANCE_ID = 'ID de la instancia RDS'
    DESC_DB_SNAPSHOT_ID = 'Identificador del snapshot'

    def __init__(self):
        self.rds_client = None

    def _get_client(self):
        """Obtiene el cliente RDS"""
        if self.rds_client is None:
            self.rds_client = get_aws_client('rds')
        return self.rds_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para RDS"""
        return [
            {
                'name': 'rds_describe_db_instances',
                'description': 'Lista todas las instancias de base de datos RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': 'ID específico de la instancia'},
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para las instancias',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_records': {'type': 'integer', 'description': self.DESC_MAX_RECORDS, 'default': 100}
                    }
                }
            },
            {
                'name': 'rds_describe_db_instance',
                'description': 'Obtiene detalles completos de una instancia RDS específica',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': 'ID de la instancia RDS'}
                    },
                    'required': ['db_instance_identifier']
                }
            },
            {
                'name': 'rds_create_db_instance',
                'description': 'Crea una nueva instancia de base de datos RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': 'Identificador único de la instancia'},
                        'db_instance_class': {'type': 'string', 'description': 'Clase de instancia (ej: db.t3.micro)'},
                        'engine': {'type': 'string', 'description': 'Motor de base de datos (mysql, postgresql, etc.)'},
                        'master_username': {'type': 'string', 'description': 'Nombre del usuario maestro'},
                        'master_user_password': {'type': 'string', 'description': 'Contraseña del usuario maestro'},
                        'allocated_storage': {'type': 'integer', 'description': 'Almacenamiento en GB', 'default': 20},
                        'db_name': {'type': 'string', 'description': 'Nombre de la base de datos'},
                        'vpc_security_group_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'IDs de security groups'},
                        'db_subnet_group_name': {'type': 'string', 'description': 'Nombre del subnet group'},
                        'publicly_accessible': {'type': 'boolean', 'description': 'Acceso público', 'default': False},
                        'multi_az': {'type': 'boolean', 'description': 'Multi-AZ', 'default': False},
                        'backup_retention_period': {'type': 'integer', 'description': 'Días de retención de backup', 'default': 7},
                        'tags': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Tags para la instancia'}
                    },
                    'required': ['db_instance_identifier', 'db_instance_class', 'engine', 'master_username', 'master_user_password']
                }
            },
            {
                'name': 'rds_start_db_instance',
                'description': 'Inicia una instancia RDS detenida',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': self.DESC_DB_INSTANCE_ID}
                    },
                    'required': ['db_instance_identifier']
                }
            },
            {
                'name': 'rds_stop_db_instance',
                'description': 'Detiene una instancia RDS en ejecución',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': self.DESC_DB_INSTANCE_ID}
                    },
                    'required': ['db_instance_identifier']
                }
            },
            {
                'name': 'rds_reboot_db_instance',
                'description': 'Reinicia una instancia RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': self.DESC_DB_INSTANCE_ID},
                        'force_failover': {'type': 'boolean', 'description': 'Forzar failover en Multi-AZ', 'default': False}
                    },
                    'required': ['db_instance_identifier']
                }
            },
            {
                'name': 'rds_delete_db_instance',
                'description': 'Elimina una instancia RDS (operación destructiva)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': self.DESC_DB_INSTANCE_ID},
                        'skip_final_snapshot': {'type': 'boolean', 'description': 'Omitir snapshot final', 'default': False},
                        'final_db_snapshot_identifier': {'type': 'string', 'description': 'Nombre del snapshot final'},
                        'delete_automated_backups': {'type': 'boolean', 'description': 'Eliminar backups automatizados', 'default': True}
                    },
                    'required': ['db_instance_identifier']
                }
            },
            {
                'name': 'rds_describe_db_snapshots',
                'description': 'Lista snapshots de base de datos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_instance_identifier': {'type': 'string', 'description': 'ID de la instancia'},
                        'snapshot_type': {'type': 'string', 'description': 'Tipo de snapshot (manual, automated)'},
                        'max_records': {'type': 'integer', 'description': self.DESC_MAX_RECORDS, 'default': 100}
                    }
                }
            },
            {
                'name': 'rds_create_db_snapshot',
                'description': 'Crea un snapshot manual de una instancia RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_snapshot_identifier': {'type': 'string', 'description': self.DESC_DB_SNAPSHOT_ID},
                        'db_instance_identifier': {'type': 'string', 'description': 'ID de la instancia'}
                    },
                    'required': ['db_snapshot_identifier', 'db_instance_identifier']
                }
            },
            {
                'name': 'rds_delete_db_snapshot',
                'description': 'Elimina un snapshot de base de datos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_snapshot_identifier': {'type': 'string', 'description': 'Identificador del snapshot'}
                    },
                    'required': ['db_snapshot_identifier']
                }
            },
            {
                'name': 'rds_describe_db_subnet_groups',
                'description': 'Lista grupos de subnets de RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_subnet_group_name': {'type': 'string', 'description': 'Nombre específico del grupo'},
                        'max_records': {'type': 'integer', 'description': self.DESC_MAX_RECORDS, 'default': 100}
                    }
                }
            },
            {
                'name': 'rds_describe_db_parameter_groups',
                'description': 'Lista grupos de parámetros de RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'db_parameter_group_name': {'type': 'string', 'description': 'Nombre específico del grupo'},
                        'max_records': {'type': 'integer', 'description': self.DESC_MAX_RECORDS, 'default': 100}
                    }
                }
            },
            {
                'name': 'rds_describe_reserved_db_instances',
                'description': 'Lista instancias reservadas de RDS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'reserved_db_instance_id': {'type': 'string', 'description': 'ID específico de la reserva'},
                        'max_records': {'type': 'integer', 'description': self.DESC_MAX_RECORDS, 'default': 100}
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de RDS"""
        try:
            if tool_name == 'rds_describe_db_instances':
                return self._describe_db_instances(**parameters)
            elif tool_name == 'rds_describe_db_instance':
                return self._describe_db_instance(**parameters)
            elif tool_name == 'rds_create_db_instance':
                return self._create_db_instance(**parameters)
            elif tool_name == 'rds_start_db_instance':
                return self._start_db_instance(**parameters)
            elif tool_name == 'rds_stop_db_instance':
                return self._stop_db_instance(**parameters)
            elif tool_name == 'rds_reboot_db_instance':
                return self._reboot_db_instance(**parameters)
            elif tool_name == 'rds_delete_db_instance':
                return self._delete_db_instance(**parameters)
            elif tool_name == 'rds_describe_db_snapshots':
                return self._describe_db_snapshots(**parameters)
            elif tool_name == 'rds_create_db_snapshot':
                return self._create_db_snapshot(**parameters)
            elif tool_name == 'rds_delete_db_snapshot':
                return self._delete_db_snapshot(**parameters)
            elif tool_name == 'rds_describe_db_subnet_groups':
                return self._describe_db_subnet_groups(**parameters)
            elif tool_name == 'rds_describe_db_parameter_groups':
                return self._describe_db_parameter_groups(**parameters)
            elif tool_name == 'rds_describe_reserved_db_instances':
                return self._describe_reserved_db_instances(**parameters)
            else:
                return {'error': f'Herramienta RDS no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta RDS {tool_name}: {str(e)}'}

    def _describe_db_instances(self, **kwargs) -> Dict[str, Any]:
        """Lista instancias de base de datos"""
        client = self._get_client()

        rds_params = {
            'MaxRecords': kwargs.get('max_records', 100)
        }

        if kwargs.get('db_instance_identifier'):
            rds_kwargs.get('DBInstanceIdentifier') = kwargs.get('db_instance_identifier')

        if kwargs.get('filters'):
            rds_kwargs.get('Filters') = kwargs.get('filters')

        response = client.describe_db_instances(**rds_params)

        instances = []
        for db in response['DBInstances']:
            instances.append({
                'db_instance_identifier': db['DBInstanceIdentifier'],
                'db_instance_class': db['DBInstanceClass'],
                'engine': db['Engine'],
                'engine_version': db['EngineVersion'],
                'db_instance_status': db['DBInstanceStatus'],
                'master_username': db.get('MasterUsername'),
                'allocated_storage': db.get('AllocatedStorage'),
                'endpoint': {
                    'address': db.get('Endpoint', {}).get('Address'),
                    'port': db.get('Endpoint', {}).get('Port')
                },
                'availability_zone': db.get('AvailabilityZone'),
                'backup_retention_period': db.get('BackupRetentionPeriod'),
                'multi_az': db.get('MultiAZ', False),
                'publicly_accessible': db.get('PubliclyAccessible', False),
                'storage_encrypted': db.get('StorageEncrypted', False),
                'instance_create_time': db.get('InstanceCreateTime').strftime('%Y-%m-%d %H:%M:%S') if db.get('InstanceCreateTime') else None,
                'tags': {tag['Key']: tag['Value'] for tag in db.get('TagList', [])}
            })

        return {
            'db_instances': instances,
            'total_count': len(instances)
        }

    def _describe_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Describe una instancia específica"""
        client = self._get_client()

        response = client.describe_db_instances(
            DBInstanceIdentifier=kwargs.get('db_instance_identifier')
        )

        db = response['DBInstances'][0]

        return {
            'db_instance': {
                'db_instance_identifier': db['DBInstanceIdentifier'],
                'db_instance_class': db['DBInstanceClass'],
                'engine': db['Engine'],
                'engine_version': db['EngineVersion'],
                'db_instance_status': db['DBInstanceStatus'],
                'master_username': db.get('MasterUsername'),
                'allocated_storage': db.get('AllocatedStorage'),
                'endpoint': {
                    'address': db.get('Endpoint', {}).get('Address'),
                    'port': db.get('Endpoint', {}).get('Port')
                },
                'availability_zone': db.get('AvailabilityZone'),
                'backup_retention_period': db.get('BackupRetentionPeriod'),
                'multi_az': db.get('MultiAZ', False),
                'publicly_accessible': db.get('PubliclyAccessible', False),
                'storage_encrypted': db.get('StorageEncrypted', False),
                'vpc_security_groups': db.get('VpcSecurityGroups', []),
                'db_subnet_group_name': db.get('DBSubnetGroupName'),
                'instance_create_time': db.get('InstanceCreateTime').strftime('%Y-%m-%d %H:%M:%S') if db.get('InstanceCreateTime') else None,
                'tags': {tag['Key']: tag['Value'] for tag in db.get('TagList', [])}
            }
        }

    def _create_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva instancia RDS"""
        client = self._get_client()

        rds_params = {
            'DBInstanceIdentifier': kwargs.get('db_instance_identifier'),
            'DBInstanceClass': kwargs.get('db_instance_class'),
            'Engine': kwargs.get('engine'),
            'MasterUsername': kwargs.get('master_username'),
            'MasterUserPassword': kwargs.get('master_user_password'),
            'AllocatedStorage': kwargs.get('allocated_storage', 20),
            'BackupRetentionPeriod': kwargs.get('backup_retention_period', 7),
            'MultiAZ': kwargs.get('multi_az', False),
            'PubliclyAccessible': kwargs.get('publicly_accessible', False)
        }

        if kwargs.get('db_name'):
            rds_kwargs.get('DBName') = kwargs.get('db_name')

        if kwargs.get('vpc_security_group_ids'):
            rds_kwargs.get('VpcSecurityGroupIds') = kwargs.get('vpc_security_group_ids')

        if kwargs.get('db_subnet_group_name'):
            rds_kwargs.get('DBSubnetGroupName') = kwargs.get('db_subnet_group_name')

        if kwargs.get('tags'):
            rds_kwargs.get('Tags') = kwargs.get('tags')

        client.create_db_instance(**rds_params)

        return {
            'message': f'Instancia RDS {kwargs.get('db_instance_identifier')} está siendo creada',
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'db_instance_status': 'creating'
        }

    def _start_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Inicia una instancia RDS"""
        client = self._get_client()

        client.start_db_instance(
            DBInstanceIdentifier=kwargs.get('db_instance_identifier')
        )

        return {
            'message': f'Instancia RDS {kwargs.get('db_instance_identifier')} iniciándose',
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'db_instance_status': 'starting'
        }

    def _stop_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Detiene una instancia RDS"""
        client = self._get_client()

        client.stop_db_instance(
            DBInstanceIdentifier=kwargs.get('db_instance_identifier')
        )

        return {
            'message': f'Instancia RDS {kwargs.get('db_instance_identifier')} deteniéndose',
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'db_instance_status': 'stopping'
        }

    def _reboot_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Reinicia una instancia RDS"""
        client = self._get_client()

        rds_params = {
            'DBInstanceIdentifier': kwargs.get('db_instance_identifier')
        }

        if kwargs.get('force_failover'):
            rds_kwargs.get('ForceFailover') = kwargs.get('force_failover')

        client.reboot_db_instance(**rds_params)

        return {
            'message': f'Instancia RDS {kwargs.get('db_instance_identifier')} reiniciándose',
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'db_instance_status': 'rebooting'
        }

    def _delete_db_instance(self, **kwargs) -> Dict[str, Any]:
        """Elimina una instancia RDS"""
        client = self._get_client()

        rds_params = {
            'DBInstanceIdentifier': kwargs.get('db_instance_identifier'),
            'SkipFinalSnapshot': kwargs.get('skip_final_snapshot', False),
            'DeleteAutomatedBackups': kwargs.get('delete_automated_backups', True)
        }

        if not kwargs.get('skip_final_snapshot', False) and kwargs.get('final_db_snapshot_identifier'):
            rds_kwargs.get('FinalDBSnapshotIdentifier') = kwargs.get('final_db_snapshot_identifier')

        client.delete_db_instance(**rds_params)

        return {
            'message': f'Instancia RDS {kwargs.get('db_instance_identifier')} eliminándose',
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'db_instance_status': 'deleting'
        }

    def _describe_db_snapshots(self, **kwargs) -> Dict[str, Any]:
        """Lista snapshots de base de datos"""
        client = self._get_client()

        rds_params = {
            'MaxRecords': kwargs.get('max_records', 100)
        }

        if kwargs.get('db_instance_identifier'):
            rds_kwargs.get('DBInstanceIdentifier') = kwargs.get('db_instance_identifier')

        if kwargs.get('snapshot_type'):
            rds_kwargs.get('SnapshotType') = kwargs.get('snapshot_type')

        response = client.describe_db_snapshots(**rds_params)

        snapshots = []
        for snap in response['DBSnapshots']:
            snapshots.append({
                'db_snapshot_identifier': snap['DBSnapshotIdentifier'],
                'db_instance_identifier': snap['DBInstanceIdentifier'],
                'snapshot_create_time': snap['SnapshotCreateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'engine': snap['Engine'],
                'allocated_storage': snap['AllocatedStorage'],
                'status': snap['Status'],
                'snapshot_type': snap['SnapshotType'],
                'encrypted': snap.get('Encrypted', False),
                'kms_key_id': snap.get('KmsKeyId'),
                'tags': {tag['Key']: tag['Value'] for tag in snap.get('TagList', [])}
            })

        return {
            'db_snapshots': snapshots,
            'total_count': len(snapshots)
        }

    def _create_db_snapshot(self, **kwargs) -> Dict[str, Any]:
        """Crea un snapshot de base de datos"""
        client = self._get_client()

        client.create_db_snapshot(
            DBSnapshotIdentifier=kwargs.get('db_snapshot_identifier'),
            DBInstanceIdentifier=kwargs.get('db_instance_identifier')
        )

        return {
            'message': f'Snapshot {kwargs.get('db_snapshot_identifier')} está siendo creado',
            'db_snapshot_identifier': kwargs.get('db_snapshot_identifier'),
            'db_instance_identifier': kwargs.get('db_instance_identifier'),
            'status': 'creating'
        }

    def _delete_db_snapshot(self, **kwargs) -> Dict[str, Any]:
        """Elimina un snapshot de base de datos"""
        client = self._get_client()

        client.delete_db_snapshot(
            DBSnapshotIdentifier=kwargs.get('db_snapshot_identifier')
        )

        return {
            'message': f'Snapshot {kwargs.get('db_snapshot_identifier')} eliminado',
            'db_snapshot_identifier': kwargs.get('db_snapshot_identifier')
        }

    def _describe_db_subnet_groups(self, **kwargs) -> Dict[str, Any]:
        """Lista grupos de subnets de RDS"""
        client = self._get_client()

        rds_params = {
            'MaxRecords': kwargs.get('max_records', 100)
        }

        if kwargs.get('db_subnet_group_name'):
            rds_kwargs.get('DBSubnetGroupName') = kwargs.get('db_subnet_group_name')

        response = client.describe_db_subnet_groups(**rds_params)

        subnet_groups = []
        for sg in response['DBSubnetGroups']:
            subnet_groups.append({
                'db_subnet_group_name': sg['DBSubnetGroupName'],
                'db_subnet_group_description': sg['DBSubnetGroupDescription'],
                'vpc_id': sg['VpcId'],
                'subnet_group_status': sg['SubnetGroupStatus'],
                'subnets': [{
                    'subnet_identifier': subnet['SubnetIdentifier'],
                    'subnet_availability_zone': {
                        'name': subnet['SubnetAvailabilityZone']['Name']
                    }
                } for subnet in sg['Subnets']],
                'tags': {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])}
            })

        return {
            'db_subnet_groups': subnet_groups,
            'total_count': len(subnet_groups)
        }

    def _describe_db_parameter_groups(self, **kwargs) -> Dict[str, Any]:
        """Lista grupos de parámetros de RDS"""
        client = self._get_client()

        rds_params = {
            'MaxRecords': kwargs.get('max_records', 100)
        }

        if kwargs.get('db_parameter_group_name'):
            rds_kwargs.get('DBParameterGroupName') = kwargs.get('db_parameter_group_name')

        response = client.describe_db_parameter_groups(**rds_params)

        parameter_groups = []
        for pg in response['DBParameterGroups']:
            parameter_groups.append({
                'db_parameter_group_name': pg['DBParameterGroupName'],
                'db_parameter_group_family': pg['DBParameterGroupFamily'],
                'description': pg['Description'],
                'db_parameter_group_arn': pg['DBParameterGroupArn'],
                'tags': {tag['Key']: tag['Value'] for tag in pg.get('Tags', [])}
            })

        return {
            'db_parameter_groups': parameter_groups,
            'total_count': len(parameter_groups)
        }

    def _describe_reserved_db_instances(self, **kwargs) -> Dict[str, Any]:
        """Lista instancias reservadas de RDS"""
        client = self._get_client()

        rds_params = {
            'MaxRecords': kwargs.get('max_records', 100)
        }

        if kwargs.get('reserved_db_instance_id'):
            rds_kwargs.get('ReservedDBInstanceId') = kwargs.get('reserved_db_instance_id')

        response = client.describe_reserved_db_instances(**rds_params)

        reserved_instances = []
        for ri in response['ReservedDBInstances']:
            reserved_instances.append({
                'reserved_db_instance_id': ri['ReservedDBInstanceId'],
                'db_instance_class': ri['DBInstanceClass'],
                'state': ri['State'],
                'multi_az': ri['MultiAZ'],
                'product_description': ri['ProductDescription'],
                'reserved_db_instances_offering_id': ri['ReservedDBInstancesOfferingId'],
                'usage_price': ri.get('UsagePrice'),
                'fixed_price': ri.get('FixedPrice'),
                'duration': ri['Duration'],
                'start_time': ri['StartTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'offering_type': ri['OfferingType'],
                'recurring_charges': ri.get('RecurringCharges', [])
            })

        return {
            'reserved_db_instances': reserved_instances,
            'total_count': len(reserved_instances)
        }