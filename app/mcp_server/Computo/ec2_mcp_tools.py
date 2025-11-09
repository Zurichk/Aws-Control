"""
MCP Tools para Amazon EC2
Herramientas para gestión de instancias EC2, AMIs, snapshots, security groups, etc.
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class EC2MCPTools:
    """Herramientas MCP para Amazon EC2"""

    def __init__(self):
        self.ec2 = None

    def _get_ec2_client(self):
        """Obtiene el cliente EC2"""
        if self.ec2 is None:
            self.ec2 = get_aws_client('ec2')
        return self.ec2

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para EC2"""
        return [
            {
                'name': 'ec2_list_instances',
                'description': 'Lista todas las instancias EC2 con filtros opcionales',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filters': {
                            'type': 'array',
                            'description': 'Lista de filtros para las instancias',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados'}
                    }
                },
                'function': self.list_instances
            },
            {
                'name': 'ec2_describe_instance',
                'description': 'Obtiene detalles completos de una instancia EC2 específica',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'instance_id': {'type': 'string', 'description': 'ID de la instancia EC2'}
                    },
                    'required': ['instance_id']
                },
                'function': self.describe_instance
            },
            {
                'name': 'ec2_start_instance',
                'description': 'Inicia una instancia EC2 detenida',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'instance_id': {'type': 'string', 'description': 'ID de la instancia EC2'}
                    },
                    'required': ['instance_id']
                },
                'function': self.start_instance
            },
            {
                'name': 'ec2_stop_instance',
                'description': 'Detiene una instancia EC2 en ejecución',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'instance_id': {'type': 'string', 'description': 'ID de la instancia EC2'}
                    },
                    'required': ['instance_id']
                },
                'function': self.stop_instance
            },
            {
                'name': 'ec2_terminate_instance',
                'description': 'Termina una instancia EC2 (operación destructiva)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'instance_id': {'type': 'string', 'description': 'ID de la instancia EC2'}
                    },
                    'required': ['instance_id']
                },
                'function': self.terminate_instance
            },
            {
                'name': 'ec2_create_instance',
                'description': 'Crea una nueva instancia EC2',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'image_id': {'type': 'string', 'description': 'ID de la AMI'},
                        'instance_type': {'type': 'string', 'description': 'Tipo de instancia (ej: t2.micro)'},
                        'min_count': {'type': 'integer', 'description': 'Número mínimo de instancias', 'default': 1},
                        'max_count': {'type': 'integer', 'description': 'Número máximo de instancias', 'default': 1},
                        'key_name': {'type': 'string', 'description': 'Nombre del key pair'},
                        'security_group_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'IDs de security groups'},
                        'subnet_id': {'type': 'string', 'description': 'ID de la subnet'},
                        'user_data': {'type': 'string', 'description': 'Script de inicialización'},
                        'tags': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Tags para la instancia'}
                    },
                    'required': ['image_id', 'instance_type']
                },
                'function': self.create_instance
            },
            {
                'name': 'ec2_list_amis',
                'description': 'Lista AMIs (Amazon Machine Images) disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'owners': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Propietarios de las AMIs'},
                        'filters': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Filtros para las AMIs'},
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados'}
                    }
                },
                'function': self.list_amis
            },
            {
                'name': 'ec2_create_snapshot',
                'description': 'Crea un snapshot de un volumen EBS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'volume_id': {'type': 'string', 'description': 'ID del volumen EBS'},
                        'description': {'type': 'string', 'description': 'Descripción del snapshot'},
                        'tags': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Tags para el snapshot'}
                    },
                    'required': ['volume_id']
                },
                'function': self.create_snapshot
            },
            {
                'name': 'ec2_list_snapshots',
                'description': 'Lista snapshots de EBS disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'owner_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'IDs de propietarios'},
                        'filters': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Filtros para snapshots'},
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados'}
                    }
                },
                'function': self.list_snapshots
            },
            {
                'name': 'ec2_list_security_groups',
                'description': 'Lista security groups disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'IDs de security groups'},
                        'group_names': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Nombres de security groups'},
                        'filters': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Filtros para security groups'}
                    }
                },
                'function': self.list_security_groups
            },
            {
                'name': 'ec2_create_security_group',
                'description': 'Crea un nuevo security group',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_name': {'type': 'string', 'description': 'Nombre del security group'},
                        'description': {'type': 'string', 'description': 'Descripción del security group'},
                        'vpc_id': {'type': 'string', 'description': 'ID de la VPC'}
                    },
                    'required': ['group_name', 'description']
                },
                'function': self.create_security_group
            },
            {
                'name': 'ec2_list_key_pairs',
                'description': 'Lista key pairs disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'key_names': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Nombres de key pairs'},
                        'filters': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Filtros para key pairs'}
                    }
                },
                'function': self.list_key_pairs
            },
            {
                'name': 'ec2_create_key_pair',
                'description': 'Crea un nuevo key pair',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'key_name': {'type': 'string', 'description': 'Nombre del key pair'},
                        'key_type': {'type': 'string', 'description': 'Tipo de key (rsa, ed25519)', 'default': 'rsa'},
                        'key_format': {'type': 'string', 'description': 'Formato de la key (pem, ppk)', 'default': 'pem'}
                    },
                    'required': ['key_name']
                },
                'function': self.create_key_pair
            }
        ]

    def list_instances(self, filters: Optional[List[Dict]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        """Lista instancias EC2 con filtros opcionales"""
        try:
            ec2 = self._get_ec2_client()
            params = {}
            if filters:
                params['Filters'] = filters
            if max_results:
                params['MaxResults'] = max_results

            response = ec2.describe_instances(**params)

            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'state_code': instance['State']['Code'],
                        'public_ip': instance.get('PublicIpAddress'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'platform': instance.get('Platform', 'linux'),
                        'architecture': instance.get('Architecture', 'x86_64'),
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                        'security_groups': [{'id': sg['GroupId'], 'name': sg['GroupName']} for sg in instance.get('SecurityGroups', [])],
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId')
                    })

            return {
                'success': True,
                'instances': instances,
                'total_count': len(instances)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando instancias EC2: {str(e)}'
            }

    def describe_instance(self, instance_id: str) -> Dict[str, Any]:
        """Obtiene detalles completos de una instancia EC2"""
        try:
            ec2 = self._get_ec2_client()
            response = ec2.describe_instances(InstanceIds=[instance_id])

            if not response['Reservations']:
                return {
                    'success': False,
                    'error': f'Instancia {instance_id} no encontrada'
                }

            instance = response['Reservations'][0]['Instances'][0]

            # Obtener información adicional
            volumes = []
            for bdm in instance.get('BlockDeviceMappings', []):
                if 'Ebs' in bdm:
                    volumes.append({
                        'device_name': bdm['DeviceName'],
                        'volume_id': bdm['Ebs']['VolumeId'],
                        'status': bdm['Ebs']['Status'],
                        'delete_on_termination': bdm['Ebs']['DeleteOnTermination']
                    })

            return {
                'success': True,
                'instance': {
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'state_code': instance['State']['Code'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'private_ip': instance.get('PrivateIpAddress'),
                    'public_dns': instance.get('PublicDnsName'),
                    'private_dns': instance.get('PrivateDnsName'),
                    'launch_time': instance['LaunchTime'].isoformat(),
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'platform': instance.get('Platform', 'linux'),
                    'architecture': instance.get('Architecture', 'x86_64'),
                    'image_id': instance['ImageId'],
                    'key_name': instance.get('KeyName'),
                    'monitoring': instance.get('Monitoring', {}).get('State', 'disabled'),
                    'ebs_optimized': instance.get('EbsOptimized', False),
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                    'security_groups': [{'id': sg['GroupId'], 'name': sg['GroupName']} for sg in instance.get('SecurityGroups', [])],
                    'network_interfaces': len(instance.get('NetworkInterfaces', [])),
                    'volumes': volumes,
                    'vpc_id': instance.get('VpcId'),
                    'subnet_id': instance.get('SubnetId'),
                    'root_device_type': instance.get('RootDeviceType'),
                    'root_device_name': instance.get('RootDeviceName')
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error obteniendo detalles de instancia: {str(e)}'
            }

    def start_instance(self, instance_id: str) -> Dict[str, Any]:
        """Inicia una instancia EC2 detenida"""
        try:
            ec2 = self._get_ec2_client()
            response = ec2.start_instances(InstanceIds=[instance_id])

            return {
                'success': True,
                'instance_id': instance_id,
                'previous_state': response['StartingInstances'][0]['PreviousState']['Name'],
                'current_state': response['StartingInstances'][0]['CurrentState']['Name'],
                'message': f'Instancia {instance_id} iniciándose'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error iniciando instancia: {str(e)}'
            }

    def stop_instance(self, instance_id: str) -> Dict[str, Any]:
        """Detiene una instancia EC2 en ejecución"""
        try:
            ec2 = self._get_ec2_client()
            response = ec2.stop_instances(InstanceIds=[instance_id])

            return {
                'success': True,
                'instance_id': instance_id,
                'previous_state': response['StoppingInstances'][0]['PreviousState']['Name'],
                'current_state': response['StoppingInstances'][0]['CurrentState']['Name'],
                'message': f'Instancia {instance_id} deteniéndose'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error deteniendo instancia: {str(e)}'
            }

    def terminate_instance(self, instance_id: str) -> Dict[str, Any]:
        """Termina una instancia EC2"""
        try:
            ec2 = self._get_ec2_client()
            response = ec2.terminate_instances(InstanceIds=[instance_id])

            return {
                'success': True,
                'instance_id': instance_id,
                'previous_state': response['TerminatingInstances'][0]['PreviousState']['Name'],
                'current_state': response['TerminatingInstances'][0]['CurrentState']['Name'],
                'message': f'Instancia {instance_id} terminándose'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error terminando instancia: {str(e)}'
            }

    def create_instance(self, image_id: str, instance_type: str, **kwargs) -> Dict[str, Any]:
        """Crea una nueva instancia EC2"""
        try:
            ec2 = self._get_ec2_client()

            params = {
                'ImageId': image_id,
                'InstanceType': instance_type,
                'MinCount': kwargs.get('min_count', 1),
                'MaxCount': kwargs.get('max_count', 1)
            }

            if 'key_name' in kwargs:
                params['KeyName'] = kwargs['key_name']
            if 'security_group_ids' in kwargs:
                params['SecurityGroupIds'] = kwargs['security_group_ids']
            if 'subnet_id' in kwargs:
                params['SubnetId'] = kwargs['subnet_id']
            if 'user_data' in kwargs:
                params['UserData'] = kwargs['user_data']
            if 'tags' in kwargs:
                params['TagSpecifications'] = [{
                    'ResourceType': 'instance',
                    'Tags': kwargs['tags']
                }]

            response = ec2.run_instances(**params)

            instances = []
            for instance in response['Instances']:
                instances.append({
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'private_ip': instance.get('PrivateIpAddress'),
                    'launch_time': instance['LaunchTime'].isoformat()
                })

            return {
                'success': True,
                'instances': instances,
                'message': f'{len(instances)} instancia(s) creada(s) exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando instancia: {str(e)}'
            }

    def list_amis(self, owners: Optional[List[str]] = None, filters: Optional[List[Dict]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        """Lista AMIs disponibles"""
        try:
            ec2 = self._get_ec2_client()
            params = {}

            if owners:
                params['Owners'] = owners
            if filters:
                params['Filters'] = filters
            if max_results:
                params['MaxResults'] = max_results

            response = ec2.describe_images(**params)

            amis = []
            for image in response['Images']:
                amis.append({
                    'image_id': image['ImageId'],
                    'name': image.get('Name', ''),
                    'description': image.get('Description', ''),
                    'state': image['State'],
                    'public': image.get('Public', False),
                    'architecture': image.get('Architecture', ''),
                    'platform': image.get('Platform', ''),
                    'root_device_type': image.get('RootDeviceType', ''),
                    'virtualization_type': image.get('VirtualizationType', ''),
                    'creation_date': image.get('CreationDate', ''),
                    'owner_id': image['OwnerId']
                })

            return {
                'success': True,
                'amis': amis,
                'total_count': len(amis)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando AMIs: {str(e)}'
            }

    def create_snapshot(self, volume_id: str, description: Optional[str] = None, tags: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Crea un snapshot de un volumen EBS"""
        try:
            ec2 = self._get_ec2_client()
            params = {'VolumeId': volume_id}

            if description:
                params['Description'] = description
            if tags:
                params['TagSpecifications'] = [{
                    'ResourceType': 'snapshot',
                    'Tags': tags
                }]

            response = ec2.create_snapshot(**params)

            return {
                'success': True,
                'snapshot_id': response['SnapshotId'],
                'volume_id': response['VolumeId'],
                'state': response['State'],
                'start_time': response['StartTime'].isoformat(),
                'message': f'Snapshot {response["SnapshotId"]} creado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando snapshot: {str(e)}'
            }

    def list_snapshots(self, owner_ids: Optional[List[str]] = None, filters: Optional[List[Dict]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        """Lista snapshots de EBS"""
        try:
            ec2 = self._get_ec2_client()
            params = {}

            if owner_ids:
                params['OwnerIds'] = owner_ids
            if filters:
                params['Filters'] = filters
            if max_results:
                params['MaxResults'] = max_results

            response = ec2.describe_snapshots(**params)

            snapshots = []
            for snapshot in response['Snapshots']:
                snapshots.append({
                    'snapshot_id': snapshot['SnapshotId'],
                    'volume_id': snapshot['VolumeId'],
                    'volume_size': snapshot['VolumeSize'],
                    'state': snapshot['State'],
                    'start_time': snapshot['StartTime'].isoformat(),
                    'description': snapshot.get('Description', ''),
                    'progress': snapshot.get('Progress', ''),
                    'owner_id': snapshot['OwnerId'],
                    'encrypted': snapshot.get('Encrypted', False)
                })

            return {
                'success': True,
                'snapshots': snapshots,
                'total_count': len(snapshots)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando snapshots: {str(e)}'
            }

    def list_security_groups(self, group_ids: Optional[List[str]] = None, group_names: Optional[List[str]] = None, filters: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Lista security groups"""
        try:
            ec2 = self._get_ec2_client()
            params = {}

            if group_ids:
                params['GroupIds'] = group_ids
            if group_names:
                params['GroupNames'] = group_names
            if filters:
                params['Filters'] = filters

            response = ec2.describe_security_groups(**params)

            security_groups = []
            for sg in response['SecurityGroups']:
                security_groups.append({
                    'group_id': sg['GroupId'],
                    'group_name': sg['GroupName'],
                    'description': sg.get('Description', ''),
                    'vpc_id': sg.get('VpcId'),
                    'owner_id': sg['OwnerId'],
                    'ip_permissions': len(sg.get('IpPermissions', [])),
                    'ip_permissions_egress': len(sg.get('IpPermissionsEgress', [])),
                    'tags': {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])}
                })

            return {
                'success': True,
                'security_groups': security_groups,
                'total_count': len(security_groups)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando security groups: {str(e)}'
            }

    def create_security_group(self, group_name: str, description: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Crea un nuevo security group"""
        try:
            ec2 = self._get_ec2_client()
            params = {
                'GroupName': group_name,
                'Description': description
            }

            if vpc_id:
                params['VpcId'] = vpc_id

            response = ec2.create_security_group(**params)

            return {
                'success': True,
                'group_id': response['GroupId'],
                'message': f'Security group {group_name} creado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando security group: {str(e)}'
            }

    def list_key_pairs(self, key_names: Optional[List[str]] = None, filters: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Lista key pairs"""
        try:
            ec2 = self._get_ec2_client()
            params = {}

            if key_names:
                params['KeyNames'] = key_names
            if filters:
                params['Filters'] = filters

            response = ec2.describe_key_pairs(**params)

            key_pairs = []
            for kp in response['KeyPairs']:
                key_pairs.append({
                    'key_name': kp['KeyName'],
                    'key_fingerprint': kp['KeyFingerprint'],
                    'key_type': kp.get('KeyType', 'rsa'),
                    'tags': {tag['Key']: tag['Value'] for tag in kp.get('Tags', [])}
                })

            return {
                'success': True,
                'key_pairs': key_pairs,
                'total_count': len(key_pairs)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando key pairs: {str(e)}'
            }

    def create_key_pair(self, key_name: str, key_type: str = 'rsa', key_format: str = 'pem') -> Dict[str, Any]:
        """Crea un nuevo key pair"""
        try:
            ec2 = self._get_ec2_client()
            params = {
                'KeyName': key_name,
                'KeyType': key_type,
                'KeyFormat': key_format
            }

            response = ec2.create_key_pair(**params)

            return {
                'success': True,
                'key_name': response['KeyName'],
                'key_fingerprint': response['KeyFingerprint'],
                'key_material': response.get('KeyMaterial', ''),  # Solo presente si se genera nueva key
                'key_type': response.get('KeyType', key_type),
                'key_format': response.get('KeyFormat', key_format),
                'message': f'Key pair {key_name} creado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando key pair: {str(e)}'
            }

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica"""
        try:
            # Buscar la herramienta por nombre
            for tool in self.get_tools():
                if tool['name'] == tool_name:
                    return tool['function'](**parameters)

            return {
                'success': False,
                'error': f'Herramienta {tool_name} no encontrada'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error ejecutando herramienta {tool_name}: {str(e)}'
            }