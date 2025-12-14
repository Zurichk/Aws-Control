"""
MCP Tools para Amazon VPC
Herramientas para gestión de redes virtuales y componentes de red
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class VPCMCPTools:
    """Herramientas MCP para operaciones con Amazon VPC"""

    # Constantes para descripciones
    DESC_VPC_ID = 'ID de la VPC'
    DESC_SUBNET_ID = 'ID de la subnet'
    DESC_SG_ID = 'ID del security group'
    DESC_RT_ID = 'ID de la route table'
    DESC_IGW_ID = 'ID del internet gateway'
    DESC_NAT_ID = 'ID del NAT gateway'
    DESC_VPC_NAME = 'Nombre de la VPC'
    DESC_CIDR_BLOCK = 'Bloque CIDR (ej: 10.0.0.0/16)'

    def __init__(self):
        self.ec2_client = None

    def _get_client(self):
        """Obtiene el cliente EC2 (que incluye VPC)"""
        if self.ec2_client is None:
            self.ec2_client = get_aws_client('ec2')
        return self.ec2_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para VPC"""
        return [
            {
                'name': 'vpc_describe_vpcs',
                'description': 'Lista todas las VPCs en la cuenta',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'vpc_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de VPCs a describir',
                            'items': {'type': 'string'}
                        },
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para las VPCs',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_vpcs
            },
            {
                'name': 'vpc_create_vpc',
                'description': 'Crea una nueva VPC',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'cidr_block': {'type': 'string', 'description': self.DESC_CIDR_BLOCK},
                        'amazon_provided_ipv6_cidr_block': {'type': 'boolean', 'description': 'Habilitar IPv6 proporcionado por Amazon', 'default': False},
                        'instance_tenancy': {'type': 'string', 'description': 'Tenancy de instancias', 'enum': ['default', 'dedicated'], 'default': 'default'},
                        'tags': {'type': 'array', 'description': 'Tags para la VPC', 'items': {'type': 'object'}}
                    },
                    'required': ['cidr_block']
                },
                'function': self._create_vpc
            },
            {
                'name': 'vpc_delete_vpc',
                'description': 'Elimina una VPC (debe estar vacía)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID}
                    },
                    'required': ['vpc_id']
                },
                'function': self._delete_vpc
            },
            {
                'name': 'vpc_describe_subnets',
                'description': 'Lista subnets en la VPC',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'subnet_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de subnets',
                            'items': {'type': 'string'}
                        },
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID},
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para las subnets',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_subnets
            },
            {
                'name': 'vpc_create_subnet',
                'description': 'Crea una nueva subnet en una VPC',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID},
                        'cidr_block': {'type': 'string', 'description': self.DESC_CIDR_BLOCK},
                        'availability_zone': {'type': 'string', 'description': 'Zona de disponibilidad'},
                        'availability_zone_id': {'type': 'string', 'description': 'ID de zona de disponibilidad'},
                        'ipv6_cidr_block': {'type': 'string', 'description': 'Bloque CIDR IPv6'},
                        'tags': {'type': 'array', 'description': 'Tags para la subnet', 'items': {'type': 'object'}}
                    },
                    'required': ['vpc_id', 'cidr_block']
                },
                'function': self._create_subnet
            },
            {
                'name': 'vpc_delete_subnet',
                'description': 'Elimina una subnet',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'subnet_id': {'type': 'string', 'description': self.DESC_SUBNET_ID}
                    },
                    'required': ['subnet_id']
                },
                'function': self._delete_subnet
            },
            {
                'name': 'vpc_describe_security_groups',
                'description': 'Lista security groups',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de security groups',
                            'items': {'type': 'string'}
                        },
                        'group_names': {
                            'type': 'array',
                            'description': 'Nombres de security groups',
                            'items': {'type': 'string'}
                        },
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para los security groups',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_security_groups
            },
            {
                'name': 'vpc_create_security_group',
                'description': 'Crea un nuevo security group',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_name': {'type': 'string', 'description': 'Nombre del security group'},
                        'description': {'type': 'string', 'description': 'Descripción del security group'},
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID},
                        'tags': {'type': 'array', 'description': 'Tags para el security group', 'items': {'type': 'object'}}
                    },
                    'required': ['group_name', 'description']
                },
                'function': self._create_security_group
            },
            {
                'name': 'vpc_authorize_security_group_ingress',
                'description': 'Agrega reglas de entrada a un security group',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_id': {
                            'type': 'string', 
                            'description': self.DESC_SG_ID
                        },
                        'ip_permissions': {
                            'type': 'array',
                            'description': 'Lista de permisos IP. Ejemplo: [{"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}]',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'IpProtocol': {
                                        'type': 'string',
                                        'description': 'Protocolo (tcp, udp, icmp o -1 para todos)'
                                    },
                                    'FromPort': {
                                        'type': 'integer',
                                        'description': 'Puerto de inicio (ej: 80 para HTTP)'
                                    },
                                    'ToPort': {
                                        'type': 'integer',
                                        'description': 'Puerto final (ej: 80 para HTTP)'
                                    },
                                    'IpRanges': {
                                        'type': 'array',
                                        'description': 'Rangos IP IPv4',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'CidrIp': {
                                                    'type': 'string',
                                                    'description': 'CIDR IPv4 (ej: 0.0.0.0/0)'
                                                },
                                                'Description': {
                                                    'type': 'string',
                                                    'description': 'Descripción opcional'
                                                }
                                            },
                                            'required': ['CidrIp']
                                        }
                                    }
                                },
                                'required': ['IpProtocol', 'IpRanges']
                            }
                        }
                    },
                    'required': ['group_id', 'ip_permissions']
                },
                'function': self.authorize_security_group_ingress
            },
            {
                'name': 'vpc_add_common_security_rules',
                'description': 'Agrega reglas comunes de entrada a un security group (HTTP, HTTPS, SSH, RDP, etc.)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_id': {'type': 'string', 'description': self.DESC_SG_ID},
                        'rules': {
                            'type': 'array',
                            'description': 'Lista de tipos de reglas a agregar: http, https, ssh, rdp, mysql, postgres, all-traffic',
                            'items': {'type': 'string'}
                        },
                        'cidr': {
                            'type': 'string', 
                            'description': 'CIDR para las reglas (por defecto 0.0.0.0/0 para acceso desde cualquier lugar)',
                            'default': '0.0.0.0/0'
                        }
                    },
                    'required': ['group_id', 'rules']
                },
                'function': self.add_common_security_rules
            },
            {
                'name': 'vpc_describe_route_tables',
                'description': 'Lista route tables',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'route_table_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de route tables',
                            'items': {'type': 'string'}
                        },
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID},
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para las route tables',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_route_tables
            },
            {
                'name': 'vpc_describe_internet_gateways',
                'description': 'Lista internet gateways',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'internet_gateway_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de internet gateways',
                            'items': {'type': 'string'}
                        },
                        'filters': {
                            'type': 'array',
                            'description': 'Filtros para los internet gateways',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_internet_gateways
            },
            {
                'name': 'vpc_create_internet_gateway',
                'description': 'Crea un nuevo internet gateway',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'tags': {'type': 'array', 'description': 'Tags para el internet gateway', 'items': {'type': 'object'}}
                    }
                },
                'function': self._create_internet_gateway
            },
            {
                'name': 'vpc_attach_internet_gateway',
                'description': 'Asocia un internet gateway a una VPC',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'internet_gateway_id': {'type': 'string', 'description': self.DESC_IGW_ID},
                        'vpc_id': {'type': 'string', 'description': self.DESC_VPC_ID}
                    },
                    'required': ['internet_gateway_id', 'vpc_id']
                },
                'function': self._attach_internet_gateway
            },
            {
                'name': 'vpc_describe_nat_gateways',
                'description': 'Lista NAT gateways',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'nat_gateway_ids': {
                            'type': 'array',
                            'description': 'IDs específicos de NAT gateways',
                            'items': {'type': 'string'}
                        },
                        'filter': {
                            'type': 'array',
                            'description': 'Filtros para los NAT gateways',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'Name': {'type': 'string'},
                                    'Values': {'type': 'array', 'items': {'type': 'string'}}
                                }
                            }
                        },
                        'max_results': {'type': 'integer', 'description': 'Número máximo de resultados', 'default': 100}
                    }
                },
                'function': self._describe_nat_gateways
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de VPC"""
        try:
            if tool_name == 'vpc_describe_vpcs':
                return self._describe_vpcs(parameters)
            elif tool_name == 'vpc_create_vpc':
                return self._create_vpc(parameters)
            elif tool_name == 'vpc_delete_vpc':
                return self._delete_vpc(parameters)
            elif tool_name == 'vpc_describe_subnets':
                return self._describe_subnets(parameters)
            elif tool_name == 'vpc_create_subnet':
                return self._create_subnet(parameters)
            elif tool_name == 'vpc_delete_subnet':
                return self._delete_subnet(parameters)
            elif tool_name == 'vpc_describe_security_groups':
                return self._describe_security_groups(parameters)
            elif tool_name == 'vpc_create_security_group':
                return self._create_security_group(parameters)
            elif tool_name == 'vpc_authorize_security_group_ingress':
                return self._authorize_security_group_ingress(parameters)
            elif tool_name == 'vpc_add_common_security_rules':
                return self.add_common_security_rules(**parameters)
            elif tool_name == 'vpc_describe_route_tables':
                return self._describe_route_tables(parameters)
            elif tool_name == 'vpc_describe_internet_gateways':
                return self._describe_internet_gateways(parameters)
            elif tool_name == 'vpc_create_internet_gateway':
                return self._create_internet_gateway(parameters)
            elif tool_name == 'vpc_attach_internet_gateway':
                return self._attach_internet_gateway(parameters)
            elif tool_name == 'vpc_describe_nat_gateways':
                return self._describe_nat_gateways(parameters)
            else:
                return {'error': f'Herramienta VPC no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta VPC {tool_name}: {str(e)}'}

    def _describe_vpcs(self, **kwargs) -> Dict[str, Any]:
        """Lista VPCs"""
        client = self._get_client()

        vpc_params = {}
        if 'vpc_ids' in kwargs:
            vpc_params['VpcIds'] = kwargs['vpc_ids']
        if 'filters' in kwargs:
            vpc_params['Filters'] = kwargs['filters']
        if 'max_results' in kwargs:
            vpc_params['MaxResults'] = kwargs['max_results']

        response = client.describe_vpcs(**vpc_params)

        vpcs = []
        for vpc in response['Vpcs']:
            vpcs.append({
                'vpc_id': vpc['VpcId'],
                'state': vpc['State'],
                'cidr_block': vpc.get('CidrBlock'),
                'cidr_block_association_set': vpc.get('CidrBlockAssociationSet', []),
                'ipv6_cidr_block_association_set': vpc.get('Ipv6CidrBlockAssociationSet', []),
                'dhcp_options_id': vpc.get('DhcpOptionsId'),
                'instance_tenancy': vpc.get('InstanceTenancy'),
                'is_default': vpc.get('IsDefault', False),
                'tags': {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
            })

        return {
            'vpcs': vpcs,
            'total_count': len(vpcs)
        }

    def _create_vpc(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva VPC"""
        client = self._get_client()

        vpc_params = {
            'CidrBlock': kwargs['cidr_block']
        }

        if 'amazon_provided_ipv6_cidr_block' in kwargs:
            vpc_params['AmazonProvidedIpv6CidrBlock'] = kwargs['amazon_provided_ipv6_cidr_block']
        if 'instance_tenancy' in kwargs:
            vpc_params['InstanceTenancy'] = kwargs['instance_tenancy']

        response = client.create_vpc(**vpc_params)

        vpc_id = response['Vpc']['VpcId']

        # Agregar tags si se proporcionaron
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            # Validar que los tags tengan el formato correcto
            valid_tags = []
            for tag in kwargs['tags']:
                if isinstance(tag, dict) and 'Key' in tag and 'Value' in tag:
                    valid_tags.append(tag)
            
            if valid_tags:
                client.create_tags(
                    Resources=[vpc_id],
                    Tags=valid_tags
                )

        return {
            'message': f'VPC {vpc_id} creada exitosamente',
            'vpc_id': vpc_id,
            'cidr_block': kwargs['cidr_block']
        }

    def _delete_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una VPC"""
        client = self._get_client()

        client.delete_vpc(VpcId=params['vpc_id'])

        return {
            'message': f'VPC {params["vpc_id"]} eliminada exitosamente',
            'vpc_id': params['vpc_id']
        }

    def _describe_subnets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista subnets"""
        client = self._get_client()

        subnet_params = {}
        if 'subnet_ids' in params:
            subnet_params['SubnetIds'] = params['subnet_ids']
        if 'vpc_id' in params:
            subnet_params['Filters'] = [{'Name': 'vpc-id', 'Values': [params['vpc_id']]}]
        if 'filters' in params:
            if 'Filters' not in subnet_params:
                subnet_params['Filters'] = []
            subnet_params['Filters'].extend(params['filters'])
        if 'max_results' in params:
            subnet_params['MaxResults'] = params['max_results']

        response = client.describe_subnets(**subnet_params)

        subnets = []
        for subnet in response['Subnets']:
            subnets.append({
                'subnet_id': subnet['SubnetId'],
                'vpc_id': subnet['VpcId'],
                'cidr_block': subnet.get('CidrBlock'),
                'ipv6_cidr_block_association_set': subnet.get('Ipv6CidrBlockAssociationSet', []),
                'availability_zone': subnet.get('AvailabilityZone'),
                'availability_zone_id': subnet.get('AvailabilityZoneId'),
                'available_ip_address_count': subnet.get('AvailableIpAddressCount'),
                'default_for_az': subnet.get('DefaultForAz', False),
                'map_public_ip_on_launch': subnet.get('MapPublicIpOnLaunch', False),
                'state': subnet.get('State'),
                'tags': {tag['Key']: tag['Value'] for tag in subnet.get('Tags', [])}
            })

        return {
            'subnets': subnets,
            'total_count': len(subnets)
        }

    def _create_subnet(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva subnet"""
        client = self._get_client()

        subnet_params = {
            'VpcId': kwargs['vpc_id'],
            'CidrBlock': kwargs['cidr_block']
        }

        if 'availability_zone' in kwargs:
            subnet_params['AvailabilityZone'] = kwargs['availability_zone']
        if 'availability_zone_id' in kwargs:
            subnet_params['AvailabilityZoneId'] = kwargs['availability_zone_id']
        if 'ipv6_cidr_block' in kwargs:
            subnet_params['Ipv6CidrBlock'] = kwargs['ipv6_cidr_block']

        response = client.create_subnet(**subnet_params)

        subnet_id = response['Subnet']['SubnetId']

        # Agregar tags si se proporcionaron
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            # Validar que los tags tengan el formato correcto
            valid_tags = []
            for tag in kwargs['tags']:
                if isinstance(tag, dict) and 'Key' in tag and 'Value' in tag:
                    valid_tags.append(tag)
            
            if valid_tags:
                client.create_tags(
                    Resources=[subnet_id],
                    Tags=valid_tags
                )

        return {
            'message': f'Subnet {subnet_id} creada exitosamente',
            'subnet_id': subnet_id,
            'vpc_id': kwargs['vpc_id'],
            'cidr_block': kwargs['cidr_block']
        }

    def _delete_subnet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una subnet"""
        client = self._get_client()

        client.delete_subnet(SubnetId=params['subnet_id'])

        return {
            'message': f'Subnet {params["subnet_id"]} eliminada exitosamente',
            'subnet_id': params['subnet_id']
        }

    def _describe_security_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista security groups"""
        client = self._get_client()

        sg_params = {}
        if 'group_ids' in params:
            sg_params['GroupIds'] = params['group_ids']
        if 'group_names' in params:
            sg_params['GroupNames'] = params['group_names']
        if 'filters' in params:
            sg_params['Filters'] = params['filters']
        if 'max_results' in params:
            sg_params['MaxResults'] = params['max_results']

        response = client.describe_security_groups(**sg_params)

        security_groups = []
        for sg in response['SecurityGroups']:
            security_groups.append({
                'group_id': sg['GroupId'],
                'group_name': sg['GroupName'],
                'group_description': sg['GroupDescription'],
                'vpc_id': sg.get('VpcId'),
                'ip_permissions': sg.get('IpPermissions', []),
                'ip_permissions_egress': sg.get('IpPermissionsEgress', []),
                'tags': {tag['Key']: tag['Value'] for tag in sg.get('Tags', [])}
            })

        return {
            'security_groups': security_groups,
            'total_count': len(security_groups)
        }

    def _create_security_group(self, **kwargs) -> Dict[str, Any]:
        """Crea un security group"""
        client = self._get_client()

        sg_params = {
            'GroupName': kwargs['group_name'],
            'Description': kwargs['description']
        }

        if 'vpc_id' in kwargs:
            sg_params['VpcId'] = kwargs['vpc_id']

        response = client.create_security_group(**sg_params)

        group_id = response['GroupId']

        # Agregar tags si se proporcionaron
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            # Validar que los tags tengan el formato correcto
            valid_tags = []
            for tag in kwargs['tags']:
                if isinstance(tag, dict) and 'Key' in tag and 'Value' in tag:
                    valid_tags.append(tag)
            
            if valid_tags:
                client.create_tags(
                    Resources=[group_id],
                    Tags=valid_tags
                )

        return {
            'message': f'Security group {group_id} creado exitosamente',
            'group_id': group_id,
            'group_name': kwargs['group_name']
        }

    def _authorize_security_group_ingress(self, **kwargs) -> Dict[str, Any]:
        """Agrega reglas de entrada a un security group (versión interna)"""
        return self.authorize_security_group_ingress(**kwargs)
    
    def authorize_security_group_ingress(self, group_id: str, ip_permissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Agrega reglas de entrada a un security group.
        
        Args:
            group_id: ID del security group
            ip_permissions: Lista de permisos IP con formato AWS
        
        Returns:
            Dict con resultado de la operación
        
        Example ip_permissions:
        [
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'Allow HTTP from anywhere'}]
            }
        ]
        """
        try:
            client = self._get_client()

            # Validar y corregir formato de ip_permissions
            valid_permissions = []
            for perm in ip_permissions:
                # Si es una lista de strings en lugar de un dict, ignorar
                if not isinstance(perm, dict):
                    continue
                
                # Validar que tenga los campos requeridos
                if 'IpProtocol' not in perm:
                    continue
                
                # Asegurar que IpRanges sea una lista de dicts
                if 'IpRanges' in perm:
                    if isinstance(perm['IpRanges'], list):
                        valid_ranges = []
                        for ip_range in perm['IpRanges']:
                            if isinstance(ip_range, dict) and 'CidrIp' in ip_range:
                                valid_ranges.append(ip_range)
                            elif isinstance(ip_range, str):
                                # Convertir string CIDR a formato correcto
                                valid_ranges.append({'CidrIp': ip_range})
                        perm['IpRanges'] = valid_ranges
                
                # Convertir puertos a enteros si vienen como strings
                if 'FromPort' in perm:
                    perm['FromPort'] = int(perm['FromPort'])
                if 'ToPort' in perm:
                    perm['ToPort'] = int(perm['ToPort'])
                
                valid_permissions.append(perm)
            
            if not valid_permissions:
                return {
                    'success': False,
                    'error': 'No se encontraron permisos IP válidos en el formato correcto',
                    'group_id': group_id
                }

            client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=valid_permissions
            )

            return {
                'success': True,
                'message': f'Reglas de entrada agregadas al security group {group_id}',
                'group_id': group_id,
                'rules_added': len(valid_permissions)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error agregando reglas de entrada: {str(e)}',
                'group_id': group_id
            }
    
    def add_common_security_rules(self, group_id: str, rules: List[str], cidr: str = '0.0.0.0/0') -> Dict[str, Any]:
        """
        Agrega reglas comunes de entrada a un security group.
        
        Args:
            group_id: ID del security group
            rules: Lista de tipos de reglas (http, https, ssh, rdp, mysql, postgres, all-traffic)
            cidr: CIDR para las reglas (por defecto 0.0.0.0/0)
        
        Returns:
            Dict con resultado de la operación
        """
        # Definición de reglas comunes
        common_rules = {
            'http': {'port': 80, 'protocol': 'tcp', 'description': 'Allow HTTP'},
            'https': {'port': 443, 'protocol': 'tcp', 'description': 'Allow HTTPS'},
            'ssh': {'port': 22, 'protocol': 'tcp', 'description': 'Allow SSH'},
            'rdp': {'port': 3389, 'protocol': 'tcp', 'description': 'Allow RDP'},
            'mysql': {'port': 3306, 'protocol': 'tcp', 'description': 'Allow MySQL'},
            'postgres': {'port': 5432, 'protocol': 'tcp', 'description': 'Allow PostgreSQL'},
            'all-traffic': {'port': -1, 'protocol': '-1', 'description': 'Allow all traffic'}
        }
        
        try:
            # Construir lista de permisos IP
            ip_permissions = []
            rules_added = []
            
            for rule in rules:
                rule_lower = rule.lower()
                if rule_lower in common_rules:
                    rule_def = common_rules[rule_lower]
                    
                    permission = {
                        'IpProtocol': rule_def['protocol'],
                        'IpRanges': [{'CidrIp': cidr, 'Description': rule_def['description']}]
                    }
                    
                    # Solo agregar puertos si no es all-traffic
                    if rule_def['port'] != -1:
                        permission['FromPort'] = rule_def['port']
                        permission['ToPort'] = rule_def['port']
                    
                    ip_permissions.append(permission)
                    rules_added.append(f"{rule_lower} (puerto {rule_def['port']})" if rule_def['port'] != -1 else rule_lower)
            
            if not ip_permissions:
                return {
                    'success': False,
                    'error': f'No se encontraron reglas válidas. Reglas disponibles: {", ".join(common_rules.keys())}'
                }
            
            # Agregar las reglas
            result = self.authorize_security_group_ingress(group_id, ip_permissions)
            
            if result.get('success'):
                result['rules_added_details'] = rules_added
                result['cidr'] = cidr
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error agregando reglas comunes: {str(e)}',
                'group_id': group_id
            }

    def _describe_route_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista route tables"""
        client = self._get_client()

        rt_params = {}
        if 'route_table_ids' in params:
            rt_params['RouteTableIds'] = params['route_table_ids']
        if 'vpc_id' in params:
            rt_params['Filters'] = [{'Name': 'vpc-id', 'Values': [params['vpc_id']]}]
        if 'filters' in params:
            if 'Filters' not in rt_params:
                rt_params['Filters'] = []
            rt_params['Filters'].extend(params['filters'])
        if 'max_results' in params:
            rt_params['MaxResults'] = params['max_results']

        response = client.describe_route_tables(**rt_params)

        route_tables = []
        for rt in response['RouteTables']:
            route_tables.append({
                'route_table_id': rt['RouteTableId'],
                'vpc_id': rt['VpcId'],
                'routes': rt.get('Routes', []),
                'associations': rt.get('Associations', []),
                'propagating_vgws': rt.get('PropagatingVgws', []),
                'tags': {tag['Key']: tag['Value'] for tag in rt.get('Tags', [])}
            })

        return {
            'route_tables': route_tables,
            'total_count': len(route_tables)
        }

    def _describe_internet_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista internet gateways"""
        client = self._get_client()

        igw_params = {}
        if 'internet_gateway_ids' in params:
            igw_params['InternetGatewayIds'] = params['internet_gateway_ids']
        if 'filters' in params:
            igw_params['Filters'] = params['filters']
        if 'max_results' in params:
            igw_params['MaxResults'] = params['max_results']

        response = client.describe_internet_gateways(**igw_params)

        internet_gateways = []
        for igw in response['InternetGateways']:
            internet_gateways.append({
                'internet_gateway_id': igw['InternetGatewayId'],
                'attachments': igw.get('Attachments', []),
                'tags': {tag['Key']: tag['Value'] for tag in igw.get('Tags', [])}
            })

        return {
            'internet_gateways': internet_gateways,
            'total_count': len(internet_gateways)
        }

    def _create_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un internet gateway"""
        client = self._get_client()

        response = client.create_internet_gateway()

        igw_id = response['InternetGateway']['InternetGatewayId']

        # Agregar tags si se proporcionaron
        if 'tags' in params:
            client.create_tags(
                Resources=[igw_id],
                Tags=params['tags']
            )

        return {
            'message': f'Internet gateway {igw_id} creado exitosamente',
            'internet_gateway_id': igw_id
        }

    def _attach_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Asocia un internet gateway a una VPC"""
        client = self._get_client()

        client.attach_internet_gateway(
            InternetGatewayId=params['internet_gateway_id'],
            VpcId=params['vpc_id']
        )

        return {
            'message': f'Internet gateway {params["internet_gateway_id"]} asociado a VPC {params["vpc_id"]}',
            'internet_gateway_id': params['internet_gateway_id'],
            'vpc_id': params['vpc_id']
        }

    def _describe_nat_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista NAT gateways"""
        client = self._get_client()

        nat_params = {}
        if 'nat_gateway_ids' in params:
            nat_params['NatGatewayIds'] = params['nat_gateway_ids']
        if 'filter' in params:
            nat_params['Filter'] = params['filter']
        if 'max_results' in params:
            nat_params['MaxResults'] = params['max_results']

        response = client.describe_nat_gateways(**nat_params)

        nat_gateways = []
        for nat in response['NatGateways']:
            nat_gateways.append({
                'nat_gateway_id': nat['NatGatewayId'],
                'subnet_id': nat.get('SubnetId'),
                'nat_gateway_addresses': nat.get('NatGatewayAddresses', []),
                'vpc_id': nat.get('VpcId'),
                'state': nat.get('State'),
                'create_time': nat.get('CreateTime').strftime('%Y-%m-%d %H:%M:%S') if nat.get('CreateTime') else None,
                'delete_time': nat.get('DeleteTime').strftime('%Y-%m-%d %H:%M:%S') if nat.get('DeleteTime') else None,
                'failure_code': nat.get('FailureCode'),
                'failure_message': nat.get('FailureMessage'),
                'tags': {tag['Key']: tag['Value'] for tag in nat.get('Tags', [])}
            })

        return {
            'nat_gateways': nat_gateways,
            'total_count': len(nat_gateways)
        }