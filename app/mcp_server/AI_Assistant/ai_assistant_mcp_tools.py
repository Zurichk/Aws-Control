"""
AI Assistant MCP Tools - Herramientas para el asistente de IA de AWS
"""

import logging
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client

logger = logging.getLogger(__name__)


class AIAssistantMCPTools:
    """Herramientas MCP para el Asistente de IA de AWS"""

    def __init__(self):
        self.tools = [
            {
                "name": "ai_assistant_help",
                "description": "Obtener ayuda general sobre el asistente de IA",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "ai_assistant_explain_service",
                "description": "Explicar un servicio específico de AWS",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Nombre del servicio AWS a explicar (ej: EC2, S3, Lambda)"
                        }
                    },
                    "required": ["service_name"]
                }
            },
            {
                "name": "ai_assistant_recommend_service",
                "description": "Recomendar servicios AWS para un caso de uso específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "use_case": {
                            "type": "string",
                            "description": "Descripción del caso de uso o problema a resolver"
                        }
                    },
                    "required": ["use_case"]
                }
            },
            {
                "name": "ai_assistant_get_service_status",
                "description": "Obtener el estado actual de un servicio AWS específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {
                            "type": "string",
                            "description": "Nombre del servicio AWS"
                        }
                    },
                    "required": ["service_name"]
                }
            },
            {
                "name": "ai_assistant_list_services_by_category",
                "description": "Listar servicios AWS por categoría",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Categoría de servicios (ej: compute, storage, database, networking, security, analytics, ml_ai, management)",
                            "enum": ["compute", "storage", "database", "networking", "security", "analytics", "ml_ai", "management", "containers", "integration", "messaging"]
                        }
                    },
                    "required": ["category"]
                }
            }
        ]

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para el Asistente de IA"""
        return [
            {
                'name': 'ai_assistant_help',
                'description': 'Obtener ayuda general sobre el asistente de IA',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                },
                'function': lambda params=None, **kwargs: self._help()
            },
            {
                'name': 'ai_assistant_explain_service',
                'description': 'Explicar un servicio específico de AWS',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'service_name': {
                            'type': 'string',
                            'description': 'Nombre del servicio AWS a explicar (ej: EC2, S3, Lambda)'
                        }
                    },
                    'required': ['service_name']
                },
                'function': lambda params=None, **kwargs: self._explain_service(params.get('service_name', '') if params else '')
            },
            {
                'name': 'ai_assistant_recommend_service',
                'description': 'Recomendar servicios AWS para un caso de uso específico',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'use_case': {
                            'type': 'string',
                            'description': 'Descripción del caso de uso o problema a resolver'
                        }
                    },
                    'required': ['use_case']
                },
                'function': lambda params=None, **kwargs: self._recommend_service(params.get('use_case', '') if params else '')
            },
            {
                'name': 'ai_assistant_get_service_status',
                'description': 'Obtener el estado actual de un servicio AWS específico',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'service_name': {
                            'type': 'string',
                            'description': 'Nombre del servicio AWS'
                        }
                    },
                    'required': ['service_name']
                },
                'function': lambda params=None, **kwargs: self._get_service_status(params.get('service_name', '') if params else '')
            },
            {
                'name': 'ai_assistant_list_services_by_category',
                'description': 'Listar servicios AWS por categoría',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'category': {
                            'type': 'string',
                            'description': 'Categoría de servicios (ej: compute, storage, database, networking, security, analytics, ml_ai, management)',
                            'enum': ['compute', 'storage', 'database', 'networking', 'security', 'analytics', 'ml_ai', 'management', 'containers', 'integration', 'messaging']
                        }
                    },
                    'required': ['category']
                },
                'function': lambda params=None, **kwargs: self._list_services_by_category(params.get('category', '') if params else '')
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar una herramienta específica"""
        try:
            if tool_name == "ai_assistant_help":
                return self._help(**parameters)
            elif tool_name == "ai_assistant_explain_service":
                return self._explain_service(parameters.get("service_name", ""))
            elif tool_name == "ai_assistant_recommend_service":
                return self._recommend_service(parameters.get("use_case", ""))
            elif tool_name == "ai_assistant_get_service_status":
                return self._get_service_status(parameters.get("service_name", ""))
            elif tool_name == "ai_assistant_list_services_by_category":
                return self._list_services_by_category(parameters.get("category", ""))
            else:
                raise ValueError(f"Herramienta no encontrada: {tool_name}")
        except Exception as e:
            logger.error(f"Error ejecutando herramienta {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

    def _help(self, **kwargs) -> Dict[str, Any]:
        """Ayuda general del asistente"""
        return {
            "success": True,
            "message": "Asistente de IA para AWS - Panel de Control",
            "capabilities": [
                "Explicar servicios AWS",
                "Recomendar servicios para casos de uso específicos",
                "Ayudar con mejores prácticas",
                "Guiar en el uso del panel web",
                "Ejecutar acciones reales en AWS"
            ],
            "available_categories": [
                "compute", "storage", "database", "networking",
                "security", "analytics", "ml_ai", "management",
                "containers", "integration", "messaging"
            ]
        }

    def _explain_service(self, service_name: str = "", **kwargs) -> Dict[str, Any]:
        """Explicar un servicio específico de AWS"""
        services_info = {
            "ec2": {
                "name": "Amazon EC2",
                "description": "Instancias de servidor virtual en la nube",
                "use_cases": ["Servidores web", "Aplicaciones empresariales", "Bases de datos", "Procesamiento por lotes"],
                "category": "compute"
            },
            "s3": {
                "name": "Amazon S3",
                "description": "Almacenamiento de objetos escalable y duradero",
                "use_cases": ["Backup y recuperación", "Almacenamiento de archivos estáticos", "Data lakes", "Sitios web estáticos"],
                "category": "storage"
            },
            "lambda": {
                "name": "AWS Lambda",
                "description": "Computación serverless - ejecuta código sin servidores",
                "use_cases": ["APIs serverless", "Procesamiento de eventos", "Tareas programadas", "Procesamiento de datos en tiempo real"],
                "category": "compute"
            },
            "rds": {
                "name": "Amazon RDS",
                "description": "Bases de datos relacionales administradas",
                "use_cases": ["Aplicaciones web", "Sistemas OLTP", "Data warehousing", "Aplicaciones móviles"],
                "category": "database"
            },
            "vpc": {
                "name": "Amazon VPC",
                "description": "Redes virtuales privadas en AWS",
                "use_cases": ["Aislamiento de red", "Conectividad híbrida", "Seguridad de red", "Multi-tenancy"],
                "category": "networking"
            },
            "iam": {
                "name": "AWS IAM",
                "description": "Gestión de identidades y accesos",
                "use_cases": ["Control de acceso", "Autenticación", "Autorización", "Auditoría de seguridad"],
                "category": "security"
            }
        }

        service = services_info.get(service_name.lower())
        if not service:
            return {
                "success": False,
                "error": f"Servicio '{service_name}' no encontrado. Servicios disponibles: {', '.join(services_info.keys())}"
            }

        return {
            "success": True,
            "service": service
        }

    def _recommend_service(self, use_case: str = "", **kwargs) -> Dict[str, Any]:
        """Recomendar servicios para un caso de uso"""
        recommendations = {
            "servidor web": ["EC2", "ELB", "RDS", "CloudFront"],
            "almacenamiento archivos": ["S3", "EFS", "FSx"],
            "base de datos": ["RDS", "DynamoDB", "Aurora"],
            "procesamiento datos": ["Lambda", "Glue", "Athena", "EMR"],
            "machine learning": ["SageMaker", "Rekognition", "Bedrock"],
            "mensajeria": ["SNS", "SQS", "EventBridge"],
            "redes": ["VPC", "Route 53", "CloudFront", "API Gateway"],
            "seguridad": ["IAM", "KMS", "Config", "GuardDuty"],
            "contenedores": ["ECS", "EKS", "ECR"],
            "infraestructura como codigo": ["CloudFormation", "CDK"]
        }

        # Buscar recomendaciones basadas en palabras clave
        matched_services = []
        use_case_lower = use_case.lower()

        for keyword, services in recommendations.items():
            if keyword in use_case_lower:
                matched_services.extend(services)

        # Remover duplicados
        matched_services = list(set(matched_services))

        if not matched_services:
            matched_services = ["EC2", "S3", "Lambda", "RDS"]  # Servicios básicos por defecto

        return {
            "success": True,
            "use_case": use_case,
            "recommendations": matched_services,
            "explanation": f"Para '{use_case}', recomiendo los siguientes servicios AWS: {', '.join(matched_services)}"
        }

    def _get_service_status(self, service_name: str = "", **kwargs) -> Dict[str, Any]:
        """Obtener estado de un servicio AWS"""
        try:
            # Intentar obtener información básica del servicio
            if service_name.lower() == "ec2":
                ec2 = get_aws_client('ec2')
                instances = ec2.describe_instances()
                running_count = sum(1 for reservation in instances['Reservations']
                                  for instance in reservation['Instances']
                                  if instance['State']['Name'] == 'running')

                return {
                    "success": True,
                    "service": "EC2",
                    "status": "operational",
                    "instances_running": running_count,
                    "message": f"EC2 operativo con {running_count} instancias ejecutándose"
                }

            elif service_name.lower() == "s3":
                s3 = get_aws_client('s3')
                buckets = s3.list_buckets()
                bucket_count = len(buckets.get('Buckets', []))

                return {
                    "success": True,
                    "service": "S3",
                    "status": "operational",
                    "buckets_count": bucket_count,
                    "message": f"S3 operativo con {bucket_count} buckets"
                }

            elif service_name.lower() == "rds":
                rds = get_aws_client('rds')
                instances = rds.describe_db_instances()
                db_count = len(instances.get('DBInstances', []))

                return {
                    "success": True,
                    "service": "RDS",
                    "status": "operational",
                    "databases_count": db_count,
                    "message": f"RDS operativo con {db_count} instancias de base de datos"
                }

            else:
                return {
                    "success": True,
                    "service": service_name,
                    "status": "unknown",
                    "message": f"Estado del servicio {service_name} no disponible en este momento"
                }

        except Exception as e:
            return {
                "success": False,
                "service": service_name,
                "error": str(e),
                "message": f"Error obteniendo estado del servicio {service_name}"
            }

    def _list_services_by_category(self, category: str = "", **kwargs) -> Dict[str, Any]:
        """Listar servicios por categoría"""
        categories = {
            "compute": ["EC2", "Lambda", "ECS", "EKS", "Batch", "Lightsail"],
            "storage": ["S3", "EFS", "FSx", "EBS", "Glacier", "Storage Gateway"],
            "database": ["RDS", "DynamoDB", "Aurora", "Redshift", "Neptune", "DocumentDB"],
            "networking": ["VPC", "Route 53", "CloudFront", "API Gateway", "ELB", "Direct Connect"],
            "security": ["IAM", "KMS", "Config", "GuardDuty", "Inspector", "Macie"],
            "analytics": ["Athena", "Glue", "EMR", "Kinesis", "QuickSight", "Data Pipeline"],
            "ml_ai": ["SageMaker", "Rekognition", "Bedrock", "Comprehend", "Polly", "Transcribe"],
            "management": ["CloudFormation", "CloudWatch", "Systems Manager", "Trusted Advisor", "Cost Explorer"],
            "containers": ["ECS", "EKS", "ECR", "App Runner"],
            "integration": ["EventBridge", "Step Functions", "MQ", "AppSync"],
            "messaging": ["SNS", "SQS", "SES", "Connect"]
        }

        services = categories.get(category.lower(), [])

        if not services:
            return {
                "success": False,
                "error": f"Categoría '{category}' no encontrada. Categorías disponibles: {', '.join(categories.keys())}"
            }

        return {
            "success": True,
            "category": category,
            "services": services,
            "count": len(services)
        }


# Instancia global para compatibilidad
ai_assistant_tools = AIAssistantMCPTools()

# Diccionario de herramientas para compatibilidad con app.py
AI_ASSISTANT_MCP_TOOLS = {
    "ai_assistant_help": {
        "name": "ai_assistant_help",
        "description": "Obtener ayuda general sobre el asistente de IA",
        "parameters": {}
    },
    "ai_assistant_explain_service": {
        "name": "ai_assistant_explain_service",
        "description": "Explicar un servicio específico de AWS",
        "parameters": {
            "service_name": {"type": "string", "description": "Nombre del servicio AWS"}
        }
    },
    "ai_assistant_recommend_service": {
        "name": "ai_assistant_recommend_service",
        "description": "Recomendar servicios AWS para un caso de uso específico",
        "parameters": {
            "use_case": {"type": "string", "description": "Descripción del caso de uso"}
        }
    },
    "ai_assistant_get_service_status": {
        "name": "ai_assistant_get_service_status",
        "description": "Obtener el estado actual de un servicio AWS específico",
        "parameters": {
            "service_name": {"type": "string", "description": "Nombre del servicio AWS"}
        }
    },
    "ai_assistant_list_services_by_category": {
        "name": "ai_assistant_list_services_by_category",
        "description": "Listar servicios AWS por categoría",
        "parameters": {
            "category": {"type": "string", "description": "Categoría de servicios"}
        }
    }
}