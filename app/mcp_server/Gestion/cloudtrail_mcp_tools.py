"""
CloudTrail MCP Tools - Herramientas para gestión de auditoría y monitoreo
"""

import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class CloudTrailMCPTools:
    """Herramientas MCP para AWS CloudTrail"""

    def __init__(self):
        self.client = boto3.client('cloudtrail')
        self.tools = [
            {
                "name": "cloudtrail_list_trails",
                "description": "Lista todos los trails de CloudTrail configurados en la cuenta",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "cloudtrail_get_trail",
                "description": "Obtiene información detallada de un trail específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_create_trail",
                "description": "Crea un nuevo trail de CloudTrail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        },
                        "s3_bucket_name": {
                            "type": "string",
                            "description": "Nombre del bucket S3 para almacenar logs"
                        },
                        "s3_key_prefix": {
                            "type": "string",
                            "description": "Prefijo para los archivos en S3"
                        },
                        "sns_topic_name": {
                            "type": "string",
                            "description": "Nombre del topic SNS para notificaciones"
                        },
                        "is_multi_region_trail": {
                            "type": "boolean",
                            "description": "Si el trail debe ser multi-región",
                            "default": False
                        },
                        "include_global_service_events": {
                            "type": "boolean",
                            "description": "Incluir eventos de servicios globales",
                            "default": True
                        },
                        "is_organization_trail": {
                            "type": "boolean",
                            "description": "Si es un trail de organización",
                            "default": False
                        },
                        "enable_log_file_validation": {
                            "type": "boolean",
                            "description": "Habilitar validación de archivos de log",
                            "default": True
                        }
                    },
                    "required": ["name", "s3_bucket_name"]
                }
            },
            {
                "name": "cloudtrail_delete_trail",
                "description": "Elimina un trail de CloudTrail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail a eliminar"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_start_logging",
                "description": "Inicia el logging para un trail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_stop_logging",
                "description": "Detiene el logging para un trail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_lookup_events",
                "description": "Busca eventos en CloudTrail con filtros opcionales",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "Fecha/hora de inicio (ISO 8601)",
                            "format": "date-time"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Fecha/hora de fin (ISO 8601)",
                            "format": "date-time"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 50
                        },
                        "lookup_attributes": {
                            "type": "array",
                            "description": "Atributos para filtrar eventos",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "attribute_key": {
                                        "type": "string",
                                        "enum": ["EventId", "EventName", "Username", "ResourceType", "ResourceName", "EventSource", "AccessKeyId"]
                                    },
                                    "attribute_value": {
                                        "type": "string"
                                    }
                                },
                                "required": ["attribute_key", "attribute_value"]
                            }
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "cloudtrail_get_trail_status",
                "description": "Obtiene el estado actual de un trail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_get_insights_selectors",
                "description": "Obtiene los selectores de insights para un trail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        }
                    },
                    "required": ["trail_name"]
                }
            },
            {
                "name": "cloudtrail_put_insight_selectors",
                "description": "Configura selectores de insights para un trail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trail_name": {
                            "type": "string",
                            "description": "Nombre del trail"
                        },
                        "insight_selectors": {
                            "type": "array",
                            "description": "Lista de selectores de insights",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "insight_type": {
                                        "type": "string",
                                        "enum": ["ApiCallRateInsight", "ApiErrorRateInsight"]
                                    }
                                },
                                "required": ["insight_type"]
                            }
                        }
                    },
                    "required": ["trail_name", "insight_selectors"]
                }
            }
        ]

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas MCP disponibles"""
        return self.tools

    def list_trails(self) -> Dict[str, Any]:
        """Lista todos los trails de CloudTrail"""
        try:
            response = self.client.describe_trails()
            trails = response.get('trailList', [])

            return {
                "success": True,
                "trails": trails,
                "count": len(trails)
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def get_trail(self, trail_name: str) -> Dict[str, Any]:
        """Obtiene información detallada de un trail"""
        try:
            response = self.client.describe_trails(trailNameList=[trail_name])
            trails = response.get('trailList', [])

            if not trails:
                return {
                    "success": False,
                    "error": f"Trail '{trail_name}' no encontrado"
                }

            trail = trails[0]

            # Obtener estado del trail
            status_response = self.client.get_trail_status(Name=trail_name)
            trail['Status'] = status_response

            return {
                "success": True,
                "trail": trail
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def create_trail(self, name: str, s3_bucket_name: str, **kwargs) -> Dict[str, Any]:
        """Crea un nuevo trail de CloudTrail"""
        try:
            params = {
                'Name': name,
                'S3BucketName': s3_bucket_name
            }

            # Parámetros opcionales
            if kwargs.get('s3_key_prefix'):
                params['S3KeyPrefix'] = kwargs['s3_key_prefix']
            if kwargs.get('sns_topic_name'):
                params['SnsTopicName'] = kwargs['sns_topic_name']
            if kwargs.get('is_multi_region_trail'):
                params['IsMultiRegionTrail'] = kwargs['is_multi_region_trail']
            if kwargs.get('include_global_service_events') is not None:
                params['IncludeGlobalServiceEvents'] = kwargs['include_global_service_events']
            if kwargs.get('is_organization_trail'):
                params['IsOrganizationTrail'] = kwargs['is_organization_trail']
            if kwargs.get('enable_log_file_validation') is not None:
                params['EnableLogFileValidation'] = kwargs['enable_log_file_validation']

            response = self.client.create_trail(**params)

            return {
                "success": True,
                "trail_arn": response.get('TrailARN'),
                "message": f"Trail '{name}' creado exitosamente"
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def delete_trail(self, trail_name: str) -> Dict[str, Any]:
        """Elimina un trail de CloudTrail"""
        try:
            self.client.delete_trail(Name=trail_name)
            return {
                "success": True,
                "message": f"Trail '{trail_name}' eliminado exitosamente"
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def start_logging(self, trail_name: str) -> Dict[str, Any]:
        """Inicia el logging para un trail"""
        try:
            self.client.start_logging(Name=trail_name)
            return {
                "success": True,
                "message": f"Logging iniciado para trail '{trail_name}'"
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def stop_logging(self, trail_name: str) -> Dict[str, Any]:
        """Detiene el logging para un trail"""
        try:
            self.client.stop_logging(Name=trail_name)
            return {
                "success": True,
                "message": f"Logging detenido para trail '{trail_name}'"
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def lookup_events(self, **kwargs) -> Dict[str, Any]:
        """Busca eventos en CloudTrail con filtros opcionales"""
        try:
            params = {}

            if kwargs.get('start_time'):
                params['StartTime'] = datetime.fromisoformat(kwargs['start_time'].replace('Z', '+00:00'))
            if kwargs.get('end_time'):
                params['EndTime'] = datetime.fromisoformat(kwargs['end_time'].replace('Z', '+00:00'))
            if kwargs.get('max_results'):
                params['MaxResults'] = kwargs['max_results']
            if kwargs.get('lookup_attributes'):
                params['LookupAttributes'] = kwargs['lookup_attributes']

            response = self.client.lookup_events(**params)
            events = response.get('Events', [])

            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def get_trail_status(self, trail_name: str) -> Dict[str, Any]:
        """Obtiene el estado actual de un trail"""
        try:
            response = self.client.get_trail_status(Name=trail_name)
            return {
                "success": True,
                "status": response
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def get_insight_selectors(self, trail_name: str) -> Dict[str, Any]:
        """Obtiene los selectores de insights para un trail"""
        try:
            response = self.client.get_insight_selectors(TrailName=trail_name)
            selectors = response.get('InsightSelectors', [])

            return {
                "success": True,
                "trail_name": trail_name,
                "insight_selectors": selectors
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }

    def put_insight_selectors(self, trail_name: str, insight_selectors: List[Dict[str, str]]) -> Dict[str, Any]:
        """Configura selectores de insights para un trail"""
        try:
            response = self.client.put_insight_selectors(
                TrailName=trail_name,
                InsightSelectors=insight_selectors
            )

            return {
                "success": True,
                "trail_name": trail_name,
                "insight_selectors": response.get('InsightSelectors', [])
            }
        except ClientError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.response['Error']['Code']
            }


# Instancia global para uso en el servidor MCP
cloudtrail_tools = CloudTrailMCPTools()