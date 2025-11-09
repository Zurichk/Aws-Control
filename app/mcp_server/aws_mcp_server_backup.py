"""
MCP Server para operaciones AWS
Permite que el chat interactúe directamente con AWS mediante herramientas organizadas por categorías
"""
import json
import logging
from typing import Any, Dict, List
import boto3
from dotenv import load_dotenv
import os

# Importar herramientas por categorías
from .Computo.ec2_mcp_tools import EC2MCPTools
from .Almacenamiento.s3_mcp_tools import S3MCPTools
from .Base_de_Datos.rds_mcp_tools import RDSMCPTools
from .Mensajeria.sns_mcp_tools import SNSMCPTools
from .Mensajeria.sqs_mcp_tools import SQSMCPTools
from .Mensajeria.kinesis_mcp_tools import KinesisMCPTools
from .Redes.vpc_mcp_tools import VPCMCPTools
from .Seguridad.iam_mcp_tools import IAMMCPTools
from .Seguridad.kms_mcp_tools import KMSMCPTools
from .Analytics.athena_mcp_tools import AthenaMCPTools
from .Analytics.glue_mcp_tools import GlueMCPTools
from .Contenedores.ecs_mcp_tools import ECSMCPTools
from .ML_AI.sagemaker_mcp_tools import SageMakerMCPTools
from .Gestion.autoscaling_mcp_tools import AutoScalingMCPTools
from .Gestion.cloudwatch_mcp_tools import CloudWatchMCPTools

load_dotenv()

logger = logging.getLogger(__name__)


class AWSMCPServer:
    """Servidor MCP para operaciones AWS organizadas por categorías"""

    def __init__(self):
        # Inicializar instancias de herramientas por categoría
        self.category_tools = {
            'Computo': {
                'ec2': EC2MCPTools(),
                # 'lambda': LambdaMCPTools(),  # TODO: Implementar
                # 'batch': BatchMCPTools(),   # TODO: Implementar
            },
            'Almacenamiento': {
                # 's3': S3MCPTools(),         # TODO: Implementar
                # 'ebs': EBSMCPTools(),       # TODO: Implementar
                # 'efs': EFSMCPTools(),       # TODO: Implementar
                # 'fsx': FSXMCPTools(),       # TODO: Implementar
            },
            'Base_de_Datos': {
                # 'rds': RDSMCPTools(),       # TODO: Implementar
                # 'dynamodb': DynamoDBMCPTools(), # TODO: Implementar
                # 'neptune': NeptuneMCPTools(),   # TODO: Implementar
                # 'documentdb': DocumentDBMCPTools(), # TODO: Implementar
                # 'elasticache': ElastiCacheMCPTools(), # TODO: Implementar
            },
            'Mensajeria': {
                # 'sns': SNSMCPTools(),       # TODO: Implementar
                # 'sqs': SQSMCPTools(),       # TODO: Implementar
                'kinesis': KinesisMCPTools(),
            },
            'Redes': {
                # 'vpc': VPCMCPTools(),       # TODO: Implementar
                # 'route53': Route53MCPTools(), # TODO: Implementar
                # 'cloudfront': CloudFrontMCPTools(), # TODO: Implementar
                # 'elb': ELBMCPTools(),       # TODO: Implementar
                # 'apigateway': APIGatewayMCPTools(), # TODO: Implementar
            },
            'Seguridad': {
                # 'iam': IAMMCPTools(),       # TODO: Implementar
                # 'kms': KMSMCPTools(),       # TODO: Implementar
                # 'acm': ACMMCPTools(),       # TODO: Implementar
                # 'secretsmanager': SecretsManagerMCPTools(), # TODO: Implementar
                # 'security_groups': SecurityGroupsMCPTools(), # TODO: Implementar
            },
            'Analytics': {
                'athena': AthenaMCPTools(),
                'glue': GlueMCPTools(),
                # 'emr': EMRMCPTools(),       # TODO: Implementar
            },
            'Integracion': {
                # 'cloudformation': CloudFormationMCPTools(), # TODO: Implementar
            },
            'Contenedores': {
                'ecs': ECSMCPTools(),
                # 'eks': EKSMCPTools(),       # TODO: Implementar
            },
            'ML_AI': {
                # 'sagemaker': SageMakerMCPTools(), # TODO: Implementar
                # 'bedrock': BedrockMCPTools(),     # TODO: Implementar
                # 'rekognition': RekognitionMCPTools(), # TODO: Implementar
            },
            'Gestion': {
                # 'autoscaling': AutoScalingMCPTools(), # TODO: Implementar
                'cloudwatch': CloudWatchMCPTools(),
                # 'cost_explorer': CostExplorerMCPTools(), # TODO: Implementar
            },
            'Config': {
                # 'config': ConfigMCPTools(), # TODO: Implementar
            },
            'AI_Assistant': {
                # 'chat': ChatMCPTools(),     # TODO: Implementar
            }
        }

        self.tools = self._register_tools()

    def _register_tools(self) -> List[Dict[str, Any]]:
        """Registra todas las herramientas disponibles organizadas por categorías"""
        tools = []

        # Registrar herramientas de cada categoría
        for category, services in self.category_tools.items():
            for service_name, service_instance in services.items():
                if hasattr(service_instance, 'get_tools'):
                    category_tools = service_instance.get_tools()
                    tools.extend(category_tools)

        return tools
            {
                "name": "create_ec2_instance",
                "description": "Crea una instancia EC2 con VPC y configuración de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_type": {
                            "type": "string",
                            "description": "Tipo de instancia (ej: t2.micro, t3.small)",
                            "default": "t2.micro"
                        },
                        "ami_id": {
                            "type": "string",
                            "description": "ID de la AMI a usar"
                        },
                        "key_name": {
                            "type": "string",
                            "description": "Nombre de la key pair para SSH"
                        },
                        "environment": {
                            "type": "string",
                            "description": "Entorno (development, staging, production)",
                            "enum": ["development", "staging", "production"]
                        },
                        "create_vpc": {
                            "type": "boolean",
                            "description": "Si debe crear una VPC nueva",
                            "default": True
                        }
                    },
                    "required": ["instance_type", "environment"]
                }
            },
            {
                "name": "list_ec2_instances",
                "description": "Lista todas las instancias EC2 activas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Filtros para las instancias (ej: estado, tags)"
                        }
                    }
                }
            },
            {
                "name": "stop_ec2_instance",
                "description": "Detiene una instancia EC2",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia a detener"
                        }
                    },
                    "required": ["instance_id"]
                }
            },
            {
                "name": "start_ec2_instance",
                "description": "Inicia una instancia EC2 que está detenida",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia a iniciar"
                        }
                    },
                    "required": ["instance_id"]
                }
            },
            {
                "name": "modify_instance_security_groups",
                "description": "Modifica los security groups de una instancia EC2. Reemplaza todos los security groups actuales con los nuevos especificados.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia EC2"
                        },
                        "security_group_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de IDs de security groups a asignar (reemplaza los existentes)"
                        }
                    },
                    "required": ["instance_id", "security_group_ids"]
                }
            },
            {
                "name": "terminate_ec2_instance",
                "description": "Termina (elimina) una instancia EC2",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia a terminar"
                        }
                    },
                    "required": ["instance_id"]
                }
            },
            {
                "name": "create_secure_vpc",
                "description": "Crea una VPC con configuración de seguridad robusta",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_name": {
                            "type": "string",
                            "description": "Nombre de la VPC"
                        },
                        "cidr_block": {
                            "type": "string",
                            "description": "Bloque CIDR para la VPC",
                            "default": "10.0.0.0/16"
                        },
                        "enable_dns": {
                            "type": "boolean",
                            "description": "Habilitar DNS",
                            "default": True
                        }
                    },
                    "required": ["vpc_name"]
                }
            },
            {
                "name": "create_subnet",
                "description": "Crea una nueva subnet en una VPC",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC"
                        },
                        "cidr_block": {
                            "type": "string",
                            "description": "Bloque CIDR para la subnet"
                        },
                        "availability_zone": {
                            "type": "string",
                            "description": "Zona de disponibilidad (opcional)"
                        }
                    },
                    "required": ["vpc_id", "cidr_block"]
                }
            },
            {
                "name": "delete_subnet",
                "description": "Elimina una subnet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subnet_id": {
                            "type": "string",
                            "description": "ID de la subnet a eliminar"
                        }
                    },
                    "required": ["subnet_id"]
                }
            },
            {
                "name": "list_route_tables",
                "description": "Lista las route tables disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC para filtrar (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_route_table",
                "description": "Crea una nueva route table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC"
                        }
                    },
                    "required": ["vpc_id"]
                }
            },
            {
                "name": "associate_route_table",
                "description": "Asocia una route table a una subnet",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_table_id": {
                            "type": "string",
                            "description": "ID de la route table"
                        },
                        "subnet_id": {
                            "type": "string",
                            "description": "ID de la subnet"
                        }
                    },
                    "required": ["route_table_id", "subnet_id"]
                }
            },
            {
                "name": "create_route",
                "description": "Crea una nueva ruta en una route table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_table_id": {
                            "type": "string",
                            "description": "ID de la route table"
                        },
                        "destination_cidr_block": {
                            "type": "string",
                            "description": "Bloque CIDR de destino"
                        },
                        "gateway_id": {
                            "type": "string",
                            "description": "ID del gateway (IGW, NAT, etc.)"
                        }
                    },
                    "required": ["route_table_id", "destination_cidr_block", "gateway_id"]
                }
            },
            {
                "name": "list_internet_gateways",
                "description": "Lista los internet gateways disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "create_internet_gateway",
                "description": "Crea un nuevo internet gateway",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "attach_internet_gateway",
                "description": "Adjunta un internet gateway a una VPC",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "internet_gateway_id": {
                            "type": "string",
                            "description": "ID del internet gateway"
                        },
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC"
                        }
                    },
                    "required": ["internet_gateway_id", "vpc_id"]
                }
            },
            {
                "name": "list_nat_gateways",
                "description": "Lista los NAT gateways disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC para filtrar (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_nat_gateway",
                "description": "Crea un nuevo NAT gateway",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subnet_id": {
                            "type": "string",
                            "description": "ID de la subnet"
                        },
                        "connectivity_type": {
                            "type": "string",
                            "description": "Tipo de conectividad",
                            "enum": ["public", "private"],
                            "default": "public"
                        },
                        "allocation_id": {
                            "type": "string",
                            "description": "ID de asignación de Elastic IP (para public NAT)"
                        }
                    },
                    "required": ["subnet_id"]
                }
            },
            {
                "name": "create_vpc_peering",
                "description": "Crea una conexión VPC peering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC requerente"
                        },
                        "peer_vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC peer"
                        },
                        "peer_owner_id": {
                            "type": "string",
                            "description": "ID del owner de la VPC peer (opcional)"
                        }
                    },
                    "required": ["vpc_id", "peer_vpc_id"]
                }
            },
            {
                "name": "accept_vpc_peering",
                "description": "Acepta una conexión VPC peering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_peering_connection_id": {
                            "type": "string",
                            "description": "ID de la conexión VPC peering"
                        }
                    },
                    "required": ["vpc_peering_connection_id"]
                }
            },
            {
                "name": "create_security_group",
                "description": "Crea un grupo de seguridad con reglas restrictivas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo de seguridad"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción del grupo"
                        },
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC"
                        },
                        "allowed_ports": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Puertos permitidos (ej: [22, 80, 443])"
                        }
                    },
                    "required": ["group_name", "vpc_id"]
                }
            },
            {
                "name": "create_s3_bucket",
                "description": "Crea un bucket S3 con encriptación y versionado",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket"
                        },
                        "enable_versioning": {
                            "type": "boolean",
                            "description": "Habilitar versionado",
                            "default": True
                        },
                        "enable_encryption": {
                            "type": "boolean",
                            "description": "Habilitar encriptación",
                            "default": True
                        }
                    },
                    "required": ["bucket_name"]
                }
            },
            {
                "name": "delete_s3_bucket",
                "description": "Elimina un bucket S3. ADVERTENCIA: Primero elimina todos los objetos del bucket antes de eliminarlo.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket a eliminar"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Si es true, elimina todos los objetos antes de eliminar el bucket",
                            "default": False
                        }
                    },
                    "required": ["bucket_name"]
                }
            },
            {
                "name": "get_aws_costs",
                "description": "Obtiene información de costos de AWS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Fecha inicio (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Fecha fin (YYYY-MM-DD)"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            {
                "name": "get_cost_forecast",
                "description": "Obtiene pronóstico de costos de AWS para un período futuro",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Fecha inicio del pronóstico (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Fecha fin del pronóstico (YYYY-MM-DD)"
                        },
                        "prediction_interval_level": {
                            "type": "integer",
                            "description": "Nivel de intervalo de predicción (por defecto: 80)",
                            "default": 80,
                            "minimum": 50,
                            "maximum": 99
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            {
                "name": "get_cost_categories",
                "description": "Obtiene desglose de costos por categoría/servicio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Fecha inicio del análisis (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Fecha fin del análisis (YYYY-MM-DD)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de categorías a retornar (por defecto: 10)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            {
                "name": "get_savings_plans_utilization",
                "description": "Obtiene información de utilización de Savings Plans",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Fecha inicio del análisis (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Fecha fin del análisis (YYYY-MM-DD)"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            {
                "name": "search_amis",
                "description": "Busca AMIs (Amazon Machine Images) disponibles con filtros específicos. Útil para encontrar la AMI correcta antes de crear una instancia EC2.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Propietario de la AMI: 'amazon' (propiedad de Amazon), 'aws-marketplace' (marketplace), 'self' (propias), o un Account ID específico",
                            "enum": ["amazon", "aws-marketplace", "self"],
                            "default": "amazon"
                        },
                        "platform": {
                            "type": "string",
                            "description": "Plataforma del sistema operativo",
                            "enum": ["windows", "linux"],
                            "default": "linux"
                        },
                        "architecture": {
                            "type": "string",
                            "description": "Arquitectura del procesador",
                            "enum": ["x86_64", "arm64"],
                            "default": "x86_64"
                        },
                        "root_device_type": {
                            "type": "string",
                            "description": "Tipo de dispositivo raíz",
                            "enum": ["ebs", "instance-store"],
                            "default": "ebs"
                        },
                        "name_filter": {
                            "type": "string",
                            "description": "Filtro de nombre (wildcard con *). Ej: 'ubuntu*', 'amzn2-ami-*', 'Windows_Server-2022-*'"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Máximo número de resultados a devolver",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_vpcs",
                "description": "Lista todas las VPCs (Virtual Private Clouds) disponibles en la cuenta AWS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "IDs de VPCs específicas a listar (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "describe_vpc",
                "description": "Obtiene información detallada de una VPC específica",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC (ej: vpc-0123456789abcdef0)"
                        }
                    },
                    "required": ["vpc_id"]
                }
            },
            {
                "name": "list_s3_buckets",
                "description": "Lista todos los buckets S3 en la cuenta AWS",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_security_groups",
                "description": "Lista los grupos de seguridad disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC para filtrar grupos de seguridad (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "delete_security_group",
                "description": "Elimina un grupo de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "string",
                            "description": "ID del grupo de seguridad a eliminar"
                        }
                    },
                    "required": ["group_id"]
                }
            },
            {
                "name": "authorize_ingress",
                "description": "Autoriza una regla de entrada (ingress) en un grupo de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "string",
                            "description": "ID del grupo de seguridad"
                        },
                        "protocol": {
                            "type": "string",
                            "description": "Protocolo (tcp, udp, icmp, -1 para todos)",
                            "enum": ["tcp", "udp", "icmp", "-1"]
                        },
                        "port_range_from": {
                            "type": "integer",
                            "description": "Puerto inicial del rango (opcional para icmp, requerido para tcp/udp)"
                        },
                        "port_range_to": {
                            "type": "integer",
                            "description": "Puerto final del rango (opcional para icmp, requerido para tcp/udp)"
                        },
                        "source_type": {
                            "type": "string",
                            "description": "Tipo de fuente: 'cidr' o 'security_group'",
                            "enum": ["cidr", "security_group"]
                        },
                        "source_value": {
                            "type": "string",
                            "description": "Valor de la fuente (CIDR block o Security Group ID)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción opcional de la regla"
                        }
                    },
                    "required": ["group_id", "protocol", "source_type", "source_value"]
                }
            },
            {
                "name": "revoke_ingress",
                "description": "Revoca una regla de entrada (ingress) de un grupo de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "string",
                            "description": "ID del grupo de seguridad"
                        },
                        "rule_index": {
                            "type": "integer",
                            "description": "Índice de la regla a revocar (0-based)"
                        }
                    },
                    "required": ["group_id", "rule_index"]
                }
            },
            {
                "name": "authorize_egress",
                "description": "Autoriza una regla de salida (egress) en un grupo de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "string",
                            "description": "ID del grupo de seguridad"
                        },
                        "protocol": {
                            "type": "string",
                            "description": "Protocolo (tcp, udp, icmp, -1 para todos)",
                            "enum": ["tcp", "udp", "icmp", "-1"]
                        },
                        "port_range_from": {
                            "type": "integer",
                            "description": "Puerto inicial del rango (opcional para icmp, requerido para tcp/udp)"
                        },
                        "port_range_to": {
                            "type": "integer",
                            "description": "Puerto final del rango (opcional para icmp, requerido para tcp/udp)"
                        },
                        "destination_type": {
                            "type": "string",
                            "description": "Tipo de destino: 'cidr' o 'security_group'",
                            "enum": ["cidr", "security_group"]
                        },
                        "destination_value": {
                            "type": "string",
                            "description": "Valor del destino (CIDR block o Security Group ID)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción opcional de la regla"
                        }
                    },
                    "required": ["group_id", "protocol", "destination_type", "destination_value"]
                }
            },
            {
                "name": "revoke_egress",
                "description": "Revoca una regla de salida (egress) de un grupo de seguridad",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_id": {
                            "type": "string",
                            "description": "ID del grupo de seguridad"
                        },
                        "rule_index": {
                            "type": "integer",
                            "description": "Índice de la regla a revocar (0-based)"
                        }
                    },
                    "required": ["group_id", "rule_index"]
                }
            },
            {
                "name": "list_subnets",
                "description": "Lista las subnets disponibles en una VPC",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC para listar sus subnets"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_ami_from_instance",
                "description": "Crea una AMI (imagen) personalizada desde una instancia EC2 existente",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia EC2 origen"
                        },
                        "ami_name": {
                            "type": "string",
                            "description": "Nombre para la nueva AMI"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción de la AMI"
                        },
                        "no_reboot": {
                            "type": "boolean",
                            "description": "Si true, no reinicia la instancia antes de crear la imagen",
                            "default": False
                        }
                    },
                    "required": ["instance_id", "ami_name"]
                }
            },
            {
                "name": "list_load_balancers",
                "description": "Lista los Application/Network Load Balancers (ALB/NLB)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Nombres específicos de load balancers (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_target_groups",
                "description": "Lista los grupos de destino (target groups) para load balancers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "load_balancer_arn": {
                            "type": "string",
                            "description": "ARN del load balancer para filtrar (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_target_group",
                "description": "Crea un grupo de destino para load balancers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del target group"
                        },
                        "protocol": {
                            "type": "string",
                            "description": "Protocolo (HTTP, HTTPS, TCP, TLS, UDP, TCP_UDP)",
                            "enum": ["HTTP", "HTTPS", "TCP", "TLS", "UDP", "TCP_UDP"],
                            "default": "HTTP"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Puerto del target group",
                            "default": 80
                        },
                        "vpc_id": {
                            "type": "string",
                            "description": "ID de la VPC"
                        },
                        "health_check_path": {
                            "type": "string",
                            "description": "Ruta para health check (para HTTP/HTTPS)",
                            "default": "/"
                        }
                    },
                    "required": ["name", "vpc_id"]
                }
            },
            {
                "name": "list_autoscaling_groups",
                "description": "Lista los grupos de Auto Scaling configurados",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Nombres específicos de ASG (opcional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_launch_template",
                "description": "Crea una plantilla de lanzamiento para Auto Scaling",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "template_name": {
                            "type": "string",
                            "description": "Nombre de la plantilla"
                        },
                        "ami_id": {
                            "type": "string",
                            "description": "ID de la AMI a usar"
                        },
                        "instance_type": {
                            "type": "string",
                            "description": "Tipo de instancia (ej: t3.micro)",
                            "default": "t3.micro"
                        },
                        "key_name": {
                            "type": "string",
                            "description": "Nombre del key pair"
                        },
                        "security_group_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "IDs de security groups"
                        },
                        "user_data": {
                            "type": "string",
                            "description": "Script de inicialización (base64 o texto plano)"
                        }
                    },
                    "required": ["template_name", "ami_id"]
                }
            },
            {
                "name": "create_autoscaling_group",
                "description": "Crea un grupo de Auto Scaling con configuración de escalado",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del Auto Scaling Group"
                        },
                        "launch_template_id": {
                            "type": "string",
                            "description": "ID de la Launch Template"
                        },
                        "min_size": {
                            "type": "integer",
                            "description": "Tamaño mínimo",
                            "default": 1
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Tamaño máximo",
                            "default": 3
                        },
                        "desired_capacity": {
                            "type": "integer",
                            "description": "Capacidad deseada",
                            "default": 2
                        },
                        "vpc_zone_identifiers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "IDs de subnets donde lanzar instancias"
                        },
                        "target_group_arns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "ARNs de target groups"
                        },
                        "health_check_type": {
                            "type": "string",
                            "description": "Tipo de health check (EC2 o ELB)",
                            "enum": ["EC2", "ELB"],
                            "default": "EC2"
                        }
                    },
                    "required": ["name", "launch_template_id", "vpc_zone_identifiers"]
                }
            },
            {
                "name": "list_rds_instances",
                "description": "Lista las instancias de bases de datos RDS",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_aurora_clusters",
                "description": "Lista los clusters de Amazon Aurora (MySQL y PostgreSQL)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "create_rds_instance",
                "description": "Crea una instancia de base de datos RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "Identificador único de la instancia"
                        },
                        "engine": {
                            "type": "string",
                            "description": "Motor de base de datos (mysql, postgres, mariadb, oracle-ee, sqlserver-ex)",
                            "enum": ["mysql", "postgres", "mariadb", "oracle-ee", "sqlserver-ex"],
                            "default": "mysql"
                        },
                        "instance_class": {
                            "type": "string",
                            "description": "Clase de instancia (ej: db.t3.micro, db.t4g.micro)",
                            "default": "db.t3.micro"
                        },
                        "allocated_storage": {
                            "type": "integer",
                            "description": "Almacenamiento en GB (mínimo 20)",
                            "default": 20
                        },
                        "master_username": {
                            "type": "string",
                            "description": "Usuario maestro de la base de datos",
                            "default": "admin"
                        },
                        "master_password": {
                            "type": "string",
                            "description": "Contraseña maestra (mínimo 8 caracteres)"
                        },
                        "vpc_security_group_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "IDs de security groups"
                        },
                        "publicly_accessible": {
                            "type": "boolean",
                            "description": "Si la DB debe ser accesible públicamente",
                            "default": False
                        }
                    },
                    "required": ["db_instance_identifier", "master_password"]
                }
            },
            {
                "name": "list_dynamodb_tables",
                "description": "Lista las tablas de DynamoDB",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "create_dynamodb_table",
                "description": "Crea una tabla en DynamoDB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Nombre de la tabla"
                        },
                        "partition_key": {
                            "type": "string",
                            "description": "Nombre de la partition key"
                        },
                        "partition_key_type": {
                            "type": "string",
                            "description": "Tipo de la partition key",
                            "enum": ["S", "N", "B"],
                            "default": "S"
                        },
                        "sort_key": {
                            "type": "string",
                            "description": "Nombre de la sort key (opcional)"
                        },
                        "sort_key_type": {
                            "type": "string",
                            "description": "Tipo de la sort key",
                            "enum": ["S", "N", "B"],
                            "default": "S"
                        },
                        "billing_mode": {
                            "type": "string",
                            "description": "Modo de facturación",
                            "enum": ["PROVISIONED", "PAY_PER_REQUEST"],
                            "default": "PAY_PER_REQUEST"
                        }
                    },
                    "required": ["table_name", "partition_key"]
                }
            },
            # ElastiCache Tools
            {
                "name": "list_elasticache_clusters",
                "description": "Lista los clusters de ElastiCache (Redis y Memcached)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "engine": {
                            "type": "string",
                            "description": "Filtrar por motor (redis o memcached)",
                            "enum": ["redis", "memcached", "all"],
                            "default": "all"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "create_elasticache_cluster",
                "description": "Crea un cluster de ElastiCache (Redis o Memcached)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_id": {
                            "type": "string",
                            "description": "Identificador único del cluster"
                        },
                        "engine": {
                            "type": "string",
                            "description": "Motor de caché",
                            "enum": ["redis", "memcached"],
                            "default": "redis"
                        },
                        "node_type": {
                            "type": "string",
                            "description": "Tipo de nodo (ej: cache.t3.micro, cache.t4g.micro)",
                            "default": "cache.t3.micro"
                        },
                        "num_cache_nodes": {
                            "type": "integer",
                            "description": "Número de nodos (solo para Memcached, Redis siempre usa 1)",
                            "default": 1
                        },
                        "engine_version": {
                            "type": "string",
                            "description": "Versión del motor",
                            "default": "7.0"
                        }
                    },
                    "required": ["cluster_id", "engine"]
                }
            },
            {
                "name": "delete_elasticache_cluster",
                "description": "Elimina un cluster de ElastiCache",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_id": {
                            "type": "string",
                            "description": "ID del cluster a eliminar"
                        }
                    },
                    "required": ["cluster_id"]
                }
            },
            {
                "name": "reboot_elasticache_cluster",
                "description": "Reinicia un cluster de ElastiCache",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_id": {
                            "type": "string",
                            "description": "ID del cluster a reiniciar"
                        }
                    },
                    "required": ["cluster_id"]
                }
            },
            # RDS Snapshots Tools
            {
                "name": "create_rds_snapshot",
                "description": "Crea un snapshot manual de una instancia RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia RDS"
                        },
                        "snapshot_identifier": {
                            "type": "string",
                            "description": "Identificador único para el snapshot"
                        }
                    },
                    "required": ["db_instance_identifier", "snapshot_identifier"]
                }
            },
            {
                "name": "delete_rds_snapshot",
                "description": "Elimina un snapshot de RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "snapshot_identifier": {
                            "type": "string",
                            "description": "ID del snapshot a eliminar"
                        }
                    },
                    "required": ["snapshot_identifier"]
                }
            },
            {
                "name": "delete_rds_instance",
                "description": "Elimina una instancia de RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia a eliminar"
                        },
                        "skip_final_snapshot": {
                            "type": "boolean",
                            "description": "Si se debe omitir el snapshot final",
                            "default": False
                        },
                        "final_snapshot_identifier": {
                            "type": "string",
                            "description": "ID para el snapshot final (requerido si skip_final_snapshot=False)"
                        }
                    },
                    "required": ["db_instance_identifier"]
                }
            },
            {
                "name": "modify_rds_instance",
                "description": "Modifica una instancia de RDS (clase de instancia, almacenamiento)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia a modificar"
                        },
                        "db_instance_class": {
                            "type": "string",
                            "description": "Nueva clase de instancia (opcional)"
                        },
                        "allocated_storage": {
                            "type": "integer",
                            "description": "Nuevo tamaño de almacenamiento en GB (opcional, debe ser mayor al actual)"
                        }
                    },
                    "required": ["db_instance_identifier"]
                }
            },
            {
                "name": "reboot_rds_instance",
                "description": "Reinicia una instancia de RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia a reiniciar"
                        }
                    },
                    "required": ["db_instance_identifier"]
                }
            },
            {
                "name": "stop_rds_instance",
                "description": "Detiene una instancia de RDS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia a detener"
                        }
                    },
                    "required": ["db_instance_identifier"]
                }
            },
            {
                "name": "start_rds_instance",
                "description": "Inicia una instancia de RDS detenida",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_instance_identifier": {
                            "type": "string",
                            "description": "ID de la instancia a iniciar"
                        }
                    },
                    "required": ["db_instance_identifier"]
                }
            },
            # DynamoDB Item Operations
            {
                "name": "put_dynamodb_item",
                "description": "Inserta o actualiza un item en una tabla DynamoDB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Nombre de la tabla"
                        },
                        "item": {
                            "type": "object",
                            "description": "Item a insertar (debe incluir las keys de la tabla)"
                        }
                    },
                    "required": ["table_name", "item"]
                }
            },
            {
                "name": "delete_dynamodb_item",
                "description": "Elimina un item de una tabla DynamoDB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Nombre de la tabla"
                        },
                        "key": {
                            "type": "object",
                            "description": "Clave del item (partition key y sort key si aplica)"
                        }
                    },
                    "required": ["table_name", "key"]
                }
            },
            {
                "name": "delete_dynamodb_table",
                "description": "Elimina una tabla de DynamoDB",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Nombre de la tabla a eliminar"
                        }
                    },
                    "required": ["table_name"]
                }
            },
            # Neptune Tools
            {
                "name": "list_neptune_clusters",
                "description": "Lista los clusters de Amazon Neptune (Graph Database)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "create_neptune_cluster",
                "description": "Crea un cluster de Neptune (Graph Database)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_identifier": {
                            "type": "string",
                            "description": "Identificador único del cluster"
                        },
                        "instance_class": {
                            "type": "string",
                            "description": "Clase de instancia",
                            "default": "db.t3.medium"
                        },
                        "engine_version": {
                            "type": "string",
                            "description": "Versión del motor Neptune",
                            "default": "1.2.1.0"
                        },
                        "master_password": {
                            "type": "string",
                            "description": "Contraseña maestra del cluster"
                        }
                    },
                    "required": ["cluster_identifier", "master_password"]
                }
            },
            {
                "name": "delete_neptune_cluster",
                "description": "Elimina un cluster de Neptune",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_identifier": {
                            "type": "string",
                            "description": "ID del cluster a eliminar"
                        }
                    },
                    "required": ["cluster_identifier"]
                }
            },
            # DocumentDB Tools
            {
                "name": "list_documentdb_clusters",
                "description": "Lista los clusters de Amazon DocumentDB (compatible con MongoDB)",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "create_documentdb_cluster",
                "description": "Crea un cluster de DocumentDB (compatible con MongoDB)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cluster_identifier": {
                            "type": "string",
                            "description": "Identificador único del cluster"
                        },
                        "instance_class": {
                            "type": "string",
                            "description": "Clase de instancia",
                            "default": "db.t3.medium"
                        },
                        "engine_version": {
                            "type": "string",
                            "description": "Versión de DocumentDB",
                            "default": "5.0.0"
                        },
                        "master_password": {
                            "type": "string",
                            "description": "Contraseña maestra del cluster"
                        }
                    },
                    "required": ["cluster_identifier", "master_password"]
                }
            },
            {
                "name": "create_iam_user",
                "description": "Crea un nuevo usuario IAM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Nombre del usuario IAM a crear"
                        }
                    },
                    "required": ["user_name"]
                }
            },
            {
                "name": "delete_iam_user",
                "description": "Elimina un usuario IAM y todas sus claves de acceso",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Nombre del usuario IAM a eliminar"
                        }
                    },
                    "required": ["user_name"]
                }
            },
            {
                "name": "list_iam_users",
                "description": "Lista todos los usuarios IAM en la cuenta",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_iam_role",
                "description": "Crea un nuevo rol IAM con política de confianza",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "role_name": {
                            "type": "string",
                            "description": "Nombre del rol IAM a crear"
                        },
                        "assume_role_policy_document": {
                            "type": "string",
                            "description": "Documento JSON de política de confianza"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción opcional del rol"
                        }
                    },
                    "required": ["role_name", "assume_role_policy_document"]
                }
            },
            {
                "name": "delete_iam_role",
                "description": "Elimina un rol IAM y desadjunta todas las políticas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "role_name": {
                            "type": "string",
                            "description": "Nombre del rol IAM a eliminar"
                        }
                    },
                    "required": ["role_name"]
                }
            },
            {
                "name": "list_iam_roles",
                "description": "Lista todos los roles IAM en la cuenta",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_iam_policy",
                "description": "Crea una nueva política IAM administrada por el cliente",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "policy_name": {
                            "type": "string",
                            "description": "Nombre de la política"
                        },
                        "policy_document": {
                            "type": "string",
                            "description": "Documento JSON de la política"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción opcional de la política"
                        }
                    },
                    "required": ["policy_name", "policy_document"]
                }
            },
            {
                "name": "delete_iam_policy",
                "description": "Elimina una política IAM administrada por el cliente",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "policy_arn": {
                            "type": "string",
                            "description": "ARN de la política a eliminar"
                        }
                    },
                    "required": ["policy_arn"]
                }
            },
            {
                "name": "list_iam_policies",
                "description": "Lista todas las políticas IAM administradas por el cliente",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_access_key",
                "description": "Crea una nueva clave de acceso para un usuario IAM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Nombre del usuario IAM"
                        }
                    },
                    "required": ["user_name"]
                }
            },
            {
                "name": "delete_access_key",
                "description": "Elimina una clave de acceso de un usuario IAM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Nombre del usuario IAM"
                        },
                        "access_key_id": {
                            "type": "string",
                            "description": "ID de la clave de acceso a eliminar"
                        }
                    },
                    "required": ["user_name", "access_key_id"]
                }
            },
            {
                "name": "list_access_keys",
                "description": "Lista todas las claves de acceso de un usuario IAM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_name": {
                            "type": "string",
                            "description": "Nombre del usuario IAM"
                        }
                    },
                    "required": ["user_name"]
                }
            },
            # Herramientas KMS (Key Management Service)
            {
                "name": "create_kms_key",
                "description": "Crea una nueva clave KMS para encriptación",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Descripción opcional de la clave"
                        },
                        "alias": {
                            "type": "string",
                            "description": "Alias opcional para la clave (sin alias/)"
                        },
                        "key_usage": {
                            "type": "string",
                            "description": "Uso de la clave",
                            "enum": ["ENCRYPT_DECRYPT", "SIGN_VERIFY"],
                            "default": "ENCRYPT_DECRYPT"
                        },
                        "key_spec": {
                            "type": "string",
                            "description": "Especificación de la clave",
                            "enum": ["SYMMETRIC_DEFAULT", "RSA_2048", "RSA_3072", "RSA_4096", "ECC_NIST_P256", "ECC_NIST_P384", "ECC_NIST_P521"],
                            "default": "SYMMETRIC_DEFAULT"
                        },
                        "multi_region": {
                            "type": "boolean",
                            "description": "Si la clave debe ser multi-región",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "list_kms_keys",
                "description": "Lista todas las claves KMS disponibles",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "encrypt_data",
                "description": "Encripta datos usando una clave KMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        },
                        "plaintext": {
                            "type": "string",
                            "description": "Datos a encriptar (máximo 4096 bytes)"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "Formato de salida",
                            "enum": ["base64", "hex", "raw"],
                            "default": "base64"
                        }
                    },
                    "required": ["key_id", "plaintext"]
                }
            },
            {
                "name": "decrypt_data",
                "description": "Desencripta datos usando una clave KMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ciphertext_blob": {
                            "type": "string",
                            "description": "Datos encriptados a desencriptar"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "Formato de los datos encriptados",
                            "enum": ["base64", "hex", "raw"],
                            "default": "base64"
                        }
                    },
                    "required": ["ciphertext_blob"]
                }
            },
            {
                "name": "generate_data_key",
                "description": "Genera una clave de datos encriptada con KMS (envelope encryption)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        },
                        "key_length": {
                            "type": "integer",
                            "description": "Longitud de la clave de datos en bits",
                            "enum": [128, 256],
                            "default": 256
                        },
                        "include_plaintext": {
                            "type": "boolean",
                            "description": "Incluir la clave de datos en texto plano",
                            "default": True
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "enable_kms_key",
                "description": "Habilita una clave KMS deshabilitada",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "disable_kms_key",
                "description": "Deshabilita una clave KMS habilitada",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "rotate_kms_key",
                "description": "Rota la clave material de una clave KMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "schedule_key_deletion",
                "description": "Programa la eliminación de una clave KMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        },
                        "pending_days": {
                            "type": "integer",
                            "description": "Días de espera antes de la eliminación (7-30)",
                            "minimum": 7,
                            "maximum": 30,
                            "default": 7
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "cancel_key_deletion",
                "description": "Cancela la eliminación programada de una clave KMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_id": {
                            "type": "string",
                            "description": "ID, ARN, alias o alias ARN de la clave KMS"
                        }
                    },
                    "required": ["key_id"]
                }
            },
            {
                "name": "create_key_pair",
                "description": "Crea un nuevo par de claves (key pair) para acceder a instancias EC2",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_name": {
                            "type": "string",
                            "description": "Nombre único del key pair"
                        }
                    },
                    "required": ["key_name"]
                }
            },
            {
                "name": "list_key_pairs",
                "description": "Lista todos los pares de claves disponibles en la cuenta",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "delete_key_pair",
                "description": "Elimina un par de claves existente",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key_name": {
                            "type": "string",
                            "description": "Nombre del key pair a eliminar"
                        }
                    },
                    "required": ["key_name"]
                }
            },
            {
                "name": "describe_instance_types",
                "description": "Lista los tipos de instancia EC2 disponibles con sus especificaciones",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "modify_instance_attribute",
                "description": "Modifica atributos de una instancia EC2 (tipo de instancia, grupos de seguridad, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia a modificar"
                        },
                        "attribute": {
                            "type": "string",
                            "description": "Atributo a modificar (instanceType, securityGroups, etc.)",
                            "enum": ["instanceType", "securityGroups"]
                        },
                        "value": {
                            "type": "string",
                            "description": "Nuevo valor para el atributo"
                        }
                    },
                    "required": ["instance_id", "attribute", "value"]
                }
            },
            {
                "name": "update_autoscaling_group",
                "description": "Actualiza la configuración de un grupo de Auto Scaling (tamaños min/max, capacidad deseada)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo de Auto Scaling"
                        },
                        "min_size": {
                            "type": "integer",
                            "description": "Nuevo tamaño mínimo"
                        },
                        "max_size": {
                            "type": "integer",
                            "description": "Nuevo tamaño máximo"
                        },
                        "desired_capacity": {
                            "type": "integer",
                            "description": "Nueva capacidad deseada"
                        }
                    },
                    "required": ["group_name"]
                }
            },
            {
                "name": "delete_autoscaling_group",
                "description": "Elimina un grupo de Auto Scaling y opcionalmente sus instancias",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo de Auto Scaling a eliminar"
                        },
                        "force_delete": {
                            "type": "boolean",
                            "description": "Si debe forzar la eliminación (elimina instancias también)",
                            "default": True
                        }
                    },
                    "required": ["group_name"]
                }
            },
            {
                "name": "create_scaling_policy",
                "description": "Crea una política de escalado para un grupo de Auto Scaling",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo de Auto Scaling"
                        },
                        "policy_name": {
                            "type": "string",
                            "description": "Nombre de la política de escalado"
                        },
                        "policy_type": {
                            "type": "string",
                            "description": "Tipo de política (SimpleScaling, StepScaling, TargetTrackingScaling)",
                            "enum": ["SimpleScaling", "StepScaling", "TargetTrackingScaling"],
                            "default": "SimpleScaling"
                        },
                        "adjustment_type": {
                            "type": "string",
                            "description": "Tipo de ajuste (ChangeInCapacity, ExactCapacity, PercentChangeInCapacity)",
                            "enum": ["ChangeInCapacity", "ExactCapacity", "PercentChangeInCapacity"],
                            "default": "ChangeInCapacity"
                        },
                        "scaling_adjustment": {
                            "type": "integer",
                            "description": "Valor del ajuste de escalado",
                            "default": 1
                        },
                        "cooldown": {
                            "type": "integer",
                            "description": "Tiempo de cooldown en segundos",
                            "default": 300
                        }
                    },
                    "required": ["group_name", "policy_name", "policy_type", "adjustment_type", "scaling_adjustment"]
                }
            },
            {
                "name": "delete_scaling_policy",
                "description": "Elimina una política de escalado de un grupo de Auto Scaling",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group_name": {
                            "type": "string",
                            "description": "Nombre del grupo de Auto Scaling"
                        },
                        "policy_name": {
                            "type": "string",
                            "description": "Nombre de la política a eliminar"
                        }
                    },
                    "required": ["group_name", "policy_name"]
                }
            },
            {
                "name": "upload_s3_object",
                "description": "Sube un objeto a un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "object_key": {
                            "type": "string",
                            "description": "Clave del objeto en S3 (ruta/nombre)"
                        },
                        "file_content": {
                            "type": "string",
                            "description": "Contenido del archivo como string base64"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Tipo MIME del contenido (opcional)",
                            "default": "application/octet-stream"
                        }
                    },
                    "required": ["bucket_name", "object_key", "file_content"]
                }
            },
            {
                "name": "delete_s3_object",
                "description": "Elimina un objeto de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "object_key": {
                            "type": "string",
                            "description": "Clave del objeto a eliminar"
                        }
                    },
                    "required": ["bucket_name", "object_key"]
                }
            },
            {
                "name": "get_s3_bucket_policy",
                "description": "Obtiene la política de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        }
                    },
                    "required": ["bucket_name"]
                }
            },
            {
                "name": "put_s3_bucket_policy",
                "description": "Establece la política de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "policy": {
                            "type": "string",
                            "description": "Política del bucket en formato JSON"
                        }
                    },
                    "required": ["bucket_name", "policy"]
                }
            },
            {
                "name": "get_s3_bucket_lifecycle",
                "description": "Obtiene la configuración de lifecycle de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        }
                    },
                    "required": ["bucket_name"]
                }
            },
            {
                "name": "put_s3_bucket_lifecycle",
                "description": "Establece la configuración de lifecycle de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "lifecycle_config": {
                            "type": "string",
                            "description": "Configuración de lifecycle en formato JSON"
                        }
                    },
                    "required": ["bucket_name", "lifecycle_config"]
                }
            },
            {
                "name": "enable_s3_bucket_versioning",
                "description": "Habilita o deshabilita el versionado de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "status": {
                            "type": "string",
                            "description": "Estado del versionado",
                            "enum": ["Enabled", "Suspended"]
                        }
                    },
                    "required": ["bucket_name", "status"]
                }
            },
            {
                "name": "get_s3_bucket_cors",
                "description": "Obtiene la configuración CORS de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        }
                    },
                    "required": ["bucket_name"]
                }
            },
            {
                "name": "put_s3_bucket_cors",
                "description": "Establece la configuración CORS de un bucket S3",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3"
                        },
                        "cors_config": {
                            "type": "string",
                            "description": "Configuración CORS en formato JSON"
                        }
                    },
                    "required": ["bucket_name", "cors_config"]
                }
            },
            {
                "name": "list_efs_file_systems",
                "description": "Lista todos los file systems EFS en la cuenta AWS",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_efs_file_system",
                "description": "Crea un nuevo file system EFS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "creation_token": {
                            "type": "string",
                            "description": "Token único para identificar el file system"
                        },
                        "performance_mode": {
                            "type": "string",
                            "description": "Modo de rendimiento",
                            "enum": ["generalPurpose", "maxIO"],
                            "default": "generalPurpose"
                        },
                        "throughput_mode": {
                            "type": "string",
                            "description": "Modo de throughput",
                            "enum": ["bursting", "provisioned"],
                            "default": "bursting"
                        },
                        "provisioned_throughput": {
                            "type": "number",
                            "description": "Throughput provisionado en MiB/s (solo para modo provisioned)",
                            "minimum": 0.1
                        }
                    },
                    "required": ["creation_token"]
                }
            },
            {
                "name": "delete_efs_file_system",
                "description": "Elimina un file system EFS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_system_id": {
                            "type": "string",
                            "description": "ID del file system EFS a eliminar"
                        }
                    },
                    "required": ["file_system_id"]
                }
            },
            {
                "name": "create_efs_mount_target",
                "description": "Crea un mount target para un file system EFS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_system_id": {
                            "type": "string",
                            "description": "ID del file system EFS"
                        },
                        "subnet_id": {
                            "type": "string",
                            "description": "ID de la subnet donde crear el mount target"
                        },
                        "ip_address": {
                            "type": "string",
                            "description": "Dirección IP específica para el mount target (opcional)"
                        },
                        "security_groups": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de IDs de security groups (opcional)"
                        }
                    },
                    "required": ["file_system_id", "subnet_id"]
                }
            },
            {
                "name": "delete_efs_mount_target",
                "description": "Elimina un mount target EFS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mount_target_id": {
                            "type": "string",
                            "description": "ID del mount target a eliminar"
                        }
                    },
                    "required": ["mount_target_id"]
                }
            },
            {
                "name": "list_fsx_file_systems",
                "description": "Lista todos los file systems FSx en la cuenta AWS",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_fsx_file_system",
                "description": "Crea un nuevo file system FSx",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_system_type": {
                            "type": "string",
                            "description": "Tipo de file system",
                            "enum": ["LUSTRE", "WINDOWS", "ONTAP", "OPENZFS"],
                            "default": "LUSTRE"
                        },
                        "storage_capacity": {
                            "type": "integer",
                            "description": "Capacidad de almacenamiento en GB",
                            "minimum": 32,
                            "default": 1200
                        },
                        "subnet_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de IDs de subnets"
                        },
                        "security_group_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de IDs de security groups"
                        },
                        "deployment_type": {
                            "type": "string",
                            "description": "Tipo de despliegue para Lustre",
                            "enum": ["PERSISTENT_1", "PERSISTENT_2", "SCRATCH_1", "SCRATCH_2"]
                        },
                        "per_unit_storage_throughput": {
                            "type": "integer",
                            "description": "Throughput por unidad para Lustre",
                            "enum": [50, 100, 200]
                        }
                    },
                    "required": ["file_system_type", "storage_capacity"]
                }
            },
            {
                "name": "delete_fsx_file_system",
                "description": "Elimina un file system FSx",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_system_id": {
                            "type": "string",
                            "description": "ID del file system FSx a eliminar"
                        }
                    },
                    "required": ["file_system_id"]
                }
            },
            {
                "name": "describe_stack_events",
                "description": "Obtiene los eventos de un stack de CloudFormation para monitorear su estado y progreso",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stack_name": {
                            "type": "string",
                            "description": "Nombre o ID del stack de CloudFormation"
                        }
                    },
                    "required": ["stack_name"]
                }
            },
            {
                "name": "describe_stack_resources",
                "description": "Obtiene información detallada sobre los recursos de un stack de CloudFormation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stack_name": {
                            "type": "string",
                            "description": "Nombre o ID del stack de CloudFormation"
                        }
                    },
                    "required": ["stack_name"]
                }
            }
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles"""
        return self.tools
    
    def _convert_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte parámetros de Gemini a tipos Python nativos (recursivamente)"""
        def convert_value(value):
            if isinstance(value, float) and value.is_integer():
                # Convertir floats enteros a int
                return int(value)
            elif isinstance(value, list):
                # Convertir listas recursivamente
                return [convert_value(v) for v in value]
            elif isinstance(value, dict):
                # Convertir diccionarios recursivamente
                return {k: convert_value(v) for k, v in value.items()}
            else:
                return value
        
        return {key: convert_value(value) for key, value in params.items()}
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica"""
        try:
            # Convertir parámetros a tipos nativos
            converted_params = self._convert_params(parameters)
            
            method = getattr(self, f"_execute_{tool_name}")
            result = method(converted_params)
            return {"success": True, "result": result}
        except AttributeError:
            return {"success": False, "error": f"Herramienta '{tool_name}' no encontrada"}
        except Exception as e:
            logger.exception(f"Error ejecutando {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    # Implementación de herramientas
    
    def _execute_create_ec2_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una instancia EC2 con VPC y seguridad"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        # Crear VPC si se solicita
        vpc_id = None
        subnet_id = None
        security_group_id = None
        
        if params.get('create_vpc', True):
            # Crear VPC
            vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
            vpc_id = vpc_response['Vpc']['VpcId']
            
            # Tag VPC
            ec2.create_tags(
                Resources=[vpc_id],
                Tags=[
                    {'Key': 'Name', 'Value': f"vpc-{params['environment']}"},
                    {'Key': 'Environment', 'Value': params['environment']}
                ]
            )
            
            # Crear subnet
            subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock='10.0.1.0/24')
            subnet_id = subnet_response['Subnet']['SubnetId']
            
            # Crear security group restrictivo
            # Nota: Los nombres de security groups NO pueden empezar con "sg-"
            sg_response = ec2.create_security_group(
                GroupName=f"secgrp-{params['environment']}-{vpc_id[-8:]}",
                Description=f"Security group for {params['environment']} environment",
                VpcId=vpc_id
            )
            security_group_id = sg_response['GroupId']
            
            # Reglas de seguridad mínimas (solo SSH desde IP específica)
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH access'}]
                    }
                ]
            )
        
        # Crear instancia
        # AMI por defecto: Amazon Linux 2023 kernel-6.1 (x86_64)
        instance_params = {
            'ImageId': params.get('ami_id', 'ami-0157af9aea2eef346'),  # Amazon Linux 2023
            'InstanceType': params.get('instance_type', 't2.micro'),
            'MinCount': 1,
            'MaxCount': 1,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': f"instance-{params['environment']}"},
                        {'Key': 'Environment', 'Value': params['environment']},
                        {'Key': 'ManagedBy', 'Value': 'AWS-Control-Panel'}
                    ]
                }
            ]
        }
        
        if subnet_id:
            instance_params['SubnetId'] = subnet_id
        if security_group_id:
            instance_params['SecurityGroupIds'] = [security_group_id]
        if params.get('key_name'):
            instance_params['KeyName'] = params['key_name']
        
        response = ec2.run_instances(**instance_params)
        instance_id = response['Instances'][0]['InstanceId']
        
        return {
            'instance_id': instance_id,
            'vpc_id': vpc_id,
            'subnet_id': subnet_id,
            'security_group_id': security_group_id,
            'environment': params['environment'],
            'message': f"Instancia EC2 creada exitosamente con configuración segura"
        }
    
    def _execute_list_ec2_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista instancias EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        filters = params.get('filters', {})
        response = ec2.describe_instances(Filters=[
            {'Name': k, 'Values': [v]} for k, v in filters.items()
        ] if filters else [])
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Convertir tags a formato serializable
                tags = {}
                for tag in instance.get('Tags', []):
                    tags[tag['Key']] = tag['Value']
                
                # Obtener nombre de la instancia
                instance_name = tags.get('Name', 'N/A')
                
                instances.append({
                    'instance_id': instance['InstanceId'],
                    'name': instance_name,
                    'state': instance['State']['Name'],
                    'type': instance['InstanceType'],
                    'public_ip': instance.get('PublicIpAddress', 'N/A'),
                    'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                    'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else 'N/A',
                    'tags': tags  # Diccionario simple Key: Value
                })
        
        return {'instances': instances, 'count': len(instances)}
    
    def _execute_stop_ec2_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detiene una instancia EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        instance_id = str(params['instance_id'])
        response = ec2.stop_instances(InstanceIds=[instance_id])
        return {
            'instance_id': instance_id,
            'state': str(response['StoppingInstances'][0]['CurrentState']['Name']),
            'message': f"Instancia {instance_id} detenida"
        }
    
    def _execute_start_ec2_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia una instancia EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            instance_id = str(params['instance_id'])
            response = ec2.start_instances(InstanceIds=[instance_id])
            return {
                'instance_id': instance_id,
                'state': str(response['StartingInstances'][0]['CurrentState']['Name']),
                'previous_state': str(response['StartingInstances'][0]['PreviousState']['Name']),
                'message': f"Instancia {instance_id} iniciada"
            }
        except Exception as e:
            logger.exception(f"Error iniciando instancia: {e}")
            return {
                'error': str(e),
                'instance_id': str(params.get('instance_id', 'unknown')),
                'message': f"Error al iniciar instancia: {str(e)}"
            }
    
    def _execute_modify_instance_security_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modifica los security groups de una instancia EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            instance_id = params['instance_id']
            # Convertir security_group_ids a lista de strings
            security_group_ids = params['security_group_ids']
            if not isinstance(security_group_ids, list):
                security_group_ids = list(security_group_ids)
            # Asegurar que son strings
            security_group_ids = [str(sg_id) for sg_id in security_group_ids]
            
            # Verificar que la instancia existe y obtener su estado
            instances = ec2.describe_instances(InstanceIds=[instance_id])
            if not instances['Reservations']:
                return {
                    'error': 'Instance not found',
                    'message': f"La instancia {instance_id} no existe"
                }
            
            instance = instances['Reservations'][0]['Instances'][0]
            instance_state = str(instance['State']['Name'])
            current_sgs = [str(sg['GroupId']) for sg in instance.get('SecurityGroups', [])]
            
            # Verificar que los security groups existen
            try:
                sg_response = ec2.describe_security_groups(GroupIds=security_group_ids)
                sg_names = [str(sg['GroupName']) for sg in sg_response['SecurityGroups']]
            except Exception as e:
                return {
                    'error': str(e),
                    'message': "Uno o más security groups no existen o no son válidos"
                }
            
            # Modificar los security groups
            # Nota: modify_instance_attribute funciona con la instancia running o stopped
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                Groups=security_group_ids
            )
            
            return {
                'instance_id': str(instance_id),
                'instance_state': instance_state,
                'previous_security_groups': current_sgs,
                'new_security_groups': security_group_ids,
                'security_group_names': sg_names,
                'message': f"Security groups actualizados exitosamente para instancia {instance_id}. Estado de la instancia: {instance_state}"
            }
            
        except Exception as e:
            logger.exception(f"Error modificando security groups: {e}")
            return {
                'error': str(e),
                'instance_id': str(params.get('instance_id', 'unknown')),
                'message': f"Error al modificar security groups: {str(e)}"
            }
    
    def _execute_terminate_ec2_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Termina una instancia EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        instance_id = str(params['instance_id'])
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        return {
            'instance_id': instance_id,
            'state': str(response['TerminatingInstances'][0]['CurrentState']['Name']),
            'message': f"Instancia {instance_id} terminada"
        }
    
    def _execute_create_secure_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una VPC segura"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            vpc_response = ec2.create_vpc(CidrBlock=params.get('cidr_block', '10.0.0.0/16'))
            vpc_id = vpc_response['Vpc']['VpcId']
            
            # Habilitar DNS
            if params.get('enable_dns', True):
                ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
                ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
            
            # Tag VPC
            ec2.create_tags(
                Resources=[vpc_id],
                Tags=[{'Key': 'Name', 'Value': params['vpc_name']}]
            )
            
            return {
                'vpc_id': vpc_id,
                'cidr_block': params.get('cidr_block', '10.0.0.0/16'),
                'message': f"VPC '{params['vpc_name']}' creada exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error creando VPC: {e}")
            return {
                'error': str(e),
                'vpc_name': str(params.get('vpc_name', 'unknown')),
                'message': f"Error al crear VPC: {str(e)}"
            }

    def _execute_create_subnet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una subnet"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            subnet_params = {
                'VpcId': params['vpc_id'],
                'CidrBlock': params['cidr_block']
            }

            if params.get('availability_zone'):
                subnet_params['AvailabilityZone'] = params['availability_zone']

            response = ec2.create_subnet(**subnet_params)
            subnet_id = response['Subnet']['SubnetId']

            return {
                'subnet_id': subnet_id,
                'vpc_id': params['vpc_id'],
                'cidr_block': params['cidr_block'],
                'availability_zone': params.get('availability_zone', 'N/A'),
                'message': f"Subnet {subnet_id} creada exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear subnet: {str(e)}"
            }

    def _execute_delete_subnet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una subnet"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            ec2.delete_subnet(SubnetId=params['subnet_id'])

            return {
                'subnet_id': params['subnet_id'],
                'message': f"Subnet {params['subnet_id']} eliminada exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'subnet_id': params.get('subnet_id', 'unknown'),
                'message': f"Error al eliminar subnet: {str(e)}"
            }

    def _execute_list_route_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista route tables"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            filters = []
            if params.get('vpc_id'):
                filters.append({'Name': 'vpc-id', 'Values': [params['vpc_id']]})

            response = ec2.describe_route_tables(Filters=filters)

            route_tables = []
            for rt in response['RouteTables']:
                route_tables.append({
                    'route_table_id': rt['RouteTableId'],
                    'vpc_id': rt['VpcId'],
                    'associations': len(rt.get('Associations', [])),
                    'routes': len(rt.get('Routes', []))
                })

            return {
                'route_tables': route_tables,
                'count': len(route_tables),
                'message': f"Encontradas {len(route_tables)} route tables"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al listar route tables: {str(e)}"
            }

    def _execute_create_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una route table"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            response = ec2.create_route_table(VpcId=params['vpc_id'])
            route_table_id = response['RouteTable']['RouteTableId']

            return {
                'route_table_id': route_table_id,
                'vpc_id': params['vpc_id'],
                'message': f"Route table {route_table_id} creada exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear route table: {str(e)}"
            }

    def _execute_associate_route_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Asocia una route table a una subnet"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            response = ec2.associate_route_table(
                RouteTableId=params['route_table_id'],
                SubnetId=params['subnet_id']
            )
            association_id = response['AssociationId']

            return {
                'association_id': association_id,
                'route_table_id': params['route_table_id'],
                'subnet_id': params['subnet_id'],
                'message': f"Route table asociada exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al asociar route table: {str(e)}"
            }

    def _execute_create_route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una ruta en una route table"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            route_params = {
                'RouteTableId': params['route_table_id'],
                'DestinationCidrBlock': params['destination_cidr_block'],
                'GatewayId': params['gateway_id']
            }

            ec2.create_route(**route_params)

            return {
                'route_table_id': params['route_table_id'],
                'destination_cidr_block': params['destination_cidr_block'],
                'gateway_id': params['gateway_id'],
                'message': f"Ruta creada exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear ruta: {str(e)}"
            }

    def _execute_list_internet_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista internet gateways"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            response = ec2.describe_internet_gateways()

            internet_gateways = []
            for igw in response['InternetGateways']:
                attachments = igw.get('Attachments', [])
                vpc_id = attachments[0].get('VpcId', 'N/A') if attachments else 'N/A'
                state = attachments[0].get('State', 'detached') if attachments else 'detached'

                internet_gateways.append({
                    'internet_gateway_id': igw['InternetGatewayId'],
                    'state': state,
                    'vpc_id': vpc_id
                })

            return {
                'internet_gateways': internet_gateways,
                'count': len(internet_gateways),
                'message': f"Encontrados {len(internet_gateways)} internet gateways"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al listar internet gateways: {str(e)}"
            }

    def _execute_create_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un internet gateway"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            response = ec2.create_internet_gateway()
            internet_gateway_id = response['InternetGateway']['InternetGatewayId']

            return {
                'internet_gateway_id': internet_gateway_id,
                'message': f"Internet Gateway {internet_gateway_id} creado exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear internet gateway: {str(e)}"
            }

    def _execute_attach_internet_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adjunta un internet gateway a una VPC"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            ec2.attach_internet_gateway(
                InternetGatewayId=params['internet_gateway_id'],
                VpcId=params['vpc_id']
            )

            return {
                'internet_gateway_id': params['internet_gateway_id'],
                'vpc_id': params['vpc_id'],
                'message': f"Internet Gateway adjuntado exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al adjuntar internet gateway: {str(e)}"
            }

    def _execute_list_nat_gateways(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista NAT gateways"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            filters = []
            if params.get('vpc_id'):
                filters.append({'Name': 'vpc-id', 'Values': [params['vpc_id']]})

            response = ec2.describe_nat_gateways(Filters=filters)

            nat_gateways = []
            for nat in response['NatGateways']:
                nat_gateways.append({
                    'nat_gateway_id': nat['NatGatewayId'],
                    'state': nat['State'],
                    'vpc_id': nat['VpcId'],
                    'subnet_id': nat['SubnetId'],
                    'connectivity_type': nat.get('ConnectivityType', 'public')
                })

            return {
                'nat_gateways': nat_gateways,
                'count': len(nat_gateways),
                'message': f"Encontrados {len(nat_gateways)} NAT gateways"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al listar NAT gateways: {str(e)}"
            }

    def _execute_create_nat_gateway(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un NAT gateway"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            nat_params = {
                'SubnetId': params['subnet_id'],
                'ConnectivityType': params.get('connectivity_type', 'public')
            }

            if params.get('allocation_id') and params.get('connectivity_type', 'public') == 'public':
                nat_params['AllocationId'] = params['allocation_id']

            response = ec2.create_nat_gateway(**nat_params)
            nat_gateway_id = response['NatGateway']['NatGatewayId']

            return {
                'nat_gateway_id': nat_gateway_id,
                'subnet_id': params['subnet_id'],
                'connectivity_type': params.get('connectivity_type', 'public'),
                'message': f"NAT Gateway {nat_gateway_id} creado exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear NAT gateway: {str(e)}"
            }

    def _execute_create_vpc_peering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una conexión VPC peering"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            peering_params = {
                'VpcId': params['vpc_id'],
                'PeerVpcId': params['peer_vpc_id']
            }

            if params.get('peer_owner_id'):
                peering_params['PeerOwnerId'] = params['peer_owner_id']

            response = ec2.create_vpc_peering_connection(**peering_params)
            peering_id = response['VpcPeeringConnection']['VpcPeeringConnectionId']

            return {
                'vpc_peering_connection_id': peering_id,
                'requester_vpc_id': params['vpc_id'],
                'accepter_vpc_id': params['peer_vpc_id'],
                'message': f"VPC Peering {peering_id} creado exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'message': f"Error al crear VPC peering: {str(e)}"
            }

    def _execute_accept_vpc_peering(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Acepta una conexión VPC peering"""
        try:
            ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            ec2.accept_vpc_peering_connection(
                VpcPeeringConnectionId=params['vpc_peering_connection_id']
            )

            return {
                'vpc_peering_connection_id': params['vpc_peering_connection_id'],
                'message': f"VPC Peering aceptado exitosamente"
            }
        except Exception as e:
            return {
                'error': str(e),
                'vpc_peering_connection_id': params.get('vpc_peering_connection_id', 'unknown'),
                'message': f"Error al aceptar VPC peering: {str(e)}"
            }

    def _execute_create_security_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un grupo de seguridad"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            # Verificar si el security group ya existe
            existing_groups = ec2.describe_security_groups(
                Filters=[
                    {'Name': 'group-name', 'Values': [params['group_name']]},
                    {'Name': 'vpc-id', 'Values': [params['vpc_id']]}
                ]
            )
            
            if existing_groups['SecurityGroups']:
                security_group_id = existing_groups['SecurityGroups'][0]['GroupId']
                return {
                    'security_group_id': security_group_id,
                    'already_exists': True,
                    'message': f"Security group '{params['group_name']}' ya existe (ID: {security_group_id})"
                }
            
            # Crear security group
            sg_response = ec2.create_security_group(
                GroupName=params['group_name'],
                Description=params.get('description', 'Security group created by AWS Control Panel'),
                VpcId=params['vpc_id']
            )
            security_group_id = sg_response['GroupId']
            
            # Agregar reglas si se especifican puertos
            if params.get('allowed_ports'):
                ip_permissions = []
                for port in params['allowed_ports']:
                    # Asegurar que el puerto sea int (no float)
                    port_int = int(port) if isinstance(port, float) else port
                    ip_permissions.append({
                        'IpProtocol': 'tcp',
                        'FromPort': port_int,
                        'ToPort': port_int,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    })
                
                ec2.authorize_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=ip_permissions
                )
            
            return {
                'security_group_id': security_group_id,
                'already_exists': False,
                'message': f"Security group '{params['group_name']}' creado exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error creando security group: {e}")
            return {
                'error': str(e),
                'message': f"Error al crear security group: {str(e)}"
            }
    
    def _execute_create_s3_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un bucket S3 seguro"""
        try:
            region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            s3 = boto3.client('s3', region_name=region)
            
            bucket_name = str(params['bucket_name'])
            
            # Crear bucket (us-east-1 no necesita LocationConstraint)
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            # Habilitar versionado
            enable_versioning = params.get('enable_versioning', True)
            if enable_versioning:
                s3.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            
            # Habilitar encriptación
            enable_encryption = params.get('enable_encryption', True)
            if enable_encryption:
                s3.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
                    }
                )
            
            # Bloquear acceso público
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            return {
                'bucket_name': bucket_name,
                'region': region,
                'versioning': enable_versioning,
                'encryption': enable_encryption,
                'public_access_blocked': True,
                'message': f"Bucket S3 '{bucket_name}' creado exitosamente en {region} con configuración segura"
            }
            
        except Exception as e:
            logger.exception(f"Error creando bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al crear bucket S3: {str(e)}"
            }
    
    def _execute_delete_s3_bucket(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un bucket S3 (opcionalmente vaciándolo primero)"""
        try:
            region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            s3 = boto3.client('s3', region_name=region)
            bucket_name = str(params['bucket_name'])
            force = params.get('force', False)
            
            # Verificar si el bucket existe
            try:
                s3.head_bucket(Bucket=bucket_name)
            except Exception as e:
                return {
                    'error': 'Bucket no encontrado',
                    'bucket_name': bucket_name,
                    'message': f"El bucket '{bucket_name}' no existe"
                }
            
            # Si force=True, eliminar todos los objetos primero
            objects_deleted = 0
            if force:
                try:
                    # Listar y eliminar todos los objetos
                    paginator = s3.get_paginator('list_objects_v2')
                    for page in paginator.paginate(Bucket=bucket_name):
                        if 'Contents' in page:
                            objects = [{'Key': obj['Key']} for obj in page['Contents']]
                            if objects:
                                s3.delete_objects(
                                    Bucket=bucket_name,
                                    Delete={'Objects': objects}
                                )
                                objects_deleted += len(objects)
                    
                    # Eliminar versiones si el versionado está habilitado
                    version_paginator = s3.get_paginator('list_object_versions')
                    for page in version_paginator.paginate(Bucket=bucket_name):
                        versions = []
                        if 'Versions' in page:
                            versions.extend([{'Key': v['Key'], 'VersionId': v['VersionId']} 
                                           for v in page['Versions']])
                        if 'DeleteMarkers' in page:
                            versions.extend([{'Key': d['Key'], 'VersionId': d['VersionId']} 
                                           for d in page['DeleteMarkers']])
                        
                        if versions:
                            s3.delete_objects(
                                Bucket=bucket_name,
                                Delete={'Objects': versions}
                            )
                            objects_deleted += len(versions)
                            
                except Exception as e:
                    logger.warning(f"Error eliminando objetos del bucket: {e}")
            
            # Eliminar el bucket
            try:
                s3.delete_bucket(Bucket=bucket_name)
                return {
                    'bucket_name': bucket_name,
                    'objects_deleted': objects_deleted,
                    'force': force,
                    'message': f"Bucket S3 '{bucket_name}' eliminado exitosamente" + 
                              (f" ({objects_deleted} objetos eliminados)" if objects_deleted > 0 else "")
                }
            except Exception as e:
                error_msg = str(e)
                if 'BucketNotEmpty' in error_msg:
                    return {
                        'error': 'Bucket no está vacío',
                        'bucket_name': bucket_name,
                        'message': f"El bucket '{bucket_name}' no está vacío. Usa force=true para eliminar todos los objetos primero."
                    }
                else:
                    raise
                    
        except Exception as e:
            logger.exception(f"Error eliminando bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al eliminar bucket S3: {str(e)}"
            }
    
    def _execute_upload_s3_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sube un objeto a un bucket S3"""
        try:
            import base64
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            object_key = str(params['object_key'])
            file_content = base64.b64decode(params['file_content'])
            content_type = params.get('content_type', 'application/octet-stream')
            
            s3.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=file_content,
                ContentType=content_type
            )
            
            return {
                'bucket_name': bucket_name,
                'object_key': object_key,
                'content_type': content_type,
                'size': len(file_content),
                'message': f"Objeto '{object_key}' subido exitosamente al bucket '{bucket_name}'"
            }
            
        except Exception as e:
            logger.exception(f"Error subiendo objeto S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'object_key': str(params.get('object_key', 'unknown')),
                'message': f"Error al subir objeto S3: {str(e)}"
            }
    
    def _execute_delete_s3_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un objeto de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            object_key = str(params['object_key'])
            
            s3.delete_object(Bucket=bucket_name, Key=object_key)
            
            return {
                'bucket_name': bucket_name,
                'object_key': object_key,
                'message': f"Objeto '{object_key}' eliminado exitosamente del bucket '{bucket_name}'"
            }
            
        except Exception as e:
            logger.exception(f"Error eliminando objeto S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'object_key': str(params.get('object_key', 'unknown')),
                'message': f"Error al eliminar objeto S3: {str(e)}"
            }
    
    def _execute_get_s3_bucket_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene la política de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            policy = s3.get_bucket_policy(Bucket=bucket_name)
            policy_document = json.loads(policy['Policy'])
            
            return {
                'bucket_name': bucket_name,
                'policy': policy_document,
                'message': f"Política del bucket '{bucket_name}' obtenida exitosamente"
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'NoSuchBucketPolicy' in error_msg:
                return {
                    'bucket_name': str(params.get('bucket_name', 'unknown')),
                    'policy': None,
                    'message': f"El bucket no tiene política configurada"
                }
            logger.exception(f"Error obteniendo política del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al obtener política del bucket S3: {str(e)}"
            }
    
    def _execute_put_s3_bucket_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Establece la política de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            policy_text = str(params['policy'])
            policy_document = json.loads(policy_text)
            
            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy_document)
            )
            
            return {
                'bucket_name': bucket_name,
                'message': f"Política del bucket '{bucket_name}' actualizada exitosamente"
            }
            
        except json.JSONDecodeError as e:
            return {
                'error': f"JSON inválido: {str(e)}",
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"La política debe ser un JSON válido"
            }
        except Exception as e:
            logger.exception(f"Error actualizando política del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al actualizar política del bucket S3: {str(e)}"
            }
    
    def _execute_get_s3_bucket_lifecycle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene la configuración de lifecycle de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            lifecycle = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            
            return {
                'bucket_name': bucket_name,
                'lifecycle_rules': lifecycle.get('Rules', []),
                'message': f"Configuración de lifecycle del bucket '{bucket_name}' obtenida exitosamente"
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'NoSuchLifecycleConfiguration' in error_msg:
                return {
                    'bucket_name': str(params.get('bucket_name', 'unknown')),
                    'lifecycle_rules': [],
                    'message': f"El bucket no tiene configuración de lifecycle"
                }
            logger.exception(f"Error obteniendo lifecycle del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al obtener lifecycle del bucket S3: {str(e)}"
            }
    
    def _execute_put_s3_bucket_lifecycle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Establece la configuración de lifecycle de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            lifecycle_config_text = str(params['lifecycle_config'])
            lifecycle_config = json.loads(lifecycle_config_text)
            
            s3.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            
            return {
                'bucket_name': bucket_name,
                'message': f"Configuración de lifecycle del bucket '{bucket_name}' actualizada exitosamente"
            }
            
        except json.JSONDecodeError as e:
            return {
                'error': f"JSON inválido: {str(e)}",
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"La configuración debe ser un JSON válido"
            }
        except Exception as e:
            logger.exception(f"Error actualizando lifecycle del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al actualizar lifecycle del bucket S3: {str(e)}"
            }
    
    def _execute_enable_s3_bucket_versioning(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Habilita o deshabilita el versionado de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            status = str(params['status'])
            
            if status not in ['Enabled', 'Suspended']:
                return {
                    'error': 'Estado inválido',
                    'bucket_name': bucket_name,
                    'message': "El estado debe ser 'Enabled' o 'Suspended'"
                }
            
            s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': status}
            )
            
            status_text = 'habilitado' if status == 'Enabled' else 'suspendido'
            return {
                'bucket_name': bucket_name,
                'versioning_status': status,
                'message': f"Versionado del bucket '{bucket_name}' {status_text} exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error cambiando versionado del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al cambiar versionado del bucket S3: {str(e)}"
            }
    
    def _execute_get_s3_bucket_cors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene la configuración CORS de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            cors = s3.get_bucket_cors(Bucket=bucket_name)
            
            return {
                'bucket_name': bucket_name,
                'cors_rules': cors.get('CORSRules', []),
                'message': f"Configuración CORS del bucket '{bucket_name}' obtenida exitosamente"
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'NoSuchCORSConfiguration' in error_msg:
                return {
                    'bucket_name': str(params.get('bucket_name', 'unknown')),
                    'cors_rules': [],
                    'message': f"El bucket no tiene configuración CORS"
                }
            logger.exception(f"Error obteniendo CORS del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al obtener CORS del bucket S3: {str(e)}"
            }
    
    def _execute_put_s3_bucket_cors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Establece la configuración CORS de un bucket S3"""
        try:
            s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            bucket_name = str(params['bucket_name'])
            cors_config_text = str(params['cors_config'])
            cors_config = json.loads(cors_config_text)
            
            s3.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_config
            )
            
            return {
                'bucket_name': bucket_name,
                'message': f"Configuración CORS del bucket '{bucket_name}' actualizada exitosamente"
            }
            
        except json.JSONDecodeError as e:
            return {
                'error': f"JSON inválido: {str(e)}",
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"La configuración debe ser un JSON válido"
            }
        except Exception as e:
            logger.exception(f"Error actualizando CORS del bucket S3: {e}")
            return {
                'error': str(e),
                'bucket_name': str(params.get('bucket_name', 'unknown')),
                'message': f"Error al actualizar CORS del bucket S3: {str(e)}"
            }
    
    def _execute_get_aws_costs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene costos de AWS"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1
            
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            
            costs = []
            for result in response['ResultsByTime']:
                costs.append({
                    'period': f"{result['TimePeriod']['Start']} - {result['TimePeriod']['End']}",
                    'amount': result['Total']['UnblendedCost']['Amount'],
                    'unit': result['Total']['UnblendedCost']['Unit']
                })
            
            return {'costs': costs}
            
        except Exception as e:
            logger.exception(f"Error obteniendo costos AWS: {e}")
            return {
                'error': str(e),
                'costs': [],
                'message': f"Error al obtener costos AWS: {str(e)}"
            }
    
    def _execute_get_cost_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene pronóstico de costos de AWS"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1
            
            response = ce.get_cost_forecast(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY',
                PredictionIntervalLevel=params.get('prediction_interval_level', 80)
            )
            
            forecast = []
            for result in response['ForecastResultsByTime']:
                forecast.append({
                    'period': f"{result['TimePeriod']['Start']} - {result['TimePeriod']['End']}",
                    'amount': result['MeanValue'],
                    'unit': result['Unit'],
                    'prediction_interval_lower': result.get('PredictionIntervalLowerBound'),
                    'prediction_interval_upper': result.get('PredictionIntervalUpperBound')
                })
            
            return {
                'forecast': forecast,
                'prediction_interval_level': params.get('prediction_interval_level', 80)
            }
            
        except Exception as e:
            logger.exception(f"Error obteniendo pronóstico de costos: {e}")
            return {
                'error': str(e),
                'forecast': [],
                'message': f"Error al obtener pronóstico de costos: {str(e)}"
            }
    
    def _execute_get_cost_categories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene categorías de costos por servicio"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1
            
            response = ce.get_cost_and_usage_with_resources(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            categories = []
            max_results = params.get('max_results', 10)
            
            for group in response['ResultsByTime'][0]['Groups'][:max_results]:
                categories.append({
                    'service': group['Keys'][0],
                    'amount': group['Metrics']['UnblendedCost']['Amount'],
                    'unit': group['Metrics']['UnblendedCost']['Unit']
                })
            
            # Ordenar por monto descendente
            categories.sort(key=lambda x: float(x['amount']), reverse=True)
            
            return {
                'categories': categories,
                'total_categories': len(categories)
            }
            
        except Exception as e:
            logger.exception(f"Error obteniendo categorías de costos: {e}")
            return {
                'error': str(e),
                'categories': [],
                'message': f"Error al obtener categorías de costos: {str(e)}"
            }
    
    def _execute_get_savings_plans_utilization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene utilización de Savings Plans"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1
            
            response = ce.get_savings_plans_utilization(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                }
            )
            
            savings_plans = []
            for sp in response['SavingsPlansUtilizationsByTime']:
                savings_plans.append({
                    'period': f"{sp['TimePeriod']['Start']} - {sp['TimePeriod']['End']}",
                    'total_commitment': sp['Total']['TotalCommitment'],
                    'used_commitment': sp['Total']['UsedCommitment'],
                    'unused_commitment': sp['Total']['UnusedCommitment'],
                    'utilization_percentage': sp['Total']['UtilizationPercentage'],
                    'unit': sp['Total']['Unit']
                })
            
            return {
                'savings_plans': savings_plans,
                'total_periods': len(savings_plans)
            }
            
        except Exception as e:
            logger.exception(f"Error obteniendo utilización de Savings Plans: {e}")
            return {
                'error': str(e),
                'savings_plans': [],
                'message': f"Error al obtener utilización de Savings Plans: {str(e)}"
            }
    
    def _execute_search_amis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca AMIs disponibles con filtros específicos"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        # Construir filtros
        filters = []
        
        # Filtro de plataforma
        if params.get('platform') == 'windows':
            filters.append({'Name': 'platform', 'Values': ['windows']})
        else:
            # Para Linux, excluir Windows
            filters.append({'Name': 'platform', 'Values': ['']})
        
        # Filtro de arquitectura
        if params.get('architecture'):
            filters.append({
                'Name': 'architecture',
                'Values': [params['architecture']]
            })
        
        # Filtro de tipo de dispositivo raíz
        if params.get('root_device_type'):
            filters.append({
                'Name': 'root-device-type',
                'Values': [params['root_device_type']]
            })
        
        # Filtro de nombre
        if params.get('name_filter'):
            filters.append({
                'Name': 'name',
                'Values': [params['name_filter']]
            })
        
        # Filtro para solo AMIs disponibles
        filters.append({'Name': 'state', 'Values': ['available']})
        
        # Propietario de la AMI
        owners = [params.get('owner', 'amazon')]
        
        try:
            # Buscar AMIs (describe_images no acepta MaxResults)
            response = ec2.describe_images(
                Owners=owners,
                Filters=filters
            )
            
            # Ordenar por fecha de creación (más recientes primero)
            images = sorted(
                response['Images'],
                key=lambda x: x.get('CreationDate', ''),
                reverse=True
            )
            
            # Limitar resultados manualmente
            max_results = params.get('max_results', 10)
            images = images[:max_results]
            
            # Si no se encontraron imágenes, usar AMI por defecto de Amazon Linux 2023
            if not images:
                # Determinar arquitectura para AMI por defecto
                arch = params.get('architecture', 'x86_64')
                default_ami_id = 'ami-0157af9aea2eef346' if arch == 'x86_64' else 'ami-08203b7a67f23af2c'
                
                logger.info(f"No se encontraron AMIs con los filtros especificados. Usando AMI por defecto: {default_ami_id}")
                
                # Obtener información de la AMI por defecto
                try:
                    default_response = ec2.describe_images(ImageIds=[default_ami_id])
                    if default_response['Images']:
                        images = [default_response['Images'][0]]
                except Exception as e:
                    logger.warning(f"No se pudo obtener información de AMI por defecto: {e}")
                    # Crear entrada manual si falla la consulta
                    images = [{
                        'ImageId': default_ami_id,
                        'Name': 'Amazon Linux 2023 kernel-6.1',
                        'Description': 'AMI de Amazon Linux 2023 con kernel 6.1 (por defecto)',
                        'Architecture': arch,
                        'CreationDate': '2023-01-01T00:00:00.000Z',
                        'OwnerId': 'amazon',
                        'PlatformDetails': 'Linux/UNIX',
                        'RootDeviceType': 'ebs'
                    }]
            
            # Formatear resultados
            ami_list = []
            for img in images:
                ami_list.append({
                    'ami_id': img['ImageId'],
                    'name': img.get('Name', 'N/A'),
                    'description': img.get('Description', 'N/A')[:100],  # Limitar descripción
                    'architecture': img.get('Architecture', 'N/A'),
                    'creation_date': img.get('CreationDate', 'N/A'),
                    'owner': img.get('OwnerId', 'N/A'),
                    'platform': img.get('PlatformDetails', 'Linux'),
                    'root_device_type': img.get('RootDeviceType', 'N/A'),
                    'is_default': img['ImageId'] in ['ami-0157af9aea2eef346', 'ami-08203b7a67f23af2c']
                })
            
            return {
                'total_found': len(images),
                'showing': len(ami_list),
                'amis': ami_list,
                'using_default': len(ami_list) > 0 and ami_list[0].get('is_default', False),
                'filters_applied': {
                    'owner': params.get('owner', 'amazon'),
                    'platform': params.get('platform', 'linux'),
                    'architecture': params.get('architecture', 'x86_64'),
                    'root_device_type': params.get('root_device_type', 'ebs'),
                    'name_filter': params.get('name_filter', 'any')
                }
            }
            
        except Exception as e:
            logger.exception(f"Error buscando AMIs: {e}")
            return {
                'error': str(e),
                'amis': []
            }
    
    def _execute_list_vpcs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todas las VPCs disponibles"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            # Filtrar por VPC IDs si se proporcionan
            if params.get('vpc_ids'):
                response = ec2.describe_vpcs(VpcIds=params['vpc_ids'])
            else:
                response = ec2.describe_vpcs()
            
            vpc_list = []
            for vpc in response['Vpcs']:
                # Extraer nombre de tags
                name = 'N/A'
                if 'Tags' in vpc:
                    for tag in vpc['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                
                vpc_list.append({
                    'vpc_id': vpc['VpcId'],
                    'name': name,
                    'state': vpc['State'],
                    'cidr_block': vpc['CidrBlock'],
                    'is_default': vpc.get('IsDefault', False),
                    'dhcp_options_id': vpc.get('DhcpOptionsId', 'N/A'),
                    'instance_tenancy': vpc.get('InstanceTenancy', 'default')
                })
            
            return {
                'total_vpcs': len(vpc_list),
                'vpcs': vpc_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando VPCs: {e}")
            return {
                'error': str(e),
                'vpcs': []
            }
    
    def _execute_describe_vpc(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene información detallada de una VPC específica"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            # Obtener información de la VPC
            vpc_response = ec2.describe_vpcs(VpcIds=[params['vpc_id']])
            
            if not vpc_response['Vpcs']:
                return {'error': f"VPC {params['vpc_id']} no encontrada"}
            
            vpc = vpc_response['Vpcs'][0]
            
            # Extraer nombre de tags
            name = 'N/A'
            tags = {}
            if 'Tags' in vpc:
                for tag in vpc['Tags']:
                    tags[tag['Key']] = tag['Value']
                    if tag['Key'] == 'Name':
                        name = tag['Value']
            
            # Obtener subnets
            subnets_response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [params['vpc_id']]}])
            subnets = [{
                'subnet_id': subnet['SubnetId'],
                'cidr_block': subnet['CidrBlock'],
                'availability_zone': subnet['AvailabilityZone'],
                'available_ips': subnet['AvailableIpAddressCount']
            } for subnet in subnets_response['Subnets']]
            
            # Obtener security groups
            sg_response = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [params['vpc_id']]}])
            security_groups = [{
                'group_id': sg['GroupId'],
                'group_name': sg['GroupName'],
                'description': sg['Description']
            } for sg in sg_response['SecurityGroups']]
            
            # Obtener route tables
            rt_response = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [params['vpc_id']]}])
            route_tables = [{
                'route_table_id': rt['RouteTableId'],
                'is_main': any(assoc.get('Main', False) for assoc in rt.get('Associations', []))
            } for rt in rt_response['RouteTables']]
            
            return {
                'vpc_id': vpc['VpcId'],
                'name': name,
                'state': vpc['State'],
                'cidr_block': vpc['CidrBlock'],
                'is_default': vpc.get('IsDefault', False),
                'dhcp_options_id': vpc.get('DhcpOptionsId', 'N/A'),
                'instance_tenancy': vpc.get('InstanceTenancy', 'default'),
                'tags': tags,
                'subnets': subnets,
                'security_groups': security_groups,
                'route_tables': route_tables,
                'total_subnets': len(subnets),
                'total_security_groups': len(security_groups)
            }
            
        except Exception as e:
            logger.exception(f"Error describiendo VPC: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_list_s3_buckets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los buckets S3"""
        s3 = boto3.client('s3', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            response = s3.list_buckets()
            
            bucket_list = []
            for bucket in response['Buckets']:
                # Obtener región del bucket
                try:
                    location = s3.get_bucket_location(Bucket=bucket['Name'])
                    region = location['LocationConstraint'] or 'us-east-1'
                except:
                    region = 'unknown'
                
                bucket_list.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
                    'region': region
                })
            
            return {
                'total_buckets': len(bucket_list),
                'buckets': bucket_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando buckets S3: {e}")
            return {
                'error': str(e),
                'buckets': []
            }
    
    def _execute_list_security_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los grupos de seguridad"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            # Filtrar por VPC si se proporciona
            filters = []
            if params.get('vpc_id'):
                filters.append({'Name': 'vpc-id', 'Values': [params['vpc_id']]})
            
            if filters:
                response = ec2.describe_security_groups(Filters=filters)
            else:
                response = ec2.describe_security_groups()
            
            sg_list = []
            for sg in response['SecurityGroups']:
                # Contar reglas
                inbound_rules = len(sg.get('IpPermissions', []))
                outbound_rules = len(sg.get('IpPermissionsEgress', []))
                
                sg_list.append({
                    'group_id': sg['GroupId'],
                    'group_name': sg['GroupName'],
                    'description': sg['Description'],
                    'vpc_id': sg.get('VpcId', 'N/A'),
                    'inbound_rules': inbound_rules,
                    'outbound_rules': outbound_rules
                })
            
            return {
                'total_security_groups': len(sg_list),
                'security_groups': sg_list,
                'filtered_by_vpc': params.get('vpc_id', 'none')
            }
            
        except Exception as e:
            logger.exception(f"Error listando security groups: {e}")
            return {
                'error': str(e),
                'security_groups': []
            }
    
    def _execute_delete_security_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un grupo de seguridad"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            group_id = params['group_id']
            
            # Verificar que el security group existe
            response = ec2.describe_security_groups(GroupIds=[group_id])
            sg = response['SecurityGroups'][0]
            
            # Eliminar el security group
            ec2.delete_security_group(GroupId=group_id)
            
            return {
                'message': f'Security Group {sg.get("GroupName", group_id)} eliminado exitosamente',
                'group_id': group_id,
                'group_name': sg.get('GroupName')
            }
            
        except Exception as e:
            logger.exception(f"Error eliminando security group {params.get('group_id')}: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_authorize_ingress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Autoriza una regla de entrada (ingress)"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            group_id = params['group_id']
            protocol = params['protocol']
            
            # Construir la regla de entrada
            ip_permissions = [{
                'IpProtocol': protocol,
            }]
            
            # Agregar puertos si no es "todos los protocolos"
            if protocol != '-1':
                if 'port_range_from' in params:
                    ip_permissions[0]['FromPort'] = params['port_range_from']
                if 'port_range_to' in params:
                    ip_permissions[0]['ToPort'] = params['port_range_to']
            
            # Agregar fuente
            source_type = params['source_type']
            source_value = params['source_value']
            
            if source_type == 'cidr':
                ip_permissions[0]['IpRanges'] = [{'CidrIp': source_value}]
                if params.get('description'):
                    ip_permissions[0]['IpRanges'][0]['Description'] = params['description']
            elif source_type == 'security_group':
                ip_permissions[0]['UserIdGroupPairs'] = [{
                    'GroupId': source_value,
                    'Description': params.get('description', '')
                }]
            
            # Autorizar la regla
            ec2.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )
            
            return {
                'message': 'Regla de entrada autorizada exitosamente',
                'group_id': group_id,
                'protocol': protocol,
                'source_type': source_type,
                'source_value': source_value
            }
            
        except Exception as e:
            logger.exception(f"Error autorizando regla de entrada en {params.get('group_id')}: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_revoke_ingress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoca una regla de entrada (ingress)"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            group_id = params['group_id']
            rule_index = params['rule_index']
            
            # Obtener reglas actuales del security group
            response = ec2.describe_security_groups(GroupIds=[group_id])
            security_group = response['SecurityGroups'][0]
            ingress_rules = security_group.get('IpPermissions', [])
            
            if 0 <= rule_index < len(ingress_rules):
                # Revocar la regla específica
                ec2.revoke_security_group_ingress(
                    GroupId=group_id,
                    IpPermissions=[ingress_rules[rule_index]]
                )
                
                return {
                    'message': 'Regla de entrada revocada exitosamente',
                    'group_id': group_id,
                    'rule_index': rule_index
                }
            else:
                return {
                    'error': f'Índice de regla inválido: {rule_index}. Total de reglas: {len(ingress_rules)}'
                }
            
        except Exception as e:
            logger.exception(f"Error revocando regla de entrada en {params.get('group_id')}: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_authorize_egress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Autoriza una regla de salida (egress)"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            group_id = params['group_id']
            protocol = params['protocol']
            
            # Construir la regla de salida
            ip_permissions = [{
                'IpProtocol': protocol,
            }]
            
            # Agregar puertos si no es "todos los protocolos"
            if protocol != '-1':
                if 'port_range_from' in params:
                    ip_permissions[0]['FromPort'] = params['port_range_from']
                if 'port_range_to' in params:
                    ip_permissions[0]['ToPort'] = params['port_range_to']
            
            # Agregar destino
            destination_type = params['destination_type']
            destination_value = params['destination_value']
            
            if destination_type == 'cidr':
                ip_permissions[0]['IpRanges'] = [{'CidrIp': destination_value}]
                if params.get('description'):
                    ip_permissions[0]['IpRanges'][0]['Description'] = params['description']
            elif destination_type == 'security_group':
                ip_permissions[0]['UserIdGroupPairs'] = [{
                    'GroupId': destination_value,
                    'Description': params.get('description', '')
                }]
            
            # Autorizar la regla
            ec2.authorize_security_group_egress(
                GroupId=group_id,
                IpPermissions=ip_permissions
            )
            
            return {
                'message': 'Regla de salida autorizada exitosamente',
                'group_id': group_id,
                'protocol': protocol,
                'destination_type': destination_type,
                'destination_value': destination_value
            }
            
        except Exception as e:
            logger.exception(f"Error autorizando regla de salida en {params.get('group_id')}: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_revoke_egress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Revoca una regla de salida (egress)"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            group_id = params['group_id']
            rule_index = params['rule_index']
            
            # Obtener reglas actuales del security group
            response = ec2.describe_security_groups(GroupIds=[group_id])
            security_group = response['SecurityGroups'][0]
            egress_rules = security_group.get('IpPermissionsEgress', [])
            
            if 0 <= rule_index < len(egress_rules):
                # Revocar la regla específica
                ec2.revoke_security_group_egress(
                    GroupId=group_id,
                    IpPermissions=[egress_rules[rule_index]]
                )
                
                return {
                    'message': 'Regla de salida revocada exitosamente',
                    'group_id': group_id,
                    'rule_index': rule_index
                }
            else:
                return {
                    'error': f'Índice de regla inválido: {rule_index}. Total de reglas: {len(egress_rules)}'
                }
            
        except Exception as e:
            logger.exception(f"Error revocando regla de salida en {params.get('group_id')}: {e}")
            return {
                'error': str(e)
            }
    
    def _execute_list_subnets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista las subnets de una VPC"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            # Filtrar por VPC si se proporciona
            filters = []
            if params.get('vpc_id'):
                filters.append({'Name': 'vpc-id', 'Values': [params['vpc_id']]})
            
            if filters:
                response = ec2.describe_subnets(Filters=filters)
            else:
                response = ec2.describe_subnets()
            
            subnet_list = []
            for subnet in response['Subnets']:
                # Extraer nombre de tags
                name = 'N/A'
                if 'Tags' in subnet:
                    for tag in subnet['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                
                subnet_list.append({
                    'subnet_id': subnet['SubnetId'],
                    'name': name,
                    'vpc_id': subnet['VpcId'],
                    'cidr_block': subnet['CidrBlock'],
                    'availability_zone': subnet['AvailabilityZone'],
                    'available_ip_addresses': subnet['AvailableIpAddressCount'],
                    'state': subnet['State'],
                    'map_public_ip': subnet.get('MapPublicIpOnLaunch', False)
                })
            
            return {
                'total_subnets': len(subnet_list),
                'subnets': subnet_list,
                'filtered_by_vpc': params.get('vpc_id', 'none')
            }
            
        except Exception as e:
            logger.exception(f"Error listando subnets: {e}")
            return {
                'error': str(e),
                'subnets': []
            }
    
    def _execute_create_ami_from_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una AMI desde una instancia EC2"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            response = ec2.create_image(
                InstanceId=params['instance_id'],
                Name=params['ami_name'],
                Description=params.get('description', f"AMI creada desde {params['instance_id']}"),
                NoReboot=params.get('no_reboot', False)
            )
            
            return {
                'ami_id': response['ImageId'],
                'ami_name': params['ami_name'],
                'source_instance': params['instance_id'],
                'message': f"AMI '{params['ami_name']}' creada exitosamente. ID: {response['ImageId']}"
            }
            
        except Exception as e:
            logger.exception(f"Error creando AMI: {e}")
            return {'error': str(e)}
    
    def _execute_list_load_balancers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los load balancers"""
        elbv2 = boto3.client('elbv2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            if params.get('names'):
                response = elbv2.describe_load_balancers(Names=params['names'])
            else:
                response = elbv2.describe_load_balancers()
            
            lb_list = []
            for lb in response['LoadBalancers']:
                lb_list.append({
                    'name': lb['LoadBalancerName'],
                    'arn': lb['LoadBalancerArn'],
                    'dns_name': lb['DNSName'],
                    'type': lb['Type'],
                    'scheme': lb['Scheme'],
                    'state': lb['State']['Code'],
                    'vpc_id': lb['VpcId'],
                    'availability_zones': [az['ZoneName'] for az in lb['AvailabilityZones']]
                })
            
            return {
                'total_load_balancers': len(lb_list),
                'load_balancers': lb_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando load balancers: {e}")
            return {
                'error': str(e),
                'load_balancers': []
            }
    
    def _execute_list_target_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los target groups"""
        elbv2 = boto3.client('elbv2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            if params.get('load_balancer_arn'):
                response = elbv2.describe_target_groups(LoadBalancerArn=params['load_balancer_arn'])
            else:
                response = elbv2.describe_target_groups()
            
            tg_list = []
            for tg in response['TargetGroups']:
                # Obtener health de targets
                health_response = elbv2.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])
                healthy_count = sum(1 for t in health_response['TargetHealthDescriptions'] 
                                  if t['TargetHealth']['State'] == 'healthy')
                total_targets = len(health_response['TargetHealthDescriptions'])
                
                tg_list.append({
                    'name': tg['TargetGroupName'],
                    'arn': tg['TargetGroupArn'],
                    'protocol': tg['Protocol'],
                    'port': tg['Port'],
                    'vpc_id': tg['VpcId'],
                    'health_check_path': tg.get('HealthCheckPath', 'N/A'),
                    'healthy_targets': healthy_count,
                    'total_targets': total_targets
                })
            
            return {
                'total_target_groups': len(tg_list),
                'target_groups': tg_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando target groups: {e}")
            return {
                'error': str(e),
                'target_groups': []
            }
    
    def _execute_create_target_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un target group"""
        elbv2 = boto3.client('elbv2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            create_params = {
                'Name': params['name'],
                'Protocol': params.get('protocol', 'HTTP'),
                'Port': params.get('port', 80),
                'VpcId': params['vpc_id'],
                'TargetType': 'instance'
            }
            
            # Agregar health check solo para HTTP/HTTPS
            if params.get('protocol', 'HTTP') in ['HTTP', 'HTTPS']:
                create_params['HealthCheckPath'] = params.get('health_check_path', '/')
                create_params['HealthCheckProtocol'] = params.get('protocol', 'HTTP')
            
            response = elbv2.create_target_group(**create_params)
            
            tg = response['TargetGroups'][0]
            
            return {
                'target_group_arn': tg['TargetGroupArn'],
                'name': tg['TargetGroupName'],
                'protocol': tg['Protocol'],
                'port': tg['Port'],
                'vpc_id': tg['VpcId'],
                'message': f"Target group '{params['name']}' creado exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error creando target group: {e}")
            return {'error': str(e)}
    
    def _execute_list_autoscaling_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los Auto Scaling Groups"""
        asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            if params.get('names'):
                response = asg.describe_auto_scaling_groups(AutoScalingGroupNames=params['names'])
            else:
                response = asg.describe_auto_scaling_groups()
            
            asg_list = []
            for group in response['AutoScalingGroups']:
                asg_list.append({
                    'name': group['AutoScalingGroupName'],
                    'min_size': group['MinSize'],
                    'max_size': group['MaxSize'],
                    'desired_capacity': group['DesiredCapacity'],
                    'current_instances': len(group['Instances']),
                    'healthy_instances': sum(1 for i in group['Instances'] if i['HealthStatus'] == 'Healthy'),
                    'launch_template': group.get('LaunchTemplate', {}).get('LaunchTemplateId', 'N/A'),
                    'vpc_zones': group['VPCZoneIdentifier'].split(',') if group.get('VPCZoneIdentifier') else [],
                    'target_group_arns': group.get('TargetGroupARNs', []),
                    'health_check_type': group['HealthCheckType']
                })
            
            return {
                'total_autoscaling_groups': len(asg_list),
                'autoscaling_groups': asg_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando Auto Scaling Groups: {e}")
            return {
                'error': str(e),
                'autoscaling_groups': []
            }
    
    def _execute_create_launch_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una Launch Template"""
        ec2 = boto3.client('ec2', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            launch_template_data = {
                'ImageId': params['ami_id'],
                'InstanceType': params.get('instance_type', 't3.micro')
            }
            
            if params.get('key_name'):
                launch_template_data['KeyName'] = params['key_name']
            
            if params.get('security_group_ids'):
                launch_template_data['SecurityGroupIds'] = params['security_group_ids']
            
            if params.get('user_data'):
                import base64
                # Codificar user_data si no está ya codificado
                user_data = params['user_data']
                if not user_data.startswith('IyE'):  # No está en base64
                    user_data = base64.b64encode(user_data.encode()).decode()
                launch_template_data['UserData'] = user_data
            
            response = ec2.create_launch_template(
                LaunchTemplateName=params['template_name'],
                LaunchTemplateData=launch_template_data
            )
            
            template = response['LaunchTemplate']
            
            return {
                'template_id': template['LaunchTemplateId'],
                'template_name': template['LaunchTemplateName'],
                'version': template['LatestVersionNumber'],
                'message': f"Launch Template '{params['template_name']}' creada exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error creando Launch Template: {e}")
            return {'error': str(e)}
    
    def _execute_create_autoscaling_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un Auto Scaling Group"""
        asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            create_params = {
                'AutoScalingGroupName': params['name'],
                'LaunchTemplate': {
                    'LaunchTemplateId': params['launch_template_id']
                },
                'MinSize': params.get('min_size', 1),
                'MaxSize': params.get('max_size', 3),
                'DesiredCapacity': params.get('desired_capacity', 2),
                'VPCZoneIdentifier': ','.join(params['vpc_zone_identifiers']),
                'HealthCheckType': params.get('health_check_type', 'EC2'),
                'HealthCheckGracePeriod': 300
            }
            
            if params.get('target_group_arns'):
                create_params['TargetGroupARNs'] = params['target_group_arns']
            
            asg.create_auto_scaling_group(**create_params)
            
            return {
                'name': params['name'],
                'min_size': params.get('min_size', 1),
                'max_size': params.get('max_size', 3),
                'desired_capacity': params.get('desired_capacity', 2),
                'message': f"Auto Scaling Group '{params['name']}' creado exitosamente"
            }
            
        except Exception as e:
            logger.exception(f"Error creando Auto Scaling Group: {e}")
            return {'error': str(e)}
    
    def _execute_list_rds_instances(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista las instancias RDS"""
        rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            response = rds.describe_db_instances()
            
            instance_list = []
            for instance in response['DBInstances']:
                instance_list.append({
                    'identifier': instance['DBInstanceIdentifier'],
                    'engine': instance['Engine'],
                    'engine_version': instance['EngineVersion'],
                    'instance_class': instance['DBInstanceClass'],
                    'status': instance['DBInstanceStatus'],
                    'endpoint': instance.get('Endpoint', {}).get('Address', 'N/A'),
                    'port': instance.get('Endpoint', {}).get('Port', 'N/A'),
                    'storage_gb': instance['AllocatedStorage'],
                    'multi_az': instance['MultiAZ']
                })
            
            return {
                'total_instances': len(instance_list),
                'rds_instances': instance_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando instancias RDS: {e}")
            return {
                'error': str(e),
                'rds_instances': []
            }
    
    def _execute_list_dynamodb_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista las tablas de DynamoDB"""
        dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        
        try:
            response = dynamodb.list_tables()
            table_names = response.get('TableNames', [])
            
            table_list = []
            for table_name in table_names:
                # Obtener detalles de cada tabla
                table_details = dynamodb.describe_table(TableName=table_name)
                table = table_details['Table']
                
                table_list.append({
                    'name': table['TableName'],
                    'status': table['TableStatus'],
                    'item_count': table.get('ItemCount', 0),
                    'size_bytes': table.get('TableSizeBytes', 0),
                    'creation_date': table['CreationDateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
                })
            
            return {
                'total_tables': len(table_list),
                'dynamodb_tables': table_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando tablas DynamoDB: {e}")
            return {
                'error': str(e),
                'dynamodb_tables': []
            }
    
    def _execute_list_aurora_clusters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los clusters de Amazon Aurora"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            response = rds.describe_db_clusters()
            clusters = response.get('DBClusters', [])
            
            cluster_list = []
            for cluster in clusters:
                # Solo incluir clusters Aurora
                if 'aurora' in cluster.get('Engine', '').lower():
                    cluster_list.append({
                        'cluster_identifier': cluster['DBClusterIdentifier'],
                        'engine': cluster['Engine'],
                        'engine_version': cluster.get('EngineVersion', 'N/A'),
                        'status': cluster['Status'],
                        'endpoint': cluster.get('Endpoint', 'N/A'),
                        'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                        'multi_az': cluster.get('MultiAZ', False),
                        'database_name': cluster.get('DatabaseName', 'N/A'),
                        'master_username': cluster.get('MasterUsername', 'N/A'),
                        'cluster_members': len(cluster.get('DBClusterMembers', [])),
                        'creation_time': str(cluster.get('ClusterCreateTime', 'N/A'))
                    })
            
            return {
                'total_clusters': len(cluster_list),
                'aurora_clusters': cluster_list
            }
            
        except Exception as e:
            logger.exception(f"Error listando clusters Aurora: {e}")
            return {
                'error': str(e),
                'aurora_clusters': []
            }
    
    def _execute_create_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una instancia de base de datos RDS"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_identifier = str(params['db_instance_identifier'])
            engine = params.get('engine', 'mysql')
            instance_class = params.get('instance_class', 'db.t3.micro')
            allocated_storage = int(params.get('allocated_storage', 20))
            master_username = params.get('master_username', 'admin')
            master_password = str(params['master_password'])
            publicly_accessible = params.get('publicly_accessible', False)
            
            # Parámetros de creación
            create_params = {
                'DBInstanceIdentifier': db_identifier,
                'Engine': engine,
                'DBInstanceClass': instance_class,
                'AllocatedStorage': allocated_storage,
                'MasterUsername': master_username,
                'MasterUserPassword': master_password,
                'PubliclyAccessible': publicly_accessible,
                'BackupRetentionPeriod': 7,
                'StorageEncrypted': True
            }
            
            # Security groups si se especifican
            if params.get('vpc_security_group_ids'):
                create_params['VpcSecurityGroupIds'] = [str(sg) for sg in params['vpc_security_group_ids']]
            
            response = rds.create_db_instance(**create_params)
            db_instance = response['DBInstance']
            
            return {
                'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                'engine': db_instance['Engine'],
                'instance_class': db_instance['DBInstanceClass'],
                'status': db_instance['DBInstanceStatus'],
                'endpoint': 'Pendiente (en creación)',
                'master_username': master_username,
                'allocated_storage': allocated_storage,
                'message': f"Instancia RDS '{db_identifier}' creada exitosamente. El endpoint estará disponible cuando el estado sea 'available'."
            }
            
        except Exception as e:
            logger.exception(f"Error creando instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al crear instancia RDS: {str(e)}"
            }
    
    def _execute_modify_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modifica una instancia RDS (instance class, storage, etc.)"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_identifier = str(params['db_instance_identifier'])
            
            # Parámetros de modificación
            modify_params = {}
            
            if params.get('instance_class'):
                modify_params['DBInstanceClass'] = str(params['instance_class'])
            
            if params.get('allocated_storage'):
                modify_params['AllocatedStorage'] = int(params['allocated_storage'])
            
            if params.get('master_password'):
                modify_params['MasterUserPassword'] = str(params['master_password'])
            
            if params.get('backup_retention_period') is not None:
                modify_params['BackupRetentionPeriod'] = int(params['backup_retention_period'])
            
            if params.get('multi_az') is not None:
                modify_params['MultiAZ'] = bool(params['multi_az'])
            
            if not modify_params:
                return {
                    'error': 'No se especificaron parámetros de modificación',
                    'db_instance_identifier': db_identifier
                }
            
            # Aplicar cambios inmediatamente
            modify_params['ApplyImmediately'] = True
            
            response = rds.modify_db_instance(
                DBInstanceIdentifier=db_identifier,
                **modify_params
            )
            
            return {
                'db_instance_identifier': db_identifier,
                'modifications': list(modify_params.keys()),
                'status': 'modifying',
                'message': f"Instancia RDS '{db_identifier}' modificada exitosamente. Los cambios se aplicarán inmediatamente."
            }
            
        except Exception as e:
            logger.exception(f"Error modificando instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al modificar instancia RDS: {str(e)}"
            }
    
    def _execute_reboot_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reinicia una instancia RDS"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_identifier = str(params['db_instance_identifier'])
            
            response = rds.reboot_db_instance(DBInstanceIdentifier=db_identifier)
            
            return {
                'db_instance_identifier': db_identifier,
                'status': 'rebooting',
                'message': f"Instancia RDS '{db_identifier}' reiniciada exitosamente."
            }
            
        except Exception as e:
            logger.exception(f"Error reiniciando instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al reiniciar instancia RDS: {str(e)}"
            }
    
    def _execute_stop_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detiene una instancia RDS (solo instancias, no clusters)"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_identifier = str(params['db_instance_identifier'])
            
            response = rds.stop_db_instance(DBInstanceIdentifier=db_identifier)
            
            return {
                'db_instance_identifier': db_identifier,
                'status': 'stopping',
                'message': f"Instancia RDS '{db_identifier}' detenida exitosamente."
            }
            
        except Exception as e:
            logger.exception(f"Error deteniendo instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al detener instancia RDS: {str(e)}"
            }
    
    def _execute_start_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia una instancia RDS detenida"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_identifier = str(params['db_instance_identifier'])
            
            response = rds.start_db_instance(DBInstanceIdentifier=db_identifier)
            
            return {
                'db_instance_identifier': db_identifier,
                'status': 'starting',
                'message': f"Instancia RDS '{db_identifier}' iniciada exitosamente."
            }
            
        except Exception as e:
            logger.exception(f"Error iniciando instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al iniciar instancia RDS: {str(e)}"
            }
    
    def _execute_create_dynamodb_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una tabla en DynamoDB"""
        try:
            dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            table_name = str(params['table_name'])
            partition_key = str(params['partition_key'])
            partition_key_type = params.get('partition_key_type', 'S')
            billing_mode = params.get('billing_mode', 'PAY_PER_REQUEST')
            
            # Definir esquema de clave
            key_schema = [
                {'AttributeName': partition_key, 'KeyType': 'HASH'}
            ]
            
            attribute_definitions = [
                {'AttributeName': partition_key, 'AttributeType': partition_key_type}
            ]
            
            # Sort key opcional
            if params.get('sort_key'):
                sort_key = str(params['sort_key'])
                sort_key_type = params.get('sort_key_type', 'S')
                key_schema.append({'AttributeName': sort_key, 'KeyType': 'RANGE'})
                attribute_definitions.append({'AttributeName': sort_key, 'AttributeType': sort_key_type})
            
            # Parámetros de creación
            create_params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'BillingMode': billing_mode
            }
            
            # Si es PROVISIONED, agregar capacidad
            if billing_mode == 'PROVISIONED':
                create_params['ProvisionedThroughput'] = {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            
            response = dynamodb.create_table(**create_params)
            table = response['TableDescription']
            
            return {
                'table_name': table['TableName'],
                'status': table['TableStatus'],
                'billing_mode': billing_mode,
                'partition_key': partition_key,
                'sort_key': params.get('sort_key', 'N/A'),
                'creation_date': str(table['CreationDateTime']),
                'message': f"Tabla DynamoDB '{table_name}' creada exitosamente. Estado: {table['TableStatus']}"
            }
            
        except Exception as e:
            logger.exception(f"Error creando tabla DynamoDB: {e}")
            return {
                'error': str(e),
                'table_name': str(params.get('table_name', 'unknown')),
                'message': f"Error al crear tabla DynamoDB: {str(e)}"
            }
    
    # ElastiCache Operations
    def _execute_list_elasticache_clusters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista clusters de ElastiCache"""
        try:
            elasticache = boto3.client('elasticache', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            engine_filter = params.get('engine', 'all')
            
            response = elasticache.describe_cache_clusters(ShowCacheNodeInfo=True)
            
            clusters = []
            for cluster in response['CacheClusters']:
                engine = cluster['Engine']
                
                # Filtrar por engine si se especifica
                if engine_filter != 'all' and engine != engine_filter:
                    continue
                
                # Obtener endpoint
                endpoint = 'N/A'
                if cluster.get('CacheNodes'):
                    if engine == 'redis':
                        node = cluster['CacheNodes'][0]
                        endpoint = f"{node.get('Endpoint', {}).get('Address', 'N/A')}:{node.get('Endpoint', {}).get('Port', 'N/A')}"
                    elif engine == 'memcached' and cluster.get('ConfigurationEndpoint'):
                        cfg_endpoint = cluster['ConfigurationEndpoint']
                        endpoint = f"{cfg_endpoint.get('Address', 'N/A')}:{cfg_endpoint.get('Port', 'N/A')}"
                
                clusters.append({
                    'cluster_id': cluster['CacheClusterId'],
                    'engine': engine,
                    'engine_version': cluster.get('EngineVersion', 'N/A'),
                    'node_type': cluster.get('CacheNodeType', 'N/A'),
                    'num_nodes': cluster.get('NumCacheNodes', 0),
                    'status': cluster.get('CacheClusterStatus', 'N/A'),
                    'endpoint': endpoint
                })
            
            return {
                'clusters': clusters,
                'count': len(clusters),
                'engine_filter': engine_filter
            }
        
        except Exception as e:
            logger.exception(f"Error listando clusters ElastiCache: {e}")
            return {
                'error': str(e),
                'clusters': []
            }
    
    def _execute_create_elasticache_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un cluster de ElastiCache"""
        try:
            elasticache = boto3.client('elasticache', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            cluster_id = str(params['cluster_id'])
            engine = params.get('engine', 'redis')
            node_type = params.get('node_type', 'cache.t3.micro')
            num_nodes = int(params.get('num_cache_nodes', 1))
            engine_version = params.get('engine_version', '7.0')
            
            # Redis siempre usa 1 nodo para cluster mode disabled
            if engine == 'redis':
                num_nodes = 1
            
            create_params = {
                'CacheClusterId': cluster_id,
                'Engine': engine,
                'CacheNodeType': node_type,
                'NumCacheNodes': num_nodes,
                'EngineVersion': engine_version
            }
            
            response = elasticache.create_cache_cluster(**create_params)
            cluster = response['CacheCluster']
            
            return {
                'cluster_id': cluster['CacheClusterId'],
                'engine': cluster['Engine'],
                'engine_version': cluster['EngineVersion'],
                'node_type': cluster['CacheNodeType'],
                'num_nodes': cluster['NumCacheNodes'],
                'status': cluster['CacheClusterStatus'],
                'message': f"Cluster ElastiCache '{cluster_id}' creado exitosamente. Estado: {cluster['CacheClusterStatus']}"
            }
        
        except Exception as e:
            logger.exception(f"Error creando cluster ElastiCache: {e}")
            return {
                'error': str(e),
                'cluster_id': str(params.get('cluster_id', 'unknown')),
                'message': f"Error al crear cluster ElastiCache: {str(e)}"
            }
    
    def _execute_delete_elasticache_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un cluster de ElastiCache"""
        try:
            elasticache = boto3.client('elasticache', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            cluster_id = str(params['cluster_id'])
            
            elasticache.delete_cache_cluster(CacheClusterId=cluster_id)
            
            return {
                'cluster_id': cluster_id,
                'message': f"Cluster ElastiCache '{cluster_id}' eliminado exitosamente"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando cluster ElastiCache: {e}")
            return {
                'error': str(e),
                'cluster_id': str(params.get('cluster_id', 'unknown')),
                'message': f"Error al eliminar cluster ElastiCache: {str(e)}"
            }
    
    def _execute_reboot_elasticache_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reinicia un cluster de ElastiCache"""
        try:
            elasticache = boto3.client('elasticache', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            cluster_id = str(params['cluster_id'])
            
            # Obtener IDs de nodos
            response = elasticache.describe_cache_clusters(
                CacheClusterId=cluster_id,
                ShowCacheNodeInfo=True
            )
            
            cluster = response['CacheClusters'][0]
            node_ids = [node['CacheNodeId'] for node in cluster.get('CacheNodes', [])]
            
            elasticache.reboot_cache_cluster(
                CacheClusterId=cluster_id,
                CacheNodeIdsToReboot=node_ids
            )
            
            return {
                'cluster_id': cluster_id,
                'nodes_rebooted': len(node_ids),
                'message': f"Cluster ElastiCache '{cluster_id}' reiniciado exitosamente ({len(node_ids)} nodos)"
            }
        
        except Exception as e:
            logger.exception(f"Error reiniciando cluster ElastiCache: {e}")
            return {
                'error': str(e),
                'cluster_id': str(params.get('cluster_id', 'unknown')),
                'message': f"Error al reiniciar cluster ElastiCache: {str(e)}"
            }
    
    # RDS Snapshot Operations
    def _execute_create_rds_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un snapshot de RDS"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_instance_id = str(params['db_instance_identifier'])
            snapshot_id = str(params['snapshot_identifier'])
            
            response = rds.create_db_snapshot(
                DBInstanceIdentifier=db_instance_id,
                DBSnapshotIdentifier=snapshot_id
            )
            
            snapshot = response['DBSnapshot']
            
            return {
                'snapshot_identifier': snapshot['DBSnapshotIdentifier'],
                'db_instance_identifier': snapshot['DBInstanceIdentifier'],
                'status': snapshot['Status'],
                'engine': snapshot['Engine'],
                'allocated_storage': snapshot.get('AllocatedStorage', 0),
                'message': f"Snapshot '{snapshot_id}' creado exitosamente. Estado: {snapshot['Status']}"
            }
        
        except Exception as e:
            logger.exception(f"Error creando snapshot RDS: {e}")
            return {
                'error': str(e),
                'snapshot_identifier': str(params.get('snapshot_identifier', 'unknown')),
                'message': f"Error al crear snapshot RDS: {str(e)}"
            }
    
    def _execute_delete_rds_snapshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un snapshot de RDS"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            snapshot_id = str(params['snapshot_identifier'])
            
            rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
            
            return {
                'snapshot_identifier': snapshot_id,
                'message': f"Snapshot '{snapshot_id}' eliminado exitosamente"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando snapshot RDS: {e}")
            return {
                'error': str(e),
                'snapshot_identifier': str(params.get('snapshot_identifier', 'unknown')),
                'message': f"Error al eliminar snapshot RDS: {str(e)}"
            }
    
    def _execute_delete_rds_instance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una instancia de RDS"""
        try:
            rds = boto3.client('rds', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            db_instance_id = str(params['db_instance_identifier'])
            skip_final_snapshot = params.get('skip_final_snapshot', False)
            
            delete_params = {
                'DBInstanceIdentifier': db_instance_id,
                'SkipFinalSnapshot': skip_final_snapshot
            }
            
            if not skip_final_snapshot:
                final_snapshot_id = params.get('final_snapshot_identifier')
                if not final_snapshot_id:
                    import datetime
                    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    final_snapshot_id = f"{db_instance_id}-final-{timestamp}"
                
                delete_params['FinalDBSnapshotIdentifier'] = final_snapshot_id
            
            response = rds.delete_db_instance(**delete_params)
            db_instance = response['DBInstance']
            
            return {
                'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                'status': db_instance['DBInstanceStatus'],
                'final_snapshot': delete_params.get('FinalDBSnapshotIdentifier', 'N/A (omitido)'),
                'message': f"Instancia RDS '{db_instance_id}' eliminada. Estado: {db_instance['DBInstanceStatus']}"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando instancia RDS: {e}")
            return {
                'error': str(e),
                'db_instance_identifier': str(params.get('db_instance_identifier', 'unknown')),
                'message': f"Error al eliminar instancia RDS: {str(e)}"
            }
    
    # DynamoDB Item Operations
    def _execute_put_dynamodb_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta o actualiza un item en DynamoDB"""
        try:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            table_name = str(params['table_name'])
            item = params['item']
            
            table = dynamodb.Table(table_name)
            table.put_item(Item=item)
            
            return {
                'table_name': table_name,
                'item_keys': {k: v for k, v in item.items() if k in ['id', 'pk', 'sk', 'hash_key', 'range_key']},
                'message': f"Item insertado/actualizado exitosamente en tabla '{table_name}'"
            }
        
        except Exception as e:
            logger.exception(f"Error insertando item en DynamoDB: {e}")
            return {
                'error': str(e),
                'table_name': str(params.get('table_name', 'unknown')),
                'message': f"Error al insertar item en DynamoDB: {str(e)}"
            }
    
    def _execute_delete_dynamodb_item(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un item de DynamoDB"""
        try:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            table_name = str(params['table_name'])
            key = params['key']
            
            table = dynamodb.Table(table_name)
            table.delete_item(Key=key)
            
            return {
                'table_name': table_name,
                'key': key,
                'message': f"Item eliminado exitosamente de tabla '{table_name}'"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando item de DynamoDB: {e}")
            return {
                'error': str(e),
                'table_name': str(params.get('table_name', 'unknown')),
                'message': f"Error al eliminar item de DynamoDB: {str(e)}"
            }
    
    def _execute_delete_dynamodb_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una tabla de DynamoDB"""
        try:
            dynamodb = boto3.client('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            table_name = str(params['table_name'])
            
            response = dynamodb.delete_table(TableName=table_name)
            table = response['TableDescription']
            
            return {
                'table_name': table['TableName'],
                'status': table['TableStatus'],
                'message': f"Tabla DynamoDB '{table_name}' eliminada. Estado: {table['TableStatus']}"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando tabla DynamoDB: {e}")
            return {
                'error': str(e),
                'table_name': str(params.get('table_name', 'unknown')),
                'message': f"Error al eliminar tabla DynamoDB: {str(e)}"
            }
    
    # Neptune Operations
    def _execute_list_neptune_clusters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista clusters de Neptune"""
        try:
            neptune = boto3.client('neptune', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = neptune.describe_db_clusters()
            
            clusters = []
            for cluster in response['DBClusters']:
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
            
            return {
                'clusters': clusters,
                'count': len(clusters)
            }
        
        except Exception as e:
            logger.exception(f"Error listando clusters Neptune: {e}")
            return {
                'error': str(e),
                'clusters': []
            }
    
    def _execute_create_neptune_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un cluster de Neptune"""
        try:
            neptune = boto3.client('neptune', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            cluster_id = str(params['cluster_identifier'])
            instance_class = params.get('instance_class', 'db.t3.medium')
            engine_version = params.get('engine_version', '1.2.1.0')
            master_password = str(params['master_password'])
            
            # Crear cluster
            neptune.create_db_cluster(
                DBClusterIdentifier=cluster_id,
                Engine='neptune',
                EngineVersion=engine_version,
                MasterUsername='admin',
                MasterUserPassword=master_password,
                StorageEncrypted=True
            )
            
            # Crear instancia primaria
            neptune.create_db_instance(
                DBInstanceIdentifier=f"{cluster_id}-instance-1",
                DBInstanceClass=instance_class,
                Engine='neptune',
                DBClusterIdentifier=cluster_id
            )
            
            return {
                'cluster_identifier': cluster_id,
                'instance_identifier': f"{cluster_id}-instance-1",
                'engine': 'neptune',
                'engine_version': engine_version,
                'instance_class': instance_class,
                'message': f"Cluster Neptune '{cluster_id}' creado exitosamente con instancia primaria"
            }
        
        except Exception as e:
            logger.exception(f"Error creando cluster Neptune: {e}")
            return {
                'error': str(e),
                'cluster_identifier': str(params.get('cluster_identifier', 'unknown')),
                'message': f"Error al crear cluster Neptune: {str(e)}"
            }
    
    def _execute_delete_neptune_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un cluster de Neptune"""
        try:
            neptune = boto3.client('neptune', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            cluster_id = str(params['cluster_identifier'])
            
            # Obtener instancias del cluster
            response = neptune.describe_db_clusters(DBClusterIdentifier=cluster_id)
            cluster = response['DBClusters'][0]
            
            # Eliminar instancias primero
            instances_deleted = []
            for member in cluster.get('DBClusterMembers', []):
                instance_id = member['DBInstanceIdentifier']
                try:
                    neptune.delete_db_instance(
                        DBInstanceIdentifier=instance_id,
                        SkipFinalSnapshot=True
                    )
                    instances_deleted.append(instance_id)
                except Exception as e:
                    logger.warning(f"Error eliminando instancia Neptune {instance_id}: {e}")
            
            # Eliminar cluster
            neptune.delete_db_cluster(
                DBClusterIdentifier=cluster_id,
                SkipFinalSnapshot=True
            )
            
            return {
                'cluster_identifier': cluster_id,
                'instances_deleted': instances_deleted,
                'message': f"Cluster Neptune '{cluster_id}' y {len(instances_deleted)} instancia(s) eliminados"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando cluster Neptune: {e}")
            return {
                'error': str(e),
                'cluster_identifier': str(params.get('cluster_identifier', 'unknown')),
                'message': f"Error al eliminar cluster Neptune: {str(e)}"
            }
    
    # DocumentDB Operations
    def _execute_list_documentdb_clusters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista clusters de DocumentDB"""
        try:
            docdb = boto3.client('docdb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = docdb.describe_db_clusters()
            
            clusters = []
            for cluster in response['DBClusters']:
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
            
            return {
                'clusters': clusters,
                'count': len(clusters)
            }
        
        except Exception as e:
            logger.exception(f"Error listando clusters DocumentDB: {e}")
            return {
                'error': str(e),
                'clusters': []
            }
    
    def _execute_create_documentdb_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un cluster de DocumentDB"""
        try:
            docdb = boto3.client('docdb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            
            cluster_id = str(params['cluster_identifier'])
            instance_class = params.get('instance_class', 'db.t3.medium')
            engine_version = params.get('engine_version', '5.0.0')
            master_password = str(params['master_password'])
            
            # Crear cluster
            docdb.create_db_cluster(
                DBClusterIdentifier=cluster_id,
                Engine='docdb',
                EngineVersion=engine_version,
                MasterUsername='docdbadmin',
                MasterUserPassword=master_password,
                StorageEncrypted=True,
                Port=27017
            )
            
            # Crear instancia primaria
            docdb.create_db_instance(
                DBInstanceIdentifier=f"{cluster_id}-instance-1",
                DBInstanceClass=instance_class,
                Engine='docdb',
                DBClusterIdentifier=cluster_id
            )
            
            return {
                'cluster_identifier': cluster_id,
                'instance_identifier': f"{cluster_id}-instance-1",
                'engine': 'docdb',
                'engine_version': engine_version,
                'instance_class': instance_class,
                'port': 27017,
                'message': f"Cluster DocumentDB '{cluster_id}' creado exitosamente con instancia primaria"
            }
        
        except Exception as e:
            logger.exception(f"Error creando cluster DocumentDB: {e}")
            return {
                'error': str(e),
                'cluster_identifier': str(params.get('cluster_identifier', 'unknown')),
                'message': f"Error al crear cluster DocumentDB: {str(e)}"
            }
    
    def _execute_delete_documentdb_cluster(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un cluster de DocumentDB"""
        try:
            docdb = boto3.client('docdb', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            cluster_id = str(params['cluster_identifier'])
            
            # Obtener instancias del cluster
            response = docdb.describe_db_clusters(DBClusterIdentifier=cluster_id)
            cluster = response['DBClusters'][0]
            
            # Eliminar instancias primero
            instances_deleted = []
            for member in cluster.get('DBClusterMembers', []):
                instance_id = member['DBInstanceIdentifier']
                try:
                    docdb.delete_db_instance(
                        DBInstanceIdentifier=instance_id,
                        SkipFinalSnapshot=True
                    )
                    instances_deleted.append(instance_id)
                except Exception as e:
                    logger.warning(f"Error eliminando instancia DocumentDB {instance_id}: {e}")
            
            # Eliminar cluster
            docdb.delete_db_cluster(
                DBClusterIdentifier=cluster_id,
                SkipFinalSnapshot=True
            )
            
            return {
                'cluster_identifier': cluster_id,
                'instances_deleted': instances_deleted,
                'message': f"Cluster DocumentDB '{cluster_id}' y {len(instances_deleted)} instancia(s) eliminados"
            }
        
        except Exception as e:
            logger.exception(f"Error eliminando cluster DocumentDB: {e}")
            return {
                'error': str(e),
                'cluster_identifier': str(params.get('cluster_identifier', 'unknown')),
                'message': f"Error al eliminar cluster DocumentDB: {str(e)}"
            }

    # ===== HERRAMIENTAS IAM =====

    def _execute_create_iam_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo usuario IAM"""
        try:
            iam = boto3.client('iam')
            user_name = params['user_name']

            response = iam.create_user(UserName=user_name)

            return {
                'success': True,
                'user_name': user_name,
                'user_id': response['User']['UserId'],
                'arn': response['User']['Arn'],
                'create_date': response['User']['CreateDate'].isoformat(),
                'message': f"Usuario IAM '{user_name}' creado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error creando usuario IAM {params.get('user_name', 'unknown')}: {e}")
            return {
                'success': False,
                'user_name': str(params.get('user_name', 'unknown')),
                'message': f"Error al crear usuario IAM: {str(e)}"
            }

    def _execute_delete_iam_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un usuario IAM y todas sus claves de acceso"""
        try:
            iam = boto3.client('iam')
            user_name = params['user_name']

            # Primero eliminar todas las claves de acceso
            access_keys = iam.list_access_keys(UserName=user_name)
            for key in access_keys.get('AccessKeyMetadata', []):
                try:
                    iam.delete_access_key(UserName=user_name, AccessKeyId=key['AccessKeyId'])
                except Exception as e:
                    logger.warning(f"Error eliminando clave de acceso {key['AccessKeyId']}: {e}")

            # Eliminar el usuario
            iam.delete_user(UserName=user_name)

            return {
                'success': True,
                'user_name': user_name,
                'message': f"Usuario IAM '{user_name}' y todas sus claves de acceso eliminados exitosamente"
            }
        except Exception as e:
            logger.error(f"Error eliminando usuario IAM {params.get('user_name', 'unknown')}: {e}")
            return {
                'success': False,
                'user_name': str(params.get('user_name', 'unknown')),
                'message': f"Error al eliminar usuario IAM: {str(e)}"
            }

    def _execute_list_iam_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los usuarios IAM"""
        try:
            iam = boto3.client('iam')
            response = iam.list_users(MaxItems=100)

            users = []
            for user in response.get('Users', []):
                users.append({
                    'user_name': user['UserName'],
                    'user_id': user['UserId'],
                    'arn': user['Arn'],
                    'create_date': user['CreateDate'].isoformat(),
                    'path': user.get('Path', '/')
                })

            return {
                'success': True,
                'users': users,
                'count': len(users),
                'message': f"Se encontraron {len(users)} usuarios IAM"
            }
        except Exception as e:
            logger.error(f"Error listando usuarios IAM: {e}")
            return {
                'success': False,
                'users': [],
                'count': 0,
                'message': f"Error al listar usuarios IAM: {str(e)}"
            }

    def _execute_create_iam_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo rol IAM con política de confianza"""
        try:
            iam = boto3.client('iam')
            role_name = params['role_name']
            assume_role_policy = params['assume_role_policy_document']
            description = params.get('description', '')

            kwargs = {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': assume_role_policy
            }
            if description:
                kwargs['Description'] = description

            response = iam.create_role(**kwargs)

            return {
                'success': True,
                'role_name': role_name,
                'role_id': response['Role']['RoleId'],
                'arn': response['Role']['Arn'],
                'create_date': response['Role']['CreateDate'].isoformat(),
                'message': f"Rol IAM '{role_name}' creado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error creando rol IAM {params.get('role_name', 'unknown')}: {e}")
            return {
                'success': False,
                'role_name': str(params.get('role_name', 'unknown')),
                'message': f"Error al crear rol IAM: {str(e)}"
            }

    def _execute_delete_iam_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un rol IAM y desadjunta todas las políticas"""
        try:
            iam = boto3.client('iam')
            role_name = params['role_name']

            # Desadjuntar todas las políticas administradas
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies.get('AttachedPolicies', []):
                try:
                    iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                except Exception as e:
                    logger.warning(f"Error desadjuntando política {policy['PolicyArn']}: {e}")

            # Desadjuntar todas las políticas inline
            inline_policies = iam.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies.get('PolicyNames', []):
                try:
                    iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                except Exception as e:
                    logger.warning(f"Error eliminando política inline {policy_name}: {e}")

            # Eliminar el rol
            iam.delete_role(RoleName=role_name)

            return {
                'success': True,
                'role_name': role_name,
                'message': f"Rol IAM '{role_name}' y todas sus políticas eliminados exitosamente"
            }
        except Exception as e:
            logger.error(f"Error eliminando rol IAM {params.get('role_name', 'unknown')}: {e}")
            return {
                'success': False,
                'role_name': str(params.get('role_name', 'unknown')),
                'message': f"Error al eliminar rol IAM: {str(e)}"
            }

    def _execute_list_iam_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los roles IAM"""
        try:
            iam = boto3.client('iam')
            response = iam.list_roles(MaxItems=100)

            roles = []
            for role in response.get('Roles', []):
                roles.append({
                    'role_name': role['RoleName'],
                    'role_id': role['RoleId'],
                    'arn': role['Arn'],
                    'create_date': role['CreateDate'].isoformat(),
                    'path': role.get('Path', '/'),
                    'description': role.get('Description', '')
                })

            return {
                'success': True,
                'roles': roles,
                'count': len(roles),
                'message': f"Se encontraron {len(roles)} roles IAM"
            }
        except Exception as e:
            logger.error(f"Error listando roles IAM: {e}")
            return {
                'success': False,
                'roles': [],
                'count': 0,
                'message': f"Error al listar roles IAM: {str(e)}"
            }

    def _execute_create_iam_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva política IAM administrada por el cliente"""
        try:
            iam = boto3.client('iam')
            policy_name = params['policy_name']
            policy_document = params['policy_document']
            description = params.get('description', '')

            kwargs = {
                'PolicyName': policy_name,
                'PolicyDocument': policy_document
            }
            if description:
                kwargs['Description'] = description

            response = iam.create_policy(**kwargs)

            return {
                'success': True,
                'policy_name': policy_name,
                'policy_arn': response['Policy']['Arn'],
                'policy_id': response['Policy']['PolicyId'],
                'create_date': response['Policy']['CreateDate'].isoformat(),
                'message': f"Política IAM '{policy_name}' creada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error creando política IAM {params.get('policy_name', 'unknown')}: {e}")
            return {
                'success': False,
                'policy_name': str(params.get('policy_name', 'unknown')),
                'message': f"Error al crear política IAM: {str(e)}"
            }

    def _execute_delete_iam_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una política IAM administrada por el cliente"""
        try:
            iam = boto3.client('iam')
            policy_arn = params['policy_arn']

            iam.delete_policy(PolicyArn=policy_arn)

            return {
                'success': True,
                'policy_arn': policy_arn,
                'message': f"Política IAM eliminada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error eliminando política IAM {params.get('policy_arn', 'unknown')}: {e}")
            return {
                'success': False,
                'policy_arn': str(params.get('policy_arn', 'unknown')),
                'message': f"Error al eliminar política IAM: {str(e)}"
            }

    def _execute_list_iam_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todas las políticas IAM administradas por el cliente"""
        try:
            iam = boto3.client('iam')
            response = iam.list_policies(Scope='Local', MaxItems=100)

            policies = []
            for policy in response.get('Policies', []):
                policies.append({
                    'policy_name': policy['PolicyName'],
                    'policy_id': policy['PolicyId'],
                    'arn': policy['Arn'],
                    'create_date': policy['CreateDate'].isoformat(),
                    'description': policy.get('Description', ''),
                    'attachment_count': policy.get('AttachmentCount', 0)
                })

            return {
                'success': True,
                'policies': policies,
                'count': len(policies),
                'message': f"Se encontraron {len(policies)} políticas IAM administradas por el cliente"
            }
        except Exception as e:
            logger.error(f"Error listando políticas IAM: {e}")
            return {
                'success': False,
                'policies': [],
                'count': 0,
                'message': f"Error al listar políticas IAM: {str(e)}"
            }

    def _execute_create_access_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva clave de acceso para un usuario IAM"""
        try:
            iam = boto3.client('iam')
            user_name = params['user_name']

            response = iam.create_access_key(UserName=user_name)

            # IMPORTANTE: Solo devolver el AccessKeyId, NO el SecretAccessKey por seguridad
            return {
                'success': True,
                'user_name': user_name,
                'access_key_id': response['AccessKey']['AccessKeyId'],
                'create_date': response['AccessKey']['CreateDate'].isoformat(),
                'status': response['AccessKey']['Status'],
                'warning': '⚠️ La clave secreta solo se muestra UNA vez. Guárdala de forma segura.',
                'message': f"Clave de acceso creada para usuario '{user_name}'. ¡Guarda la clave secreta ahora!"
            }
        except Exception as e:
            logger.error(f"Error creando clave de acceso para {params.get('user_name', 'unknown')}: {e}")
            return {
                'success': False,
                'user_name': str(params.get('user_name', 'unknown')),
                'message': f"Error al crear clave de acceso: {str(e)}"
            }

    def _execute_delete_access_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una clave de acceso de un usuario IAM"""
        try:
            iam = boto3.client('iam')
            user_name = params['user_name']
            access_key_id = params['access_key_id']

            iam.delete_access_key(UserName=user_name, AccessKeyId=access_key_id)

            return {
                'success': True,
                'user_name': user_name,
                'access_key_id': access_key_id,
                'message': f"Clave de acceso '{access_key_id}' eliminada exitosamente del usuario '{user_name}'"
            }
        except Exception as e:
            logger.error(f"Error eliminando clave de acceso {params.get('access_key_id', 'unknown')} del usuario {params.get('user_name', 'unknown')}: {e}")
            return {
                'success': False,
                'user_name': str(params.get('user_name', 'unknown')),
                'access_key_id': str(params.get('access_key_id', 'unknown')),
                'message': f"Error al eliminar clave de acceso: {str(e)}"
            }

    def _execute_list_access_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todas las claves de acceso de un usuario IAM"""
        try:
            iam = boto3.client('iam')
            user_name = params['user_name']

            response = iam.list_access_keys(UserName=user_name)

            access_keys = []
            for key in response.get('AccessKeyMetadata', []):
                access_keys.append({
                    'access_key_id': key['AccessKeyId'],
                    'create_date': key['CreateDate'].isoformat(),
                    'status': key['Status']
                })

            return {
                'success': True,
                'user_name': user_name,
                'access_keys': access_keys,
                'count': len(access_keys),
                'message': f"Se encontraron {len(access_keys)} claves de acceso para el usuario '{user_name}'"
            }
        except Exception as e:
            logger.error(f"Error listando claves de acceso del usuario {params.get('user_name', 'unknown')}: {e}")
            return {
                'success': False,
                'user_name': str(params.get('user_name', 'unknown')),
                'access_keys': [],
                'count': 0,
                'message': f"Error al listar claves de acceso: {str(e)}"
            }

    # Métodos KMS (Key Management Service)
    def _execute_create_kms_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva clave KMS"""
        try:
            kms = boto3.client('kms')

            # Parámetros de creación
            create_params = {
                'KeyUsage': params.get('key_usage', 'ENCRYPT_DECRYPT'),
                'KeySpec': params.get('key_spec', 'SYMMETRIC_DEFAULT'),
                'MultiRegion': params.get('multi_region', False)
            }

            # Agregar descripción si se proporciona
            if 'description' in params and params['description']:
                create_params['Description'] = params['description']

            response = kms.create_key(**create_params)
            key_id = response['KeyMetadata']['KeyId']

            # Crear alias si se proporciona
            if 'alias' in params and params['alias']:
                alias_name = f"alias/{params['alias']}"
                kms.create_alias(AliasName=alias_name, TargetKeyId=key_id)

            return {
                'success': True,
                'key_id': key_id,
                'key_arn': response['KeyMetadata']['Arn'],
                'description': params.get('description', ''),
                'alias': params.get('alias', ''),
                'key_usage': create_params['KeyUsage'],
                'key_spec': create_params['KeySpec'],
                'multi_region': create_params['MultiRegion'],
                'message': f"Clave KMS creada exitosamente con ID: {key_id}"
            }
        except Exception as e:
            logger.error(f"Error creando clave KMS: {e}")
            return {
                'success': False,
                'message': f"Error al crear clave KMS: {str(e)}"
            }

    def _execute_list_kms_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todas las claves KMS disponibles"""
        try:
            kms = boto3.client('kms')

            response = kms.list_keys(Limit=100)
            keys = []

            for key in response.get('Keys', []):
                try:
                    # Obtener detalles de la clave
                    key_details = kms.describe_key(KeyId=key['KeyId'])['KeyMetadata']

                    # Obtener aliases
                    aliases_response = kms.list_aliases(KeyId=key['KeyId'])
                    aliases = [alias['AliasName'] for alias in aliases_response.get('Aliases', [])
                             if not alias['AliasName'].startswith('alias/aws/')]

                    keys.append({
                        'key_id': key_details['KeyId'],
                        'key_arn': key_details['Arn'],
                        'description': key_details.get('Description', ''),
                        'key_usage': key_details['KeyUsage'],
                        'key_spec': key_details.get('KeySpec', 'SYMMETRIC_DEFAULT'),
                        'key_state': key_details['KeyState'],
                        'enabled': key_details['Enabled'],
                        'multi_region': key_details.get('MultiRegion', False),
                        'aliases': aliases,
                        'creation_date': key_details['CreationDate'].isoformat() if key_details.get('CreationDate') else None
                    })
                except Exception as key_error:
                    # Si hay error obteniendo detalles de una clave específica, incluir info básica
                    keys.append({
                        'key_id': key['KeyId'],
                        'error': str(key_error)
                    })

            return {
                'success': True,
                'keys': keys,
                'count': len(keys),
                'message': f"Se encontraron {len(keys)} claves KMS"
            }
        except Exception as e:
            logger.error(f"Error listando claves KMS: {e}")
            return {
                'success': False,
                'keys': [],
                'count': 0,
                'message': f"Error al listar claves KMS: {str(e)}"
            }

    def _execute_encrypt_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Encripta datos usando una clave KMS"""
        try:
            kms = boto3.client('kms')

            plaintext = params['plaintext']
            encoding = params.get('encoding', 'base64')

            # Convertir plaintext según el encoding
            if encoding == 'base64':
                import base64
                plaintext_bytes = base64.b64decode(plaintext)
            elif encoding == 'hex':
                plaintext_bytes = bytes.fromhex(plaintext)
            else:  # raw
                plaintext_bytes = plaintext.encode('utf-8')

            # Encriptar
            response = kms.encrypt(
                KeyId=params['key_id'],
                Plaintext=plaintext_bytes
            )

            ciphertext_blob = response['CiphertextBlob']

            # Convertir respuesta según encoding solicitado
            if encoding == 'base64':
                import base64
                ciphertext_encoded = base64.b64encode(ciphertext_blob).decode('utf-8')
            elif encoding == 'hex':
                ciphertext_encoded = ciphertext_blob.hex()
            else:  # raw
                ciphertext_encoded = ciphertext_blob.decode('latin-1')  # Para bytes raw

            return {
                'success': True,
                'key_id': response['KeyId'],
                'ciphertext_blob': ciphertext_encoded,
                'encoding': encoding,
                'message': f"Datos encriptados exitosamente usando la clave {params['key_id']}"
            }
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            return {
                'success': False,
                'message': f"Error al encriptar datos: {str(e)}"
            }

    def _execute_decrypt_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Desencripta datos usando una clave KMS"""
        try:
            kms = boto3.client('kms')

            ciphertext_blob = params['ciphertext_blob']
            encoding = params.get('encoding', 'base64')

            # Convertir ciphertext según el encoding
            if encoding == 'base64':
                import base64
                ciphertext_bytes = base64.b64decode(ciphertext_blob)
            elif encoding == 'hex':
                ciphertext_bytes = bytes.fromhex(ciphertext_blob)
            else:  # raw
                ciphertext_bytes = ciphertext_blob.encode('latin-1')

            # Desencriptar
            response = kms.decrypt(CiphertextBlob=ciphertext_bytes)

            plaintext_bytes = response['Plaintext']
            plaintext = plaintext_bytes.decode('utf-8')

            return {
                'success': True,
                'key_id': response['KeyId'],
                'plaintext': plaintext,
                'message': f"Datos desencriptados exitosamente usando la clave {response['KeyId']}"
            }
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            return {
                'success': False,
                'message': f"Error al desencriptar datos: {str(e)}"
            }

    def _execute_generate_data_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera una clave de datos encriptada con KMS"""
        try:
            kms = boto3.client('kms')

            generate_params = {
                'KeyId': params['key_id'],
                'KeySpec': f'AES_{params.get("key_length", 256)}'
            }

            # Incluir plaintext si se solicita
            if params.get('include_plaintext', True):
                response = kms.generate_data_key(**generate_params)
                plaintext_key = response['Plaintext']
            else:
                response = kms.generate_data_key_without_plaintext(**generate_params)
                plaintext_key = None

            ciphertext_blob = response['CiphertextBlob']

            # Codificar en base64 para respuesta
            import base64
            ciphertext_encoded = base64.b64encode(ciphertext_blob).decode('utf-8')
            plaintext_encoded = base64.b64encode(plaintext_key).decode('utf-8') if plaintext_key else None

            return {
                'success': True,
                'key_id': response['KeyId'],
                'ciphertext_blob': ciphertext_encoded,
                'plaintext': plaintext_encoded,
                'key_length': params.get('key_length', 256),
                'encoding': 'base64',
                'message': f"Clave de datos generada exitosamente usando la clave {params['key_id']}"
            }
        except Exception as e:
            logger.error(f"Error generando clave de datos: {e}")
            return {
                'success': False,
                'message': f"Error al generar clave de datos: {str(e)}"
            }

    def _execute_enable_kms_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Habilita una clave KMS deshabilitada"""
        try:
            kms = boto3.client('kms')
            key_id = params['key_id']

            kms.enable_key(KeyId=key_id)

            return {
                'success': True,
                'key_id': key_id,
                'message': f"Clave KMS {key_id} habilitada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error habilitando clave KMS {params.get('key_id', 'unknown')}: {e}")
            return {
                'success': False,
                'key_id': str(params.get('key_id', 'unknown')),
                'message': f"Error al habilitar clave KMS: {str(e)}"
            }

    def _execute_disable_kms_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deshabilita una clave KMS habilitada"""
        try:
            kms = boto3.client('kms')
            key_id = params['key_id']

            kms.disable_key(KeyId=key_id)

            return {
                'success': True,
                'key_id': key_id,
                'message': f"Clave KMS {key_id} deshabilitada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error deshabilitando clave KMS {params.get('key_id', 'unknown')}: {e}")
            return {
                'success': False,
                'key_id': str(params.get('key_id', 'unknown')),
                'message': f"Error al deshabilitar clave KMS: {str(e)}"
            }

    def _execute_rotate_kms_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rota la clave material de una clave KMS"""
        try:
            kms = boto3.client('kms')
            key_id = params['key_id']

            kms.rotate_key_on_demand(KeyId=key_id)

            return {
                'success': True,
                'key_id': key_id,
                'message': f"Clave KMS {key_id} rotada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error rotando clave KMS {params.get('key_id', 'unknown')}: {e}")
            return {
                'success': False,
                'key_id': str(params.get('key_id', 'unknown')),
                'message': f"Error al rotar clave KMS: {str(e)}"
            }

    def _execute_schedule_key_deletion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Programa la eliminación de una clave KMS"""
        try:
            kms = boto3.client('kms')
            key_id = params['key_id']
            pending_days = params.get('pending_days', 7)

            response = kms.schedule_key_deletion(
                KeyId=key_id,
                PendingWindowInDays=pending_days
            )

            return {
                'success': True,
                'key_id': key_id,
                'deletion_date': response['DeletionDate'].isoformat(),
                'pending_days': pending_days,
                'message': f"Eliminación de clave KMS {key_id} programada para {response['DeletionDate'].isoformat()}"
            }
        except Exception as e:
            logger.error(f"Error programando eliminación de clave KMS {params.get('key_id', 'unknown')}: {e}")
            return {
                'success': False,
                'key_id': str(params.get('key_id', 'unknown')),
                'message': f"Error al programar eliminación de clave KMS: {str(e)}"
            }

    def _execute_cancel_key_deletion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancela la eliminación programada de una clave KMS"""
        try:
            kms = boto3.client('kms')
            key_id = params['key_id']

            response = kms.cancel_key_deletion(KeyId=key_id)

            return {
                'success': True,
                'key_id': key_id,
                'key_state': response['KeyState'],
                'message': f"Eliminación de clave KMS {key_id} cancelada exitosamente"
            }
        except Exception as e:
            logger.error(f"Error cancelando eliminación de clave KMS {params.get('key_id', 'unknown')}: {e}")
            return {
                'success': False,
                'key_id': str(params.get('key_id', 'unknown')),
                'message': f"Error al cancelar eliminación de clave KMS: {str(e)}"
            }

    def _execute_create_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo par de claves (key pair) para EC2"""
        try:
            ec2 = boto3.client('ec2')
            key_name = params['key_name']

            response = ec2.create_key_pair(KeyName=key_name)

            return {
                'success': True,
                'key_name': key_name,
                'key_fingerprint': response['KeyFingerprint'],
                'key_material': response['KeyMaterial'][:50] + '...',  # Solo mostrar parte del material
                'message': f"Key pair '{key_name}' creado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error creando key pair {params.get('key_name', 'unknown')}: {e}")
            return {
                'success': False,
                'key_name': str(params.get('key_name', 'unknown')),
                'message': f"Error al crear key pair: {str(e)}"
            }

    def _execute_list_key_pairs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los pares de claves disponibles"""
        try:
            ec2 = boto3.client('ec2')
            response = ec2.describe_key_pairs()

            key_pairs = []
            for kp in response.get('KeyPairs', []):
                key_pairs.append({
                    'key_name': kp['KeyName'],
                    'key_fingerprint': kp['KeyFingerprint'],
                    'key_type': kp.get('KeyType', 'rsa'),
                    'key_pair_id': kp.get('KeyPairId', 'N/A')
                })

            return {
                'success': True,
                'key_pairs': key_pairs,
                'total_count': len(key_pairs),
                'message': f"Se encontraron {len(key_pairs)} key pairs"
            }
        except Exception as e:
            logger.error(f"Error listando key pairs: {e}")
            return {
                'success': False,
                'key_pairs': [],
                'message': f"Error al listar key pairs: {str(e)}"
            }

    def _execute_delete_key_pair(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un par de claves existente"""
        try:
            ec2 = boto3.client('ec2')
            key_name = params['key_name']

            ec2.delete_key_pair(KeyName=key_name)

            return {
                'success': True,
                'key_name': key_name,
                'message': f"Key pair '{key_name}' eliminado exitosamente"
            }
        except Exception as e:
            logger.error(f"Error eliminando key pair {params.get('key_name', 'unknown')}: {e}")
            return {
                'success': False,
                'key_name': str(params.get('key_name', 'unknown')),
                'message': f"Error al eliminar key pair: {str(e)}"
            }

    def _execute_describe_instance_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los tipos de instancia EC2 disponibles con sus especificaciones"""
        try:
            ec2 = boto3.client('ec2')
            response = ec2.describe_instance_types()

            instance_types = []
            for it in response.get('InstanceTypes', []):
                instance_types.append({
                    'instance_type': it['InstanceType'],
                    'vcpu_info': it.get('VCpuInfo', {}),
                    'memory_info': it.get('MemoryInfo', {}),
                    'instance_storage_supported': it.get('InstanceStorageSupported', False),
                    'ebs_info': it.get('EbsInfo', {}),
                    'network_info': it.get('NetworkInfo', {}),
                    'processor_info': it.get('ProcessorInfo', {})
                })

            # Ordenar por tipo de instancia
            instance_types.sort(key=lambda x: x['instance_type'])

            return {
                'success': True,
                'instance_types': instance_types,
                'total_count': len(instance_types),
                'message': f"Se encontraron {len(instance_types)} tipos de instancia"
            }
        except Exception as e:
            logger.error(f"Error describiendo tipos de instancia: {e}")
            return {
                'success': False,
                'instance_types': [],
                'message': f"Error al describir tipos de instancia: {str(e)}"
            }

    def _execute_modify_instance_attribute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modifica atributos de una instancia EC2"""
        try:
            ec2 = boto3.client('ec2')
            instance_id = params['instance_id']
            attribute = params['attribute']
            value = params['value']

            # Obtener el estado actual de la instancia
            instance_response = ec2.describe_instances(InstanceIds=[instance_id])
            instance = instance_response['Reservations'][0]['Instances'][0]
            current_state = instance['State']['Name']

            # Para cambiar el tipo de instancia, la instancia debe estar detenida
            if attribute == 'instanceType' and current_state == 'running':
                # Detener la instancia
                ec2.stop_instances(InstanceIds=[instance_id])
                ec2.get_waiter('instance_stopped').wait(InstanceIds=[instance_id])

            # Modificar el atributo
            if attribute == 'instanceType':
                ec2.modify_instance_attribute(
                    InstanceId=instance_id,
                    InstanceType={'Value': value}
                )
                message = f"Tipo de instancia cambiado a {value}"
            elif attribute == 'securityGroups':
                # value debe ser una lista de IDs de security groups separados por coma
                sg_ids = [sg.strip() for sg in value.split(',')]
                ec2.modify_instance_attribute(
                    InstanceId=instance_id,
                    Groups=sg_ids
                )
                message = f"Grupos de seguridad actualizados"
            else:
                return {
                    'success': False,
                    'instance_id': instance_id,
                    'message': f"Atributo '{attribute}' no soportado"
                }

            # Reiniciar la instancia si estaba corriendo y cambiamos el tipo
            if attribute == 'instanceType' and current_state == 'running':
                ec2.start_instances(InstanceIds=[instance_id])
                message += " (instancia reiniciada)"

            return {
                'success': True,
                'instance_id': instance_id,
                'attribute': attribute,
                'new_value': value,
                'message': message
            }
        except Exception as e:
            logger.error(f"Error modificando atributo de instancia {params.get('instance_id', 'unknown')}: {e}")
            return {
                'success': False,
                'instance_id': str(params.get('instance_id', 'unknown')),
                'message': f"Error al modificar atributo de instancia: {str(e)}"
            }

    def _execute_update_autoscaling_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un grupo de Auto Scaling"""
        try:
            asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            update_params = {'AutoScalingGroupName': params['group_name']}

            if 'min_size' in params:
                update_params['MinSize'] = params['min_size']
            if 'max_size' in params:
                update_params['MaxSize'] = params['max_size']
            if 'desired_capacity' in params:
                update_params['DesiredCapacity'] = params['desired_capacity']

            asg.update_auto_scaling_group(**update_params)

            return {
                'success': True,
                'group_name': params['group_name'],
                'message': f"Grupo de Auto Scaling '{params['group_name']}' actualizado exitosamente",
                'changes': {k: v for k, v in params.items() if k != 'group_name'}
            }

        except Exception as e:
            logger.exception(f"Error actualizando grupo de Auto Scaling: {e}")
            return {
                'success': False,
                'group_name': str(params.get('group_name', 'unknown')),
                'message': f"Error al actualizar grupo de Auto Scaling: {str(e)}"
            }

    def _execute_delete_autoscaling_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un grupo de Auto Scaling"""
        try:
            asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            force_delete = params.get('force_delete', True)

            asg.delete_auto_scaling_group(
                AutoScalingGroupName=params['group_name'],
                ForceDelete=force_delete
            )

            return {
                'success': True,
                'group_name': params['group_name'],
                'force_delete': force_delete,
                'message': f"Grupo de Auto Scaling '{params['group_name']}' eliminado exitosamente"
            }

        except Exception as e:
            logger.exception(f"Error eliminando grupo de Auto Scaling: {e}")
            return {
                'success': False,
                'group_name': str(params.get('group_name', 'unknown')),
                'message': f"Error al eliminar grupo de Auto Scaling: {str(e)}"
            }

    def _execute_create_scaling_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una política de escalado"""
        try:
            asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            policy_params = {
                'AutoScalingGroupName': params['group_name'],
                'PolicyName': params['policy_name'],
                'PolicyType': params['policy_type'],
                'AdjustmentType': params['adjustment_type'],
                'ScalingAdjustment': params['scaling_adjustment']
            }

            if 'cooldown' in params:
                policy_params['Cooldown'] = params['cooldown']

            response = asg.put_scaling_policy(**policy_params)

            return {
                'success': True,
                'group_name': params['group_name'],
                'policy_name': params['policy_name'],
                'policy_arn': response.get('PolicyARN'),
                'message': f"Política de escalado '{params['policy_name']}' creada exitosamente"
            }

        except Exception as e:
            logger.exception(f"Error creando política de escalado: {e}")
            return {
                'success': False,
                'group_name': str(params.get('group_name', 'unknown')),
                'policy_name': str(params.get('policy_name', 'unknown')),
                'message': f"Error al crear política de escalado: {str(e)}"
            }

    def _execute_delete_scaling_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una política de escalado"""
        try:
            asg = boto3.client('autoscaling', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            asg.delete_policy(
                AutoScalingGroupName=params['group_name'],
                PolicyName=params['policy_name']
            )

            return {
                'success': True,
                'group_name': params['group_name'],
                'policy_name': params['policy_name'],
                'message': f"Política de escalado '{params['policy_name']}' eliminada exitosamente"
            }

        except Exception as e:
            logger.exception(f"Error eliminando política de escalado: {e}")
            return {
                'success': False,
                'group_name': str(params.get('group_name', 'unknown')),
                'policy_name': str(params.get('policy_name', 'unknown')),
                'message': f"Error al eliminar política de escalado: {str(e)}"
            }

    def _execute_list_efs_file_systems(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los file systems EFS"""
        try:
            efs = boto3.client('efs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = efs.describe_file_systems()

            file_systems = []
            for fs in response['FileSystems']:
                file_systems.append({
                    'file_system_id': fs['FileSystemId'],
                    'creation_token': fs.get('CreationToken', ''),
                    'life_cycle_state': fs['LifeCycleState'],
                    'performance_mode': fs['PerformanceMode'],
                    'throughput_mode': fs['ThroughputMode'],
                    'provisioned_throughput': fs.get('ProvisionedThroughputInMibps'),
                    'size_in_bytes': fs.get('SizeInBytes', {}),
                    'creation_time': fs['CreationTime'].isoformat() if fs.get('CreationTime') else None,
                    'encrypted': fs.get('Encrypted', False)
                })

            return {
                'success': True,
                'file_systems': file_systems,
                'count': len(file_systems)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error al listar file systems EFS: {str(e)}"
            }

    def _execute_create_efs_file_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo file system EFS"""
        try:
            efs = boto3.client('efs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            creation_params = {
                'CreationToken': params['creation_token'],
                'PerformanceMode': params.get('performance_mode', 'generalPurpose'),
                'ThroughputMode': params.get('throughput_mode', 'bursting')
            }

            if params.get('throughput_mode') == 'provisioned' and params.get('provisioned_throughput'):
                creation_params['ProvisionedThroughputInMibps'] = float(params['provisioned_throughput'])

            response = efs.create_file_system(**creation_params)

            return {
                'success': True,
                'file_system_id': response['FileSystemId'],
                'creation_token': response.get('CreationToken', ''),
                'life_cycle_state': response['LifeCycleState'],
                'performance_mode': response['PerformanceMode'],
                'throughput_mode': response['ThroughputMode'],
                'creation_time': response['CreationTime'].isoformat() if response.get('CreationTime') else None
            }
        except Exception as e:
            return {
                'success': False,
                'creation_token': params.get('creation_token', 'unknown'),
                'message': f"Error al crear file system EFS: {str(e)}"
            }

    def _execute_delete_efs_file_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un file system EFS"""
        try:
            efs = boto3.client('efs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            efs.delete_file_system(FileSystemId=params['file_system_id'])

            return {
                'success': True,
                'file_system_id': params['file_system_id'],
                'message': 'File system EFS eliminado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'file_system_id': params.get('file_system_id', 'unknown'),
                'message': f"Error al eliminar file system EFS: {str(e)}"
            }

    def _execute_create_efs_mount_target(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un mount target para un file system EFS"""
        try:
            efs = boto3.client('efs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            mount_params = {
                'FileSystemId': params['file_system_id'],
                'SubnetId': params['subnet_id']
            }

            if params.get('ip_address'):
                mount_params['IpAddress'] = params['ip_address']

            if params.get('security_groups'):
                mount_params['SecurityGroups'] = params['security_groups']

            response = efs.create_mount_target(**mount_params)

            return {
                'success': True,
                'mount_target_id': response['MountTargetId'],
                'file_system_id': response['FileSystemId'],
                'subnet_id': response['SubnetId'],
                'ip_address': response.get('IpAddress', ''),
                'life_cycle_state': response['LifeCycleState']
            }
        except Exception as e:
            return {
                'success': False,
                'file_system_id': params.get('file_system_id', 'unknown'),
                'subnet_id': params.get('subnet_id', 'unknown'),
                'message': f"Error al crear mount target EFS: {str(e)}"
            }

    def _execute_delete_efs_mount_target(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un mount target EFS"""
        try:
            efs = boto3.client('efs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            efs.delete_mount_target(MountTargetId=params['mount_target_id'])

            return {
                'success': True,
                'mount_target_id': params['mount_target_id'],
                'message': 'Mount target EFS eliminado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'mount_target_id': params.get('mount_target_id', 'unknown'),
                'message': f"Error al eliminar mount target EFS: {str(e)}"
            }

    def _execute_list_fsx_file_systems(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista todos los file systems FSx"""
        try:
            fsx = boto3.client('fsx', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = fsx.describe_file_systems()

            file_systems = []
            for fs in response.get('FileSystems', []):
                file_systems.append({
                    'file_system_id': fs['FileSystemId'],
                    'file_system_type': fs['FileSystemType'],
                    'lifecycle': fs['Lifecycle'],
                    'storage_capacity': fs.get('StorageCapacity', 'N/A'),
                    'creation_time': fs['CreationTime'].isoformat() if fs.get('CreationTime') else 'N/A',
                    'dns_name': fs.get('DNSName', 'N/A'),
                    'network_interface_ids': fs.get('NetworkInterfaceIds', []),
                    'subnet_ids': fs.get('SubnetIds', []),
                    'deployment_type': fs.get('LustreConfiguration', {}).get('DeploymentType', 'N/A') if fs['FileSystemType'] == 'LUSTRE' else 'N/A'
                })

            return {
                'success': True,
                'file_systems': file_systems,
                'count': len(file_systems),
                'message': f'Encontrados {len(file_systems)} file systems FSx'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error al listar file systems FSx: {str(e)}"
            }

    def _execute_create_fsx_file_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo file system FSx"""
        try:
            fsx = boto3.client('fsx', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

            # Configuración base
            fs_config = {
                'FileSystemType': params['file_system_type'],
                'StorageCapacity': params['storage_capacity']
            }

            # Configuración específica por tipo
            if params['file_system_type'] == 'LUSTRE':
                lustre_config = {
                    'DeploymentType': params.get('deployment_type', 'PERSISTENT_1')
                }
                if 'per_unit_storage_throughput' in params:
                    lustre_config['PerUnitStorageThroughput'] = params['per_unit_storage_throughput']
                fs_config['LustreConfiguration'] = lustre_config

            # Configuración de red
            if 'subnet_ids' in params:
                fs_config['SubnetIds'] = params['subnet_ids']
            if 'security_group_ids' in params:
                fs_config['SecurityGroupIds'] = params['security_group_ids']

            response = fsx.create_file_system(**fs_config)
            fs = response['FileSystem']

            return {
                'success': True,
                'file_system_id': fs['FileSystemId'],
                'file_system_type': fs['FileSystemType'],
                'lifecycle': fs['Lifecycle'],
                'storage_capacity': fs.get('StorageCapacity', 'N/A'),
                'dns_name': fs.get('DNSName', 'N/A'),
                'creation_time': fs['CreationTime'].isoformat(),
                'message': f'File system FSx {fs["FileSystemId"]} creado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error al crear file system FSx: {str(e)}"
            }

    def _execute_delete_fsx_file_system(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un file system FSx"""
        try:
            fsx = boto3.client('fsx', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            fsx.delete_file_system(FileSystemId=params['file_system_id'])

            return {
                'success': True,
                'file_system_id': params['file_system_id'],
                'message': 'File system FSx eliminado exitosamente'
            }
        except Exception as e:
            return {
                'success': False,
                'file_system_id': params.get('file_system_id', 'unknown'),
                'message': f"Error al eliminar file system FSx: {str(e)}"
            }

    def _execute_describe_stack_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene los eventos de un stack de CloudFormation"""
        try:
            cf = boto3.client('cloudformation', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = cf.describe_stack_events(StackName=params['stack_name'])

            events = []
            for event in response.get('StackEvents', []):
                events.append({
                    'timestamp': event['Timestamp'].isoformat(),
                    'resource_status': event['ResourceStatus'],
                    'resource_type': event.get('ResourceType', 'N/A'),
                    'logical_resource_id': event.get('LogicalResourceId', 'N/A'),
                    'physical_resource_id': event.get('PhysicalResourceId', 'N/A'),
                    'resource_status_reason': event.get('ResourceStatusReason', 'N/A'),
                    'resource_properties': event.get('ResourceProperties', 'N/A')
                })

            return {
                'success': True,
                'stack_name': params['stack_name'],
                'events': events,
                'event_count': len(events),
                'message': f'Encontrados {len(events)} eventos para el stack {params["stack_name"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'stack_name': params.get('stack_name', 'unknown'),
                'message': f"Error al obtener eventos del stack: {str(e)}"
            }

    def _execute_describe_stack_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene los recursos de un stack de CloudFormation"""
        try:
            cf = boto3.client('cloudformation', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
            response = cf.describe_stack_resources(StackName=params['stack_name'])

            resources = []
            for resource in response.get('StackResources', []):
                resources.append({
                    'logical_resource_id': resource['LogicalResourceId'],
                    'physical_resource_id': resource.get('PhysicalResourceId', 'N/A'),
                    'resource_type': resource['ResourceType'],
                    'resource_status': resource['ResourceStatus'],
                    'timestamp': resource['Timestamp'].isoformat(),
                    'resource_status_reason': resource.get('ResourceStatusReason', 'N/A'),
                    'description': resource.get('Description', 'N/A')
                })

            return {
                'success': True,
                'stack_name': params['stack_name'],
                'resources': resources,
                'resource_count': len(resources),
                'message': f'Encontrados {len(resources)} recursos para el stack {params["stack_name"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'stack_name': params.get('stack_name', 'unknown'),
                'message': f"Error al obtener recursos del stack: {str(e)}"
            }


# Singleton
_mcp_server = None
_mcp_server = None

def get_mcp_server() -> AWSMCPServer:
    """Obtiene la instancia del servidor MCP"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = AWSMCPServer()
    return _mcp_server
