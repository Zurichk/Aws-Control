"""
MCP Tools para AWS API Gateway
Herramientas para gestión de APIs REST, HTTP y WebSocket
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class APIGatewayMCPTools:
    """Herramientas MCP para operaciones con AWS API Gateway"""

    # Constantes para descripciones
    DESC_REST_API_ID = 'ID de la API REST'
    DESC_RESOURCE_ID = 'ID del recurso'
    DESC_METHOD = 'Método HTTP (GET, POST, PUT, DELETE, etc.)'
    DESC_STATUS_CODE = 'Código de estado HTTP'
    DESC_API_KEY = 'Clave de API'
    DESC_USAGE_PLAN_ID = 'ID del plan de uso'
    DESC_DEPLOYMENT_ID = 'ID del deployment'
    DESC_STAGE_NAME = 'Nombre del stage'
    DESC_DOMAIN_NAME = 'Nombre de dominio personalizado'
    DESC_BASE_PATH = 'Ruta base'
    DESC_PATH_PART = 'Parte de la ruta'

    def __init__(self):
        self.api_client = None

    def _get_client(self):
        """Obtiene el cliente API Gateway"""
        if self.api_client is None:
            self.api_client = get_aws_client('apigateway')
        return self.api_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para API Gateway"""
        return [
            {
                'name': 'apigateway_get_rest_apis',
                'description': 'Lista APIs REST',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Límite de resultados', 'default': 25},
                        'position': {'type': 'string', 'description': 'Posición para paginación'}
                    }
                }
            },
            {
                'name': 'apigateway_get_rest_api',
                'description': 'Obtiene detalles de una API REST',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID}
                    },
                    'required': ['rest_api_id']
                }
            },
            {
                'name': 'apigateway_create_rest_api',
                'description': 'Crea una nueva API REST',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Nombre de la API'},
                        'description': {'type': 'string', 'description': 'Descripción de la API'},
                        'endpoint_configuration': {
                            'type': 'object',
                            'description': 'Configuración de endpoints',
                            'properties': {
                                'types': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Tipos de endpoint'}
                            }
                        },
                        'api_key_source_type': {'type': 'string', 'description': 'Tipo de fuente de API key', 'enum': ['HEADER', 'QUERY']},
                        'binary_media_types': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Tipos de media binarios'}
                    },
                    'required': ['name']
                }
            },
            {
                'name': 'apigateway_delete_rest_api',
                'description': 'Elimina una API REST',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID}
                    },
                    'required': ['rest_api_id']
                }
            },
            {
                'name': 'apigateway_get_resources',
                'description': 'Lista recursos de una API',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'limit': {'type': 'integer', 'description': 'Límite de resultados', 'default': 25},
                        'position': {'type': 'string', 'description': 'Posición para paginación'}
                    },
                    'required': ['rest_api_id']
                }
            },
            {
                'name': 'apigateway_create_resource',
                'description': 'Crea un recurso en una API',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'parent_id': {'type': 'string', 'description': 'ID del recurso padre'},
                        'path_part': {'type': 'string', 'description': self.DESC_PATH_PART}
                    },
                    'required': ['rest_api_id', 'parent_id', 'path_part']
                }
            },
            {
                'name': 'apigateway_delete_resource',
                'description': 'Elimina un recurso de una API',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID}
                    },
                    'required': ['rest_api_id', 'resource_id']
                }
            },
            {
                'name': 'apigateway_get_method',
                'description': 'Obtiene un método de un recurso',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID},
                        'method': {'type': 'string', 'description': self.DESC_METHOD},
                        'position': {'type': 'string', 'description': 'Posición para paginación'}
                    },
                    'required': ['rest_api_id', 'resource_id', 'method']
                }
            },
            {
                'name': 'apigateway_put_method',
                'description': 'Crea o actualiza un método en un recurso',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID},
                        'method': {'type': 'string', 'description': self.DESC_METHOD},
                        'authorization_type': {'type': 'string', 'description': 'Tipo de autorización', 'enum': ['NONE', 'AWS_IAM', 'COGNITO_USER_POOLS', 'CUSTOM']},
                        'api_key_required': {'type': 'boolean', 'description': 'Requiere API key', 'default': False},
                        'operation_name': {'type': 'string', 'description': 'Nombre de la operación'},
                        'request_parameters': {'type': 'object', 'description': 'Parámetros de request'},
                        'request_models': {'type': 'object', 'description': 'Modelos de request'}
                    },
                    'required': ['rest_api_id', 'resource_id', 'method']
                }
            },
            {
                'name': 'apigateway_put_integration',
                'description': 'Crea o actualiza una integración para un método',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID},
                        'method': {'type': 'string', 'description': self.DESC_METHOD},
                        'type': {'type': 'string', 'description': 'Tipo de integración', 'enum': ['HTTP', 'AWS', 'MOCK', 'HTTP_PROXY', 'AWS_PROXY']},
                        'integration_method': {'type': 'string', 'description': 'Método de integración'},
                        'uri': {'type': 'string', 'description': 'URI del backend'},
                        'credentials': {'type': 'string', 'description': 'Credenciales para la integración'},
                        'request_parameters': {'type': 'object', 'description': 'Parámetros de request de integración'},
                        'request_templates': {'type': 'object', 'description': 'Templates de request'},
                        'passthrough_behavior': {'type': 'string', 'description': 'Comportamiento de passthrough', 'enum': ['WHEN_NO_MATCH', 'WHEN_NO_TEMPLATES', 'NEVER']},
                        'content_handling': {'type': 'string', 'description': 'Manejo de contenido', 'enum': ['CONVERT_TO_BINARY', 'CONVERT_TO_TEXT']}
                    },
                    'required': ['rest_api_id', 'resource_id', 'method', 'type']
                }
            },
            {
                'name': 'apigateway_put_method_response',
                'description': 'Crea o actualiza una respuesta de método',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID},
                        'method': {'type': 'string', 'description': self.DESC_METHOD},
                        'status_code': {'type': 'string', 'description': self.DESC_STATUS_CODE},
                        'response_parameters': {'type': 'object', 'description': 'Parámetros de respuesta'},
                        'response_models': {'type': 'object', 'description': 'Modelos de respuesta'}
                    },
                    'required': ['rest_api_id', 'resource_id', 'method', 'status_code']
                }
            },
            {
                'name': 'apigateway_put_integration_response',
                'description': 'Crea o actualiza una respuesta de integración',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'resource_id': {'type': 'string', 'description': self.DESC_RESOURCE_ID},
                        'method': {'type': 'string', 'description': self.DESC_METHOD},
                        'status_code': {'type': 'string', 'description': self.DESC_STATUS_CODE},
                        'response_parameters': {'type': 'object', 'description': 'Parámetros de respuesta de integración'},
                        'response_templates': {'type': 'object', 'description': 'Templates de respuesta'},
                        'content_handling': {'type': 'string', 'description': 'Manejo de contenido', 'enum': ['CONVERT_TO_BINARY', 'CONVERT_TO_TEXT']}
                    },
                    'required': ['rest_api_id', 'resource_id', 'method', 'status_code']
                }
            },
            {
                'name': 'apigateway_create_deployment',
                'description': 'Crea un deployment de una API',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'stage_name': {'type': 'string', 'description': self.DESC_STAGE_NAME},
                        'stage_description': {'type': 'string', 'description': 'Descripción del stage'},
                        'description': {'type': 'string', 'description': 'Descripción del deployment'},
                        'cache_cluster_enabled': {'type': 'boolean', 'description': 'Habilitar cluster de cache'},
                        'cache_cluster_size': {'type': 'string', 'description': 'Tamaño del cluster de cache', 'enum': ['0.5', '1.6', '6.1', '13.5', '28.4', '58.2', '118', '237']},
                        'variables': {'type': 'object', 'description': 'Variables del stage'},
                        'canary_settings': {
                            'type': 'object',
                            'description': 'Configuración de canary',
                            'properties': {
                                'percent_traffic': {'type': 'number', 'description': 'Porcentaje de tráfico'},
                                'stage_variable_overrides': {'type': 'object', 'description': 'Variables del stage para canary'},
                                'use_stage_cache': {'type': 'boolean', 'description': 'Usar cache del stage'}
                            }
                        }
                    },
                    'required': ['rest_api_id', 'stage_name']
                }
            },
            {
                'name': 'apigateway_get_stages',
                'description': 'Lista stages de una API',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'deployment_id': {'type': 'string', 'description': self.DESC_DEPLOYMENT_ID}
                    },
                    'required': ['rest_api_id']
                }
            },
            {
                'name': 'apigateway_get_api_keys',
                'description': 'Lista API keys',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Límite de resultados', 'default': 25},
                        'position': {'type': 'string', 'description': 'Posición para paginación'},
                        'name_query': {'type': 'string', 'description': 'Filtro por nombre'},
                        'customer_id': {'type': 'string', 'description': 'ID del cliente'}
                    }
                }
            },
            {
                'name': 'apigateway_create_api_key',
                'description': 'Crea una API key',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Nombre de la API key'},
                        'description': {'type': 'string', 'description': 'Descripción'},
                        'enabled': {'type': 'boolean', 'description': 'Habilitada', 'default': True},
                        'generate_distinct_id': {'type': 'boolean', 'description': 'Generar ID distintivo', 'default': False},
                        'value': {'type': 'string', 'description': 'Valor de la API key'},
                        'stage_keys': {
                            'type': 'array',
                            'description': 'Claves de stage',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'rest_api_id': {'type': 'string'},
                                    'stage_name': {'type': 'string'}
                                },
                                'required': ['rest_api_id', 'stage_name']
                            }
                        },
                        'customer_id': {'type': 'string', 'description': 'ID del cliente'},
                        'tags': {'type': 'object', 'description': 'Tags'}
                    },
                    'required': ['name']
                }
            },
            {
                'name': 'apigateway_get_usage_plans',
                'description': 'Lista planes de uso',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Límite de resultados', 'default': 25},
                        'position': {'type': 'string', 'description': 'Posición para paginación'}
                    }
                }
            },
            {
                'name': 'apigateway_create_usage_plan',
                'description': 'Crea un plan de uso',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'description': 'Nombre del plan'},
                        'description': {'type': 'string', 'description': 'Descripción'},
                        'api_stages': {
                            'type': 'array',
                            'description': 'Stages de API',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'api_id': {'type': 'string'},
                                    'stage': {'type': 'string'},
                                    'throttle': {
                                        'type': 'object',
                                        'properties': {
                                            'burst_limit': {'type': 'integer'},
                                            'rate_limit': {'type': 'number'}
                                        }
                                    }
                                }
                            }
                        },
                        'throttle': {
                            'type': 'object',
                            'description': 'Configuración de throttle global',
                            'properties': {
                                'burst_limit': {'type': 'integer'},
                                'rate_limit': {'type': 'number'}
                            }
                        },
                        'quota': {
                            'type': 'object',
                            'description': 'Configuración de quota',
                            'properties': {
                                'limit': {'type': 'integer'},
                                'offset': {'type': 'integer'},
                                'period': {'type': 'string', 'enum': ['DAY', 'WEEK', 'MONTH']}
                            }
                        }
                    },
                    'required': ['name']
                }
            },
            {
                'name': 'apigateway_create_domain_name',
                'description': 'Crea un nombre de dominio personalizado',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'domain_name': {'type': 'string', 'description': self.DESC_DOMAIN_NAME},
                        'certificate_name': {'type': 'string', 'description': 'Nombre del certificado'},
                        'certificate_body': {'type': 'string', 'description': 'Cuerpo del certificado'},
                        'certificate_private_key': {'type': 'string', 'description': 'Clave privada del certificado'},
                        'certificate_chain': {'type': 'string', 'description': 'Cadena del certificado'},
                        'certificate_arn': {'type': 'string', 'description': 'ARN del certificado'},
                        'regional_certificate_name': {'type': 'string', 'description': 'Nombre del certificado regional'},
                        'regional_certificate_arn': {'type': 'string', 'description': 'ARN del certificado regional'},
                        'endpoint_configuration': {
                            'type': 'object',
                            'description': 'Configuración de endpoint',
                            'properties': {
                                'types': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        },
                        'tags': {'type': 'object', 'description': 'Tags'},
                        'security_policy': {'type': 'string', 'description': 'Política de seguridad', 'enum': ['TLS_1_0', 'TLS_1_2']}
                    },
                    'required': ['domain_name']
                }
            },
            {
                'name': 'apigateway_create_base_path_mapping',
                'description': 'Crea un mapeo de ruta base',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'domain_name': {'type': 'string', 'description': self.DESC_DOMAIN_NAME},
                        'base_path': {'type': 'string', 'description': self.DESC_BASE_PATH},
                        'rest_api_id': {'type': 'string', 'description': self.DESC_REST_API_ID},
                        'stage': {'type': 'string', 'description': self.DESC_STAGE_NAME}
                    },
                    'required': ['domain_name', 'rest_api_id']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de API Gateway"""
        try:
            if tool_name == 'apigateway_get_rest_apis':
                return self._get_rest_apis(**parameters)
            elif tool_name == 'apigateway_get_rest_api':
                return self._get_rest_api(**parameters)
            elif tool_name == 'apigateway_create_rest_api':
                return self._create_rest_api(**parameters)
            elif tool_name == 'apigateway_delete_rest_api':
                return self._delete_rest_api(**parameters)
            elif tool_name == 'apigateway_get_resources':
                return self._get_resources(**parameters)
            elif tool_name == 'apigateway_create_resource':
                return self._create_resource(**parameters)
            elif tool_name == 'apigateway_delete_resource':
                return self._delete_resource(**parameters)
            elif tool_name == 'apigateway_get_method':
                return self._get_method(**parameters)
            elif tool_name == 'apigateway_put_method':
                return self._put_method(**parameters)
            elif tool_name == 'apigateway_put_integration':
                return self._put_integration(**parameters)
            elif tool_name == 'apigateway_put_method_response':
                return self._put_method_response(**parameters)
            elif tool_name == 'apigateway_put_integration_response':
                return self._put_integration_response(**parameters)
            elif tool_name == 'apigateway_create_deployment':
                return self._create_deployment(**parameters)
            elif tool_name == 'apigateway_get_stages':
                return self._get_stages(**parameters)
            elif tool_name == 'apigateway_get_api_keys':
                return self._get_api_keys(**parameters)
            elif tool_name == 'apigateway_create_api_key':
                return self._create_api_key(**parameters)
            elif tool_name == 'apigateway_get_usage_plans':
                return self._get_usage_plans(**parameters)
            elif tool_name == 'apigateway_create_usage_plan':
                return self._create_usage_plan(**parameters)
            elif tool_name == 'apigateway_create_domain_name':
                return self._create_domain_name(**parameters)
            elif tool_name == 'apigateway_create_base_path_mapping':
                return self._create_base_path_mapping(**parameters)
            else:
                return {'error': f'Herramienta API Gateway no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta API Gateway {tool_name}: {str(e)}'}

    def _get_rest_apis(self, **kwargs) -> Dict[str, Any]:
        """Lista APIs REST"""
        client = self._get_client()

        api_params = {}
        if kwargs.get('limit'):
            api_kwargs['limit'] = kwargs.get('limit')
        if kwargs.get('position'):
            api_kwargs['position'] = kwargs.get('position')

        response = client.get_rest_apis(**api_params)

        apis = []
        for api in response.get('items', []):
            apis.append({
                'id': api.get('id'),
                'name': api.get('name'),
                'description': api.get('description'),
                'created_date': api.get('createdDate'),
                'api_key_source_type': api.get('apiKeySourceType'),
                'endpoint_configuration': api.get('endpointConfiguration'),
                'binary_media_types': api.get('binaryMediaTypes', [])
            })

        return {
            'apis': apis,
            'total_count': len(apis),
            'position': response.get('position')
        }

    def _get_rest_api(self, **kwargs) -> Dict[str, Any]:
        """Obtiene detalles de una API REST"""
        client = self._get_client()

        response = client.get_rest_api(restApiId=kwargs.get('rest_api_id'))

        return {
            'api': {
                'id': response.get('id'),
                'name': response.get('name'),
                'description': response.get('description'),
                'created_date': response.get('createdDate'),
                'api_key_source_type': response.get('apiKeySourceType'),
                'endpoint_configuration': response.get('endpointConfiguration'),
                'binary_media_types': response.get('binaryMediaTypes', []),
                'minimum_compression_size': response.get('minimumCompressionSize'),
                'tags': response.get('tags', {})
            }
        }

    def _create_rest_api(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva API REST"""
        client = self._get_client()

        api_params = {
            'name': kwargs.get('name')
        }

        if kwargs.get('description'):
            api_kwargs['description'] = kwargs.get('description')
        if kwargs.get('endpoint_configuration'):
            api_kwargs['endpointConfiguration'] = kwargs.get('endpoint_configuration')
        if kwargs.get('api_key_source_type'):
            api_kwargs['apiKeySourceType'] = kwargs.get('api_key_source_type')
        if kwargs.get('binary_media_types'):
            api_kwargs['binaryMediaTypes'] = kwargs.get('binary_media_types')

        response = client.create_rest_api(**api_params)

        return {
            'message': f'API REST {kwargs.get("name")} creada exitosamente',
            'api_id': response.get('id'),
            'api_name': response.get('name')
        }

    def _delete_rest_api(self, **kwargs) -> Dict[str, Any]:
        """Elimina una API REST"""
        client = self._get_client()

        client.delete_rest_api(restApiId=kwargs.get('rest_api_id'))

        return {
            'message': f'API REST {kwargs.get("rest_api_id")} eliminada exitosamente'
        }

    def _get_resources(self, **kwargs) -> Dict[str, Any]:
        """Lista recursos de una API"""
        client = self._get_client()

        api_params = {'restApiId': kwargs.get('rest_api_id')}
        if kwargs.get('limit'):
            api_kwargs['limit'] = kwargs.get('limit')
        if kwargs.get('position'):
            api_kwargs['position'] = kwargs.get('position')

        response = client.get_resources(**api_params)

        resources = []
        for resource in response.get('items', []):
            resources.append({
                'id': resource.get('id'),
                'path': resource.get('path'),
                'path_part': resource.get('pathPart'),
                'parent_id': resource.get('parentId'),
                'resource_methods': resource.get('resourceMethods', {})
            })

        return {
            'resources': resources,
            'total_count': len(resources),
            'position': response.get('position')
        }

    def _create_resource(self, **kwargs) -> Dict[str, Any]:
        """Crea un recurso en una API"""
        client = self._get_client()

        response = client.create_resource(
            restApiId=kwargs.get('rest_api_id'),
            parentId=kwargs.get('parent_id'),
            pathPart=kwargs.get('path_part')
        )

        return {
            'message': f'Recurso {kwargs.get("path_part")} creado en API {kwargs.get("rest_api_id")}',
            'resource_id': response.get('id'),
            'path': response.get('path')
        }

    def _delete_resource(self, **kwargs) -> Dict[str, Any]:
        """Elimina un recurso de una API"""
        client = self._get_client()

        client.delete_resource(
            restApiId=kwargs.get('rest_api_id'),
            resourceId=kwargs.get('resource_id')
        )

        return {
            'message': f'Recurso {kwargs.get("resource_id")} eliminado de API {kwargs.get("rest_api_id")}'
        }

    def _get_method(self, **kwargs) -> Dict[str, Any]:
        """Obtiene un método de un recurso"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'resourceId': kwargs.get('resource_id'),
            'httpMethod': kwargs.get('method')
        }
        if kwargs.get('position'):
            api_kwargs['position'] = kwargs.get('position')

        response = client.get_method(**api_params)

        return {
            'method': {
                'http_method': response.get('httpMethod'),
                'authorization_type': response.get('authorizationType'),
                'api_key_required': response.get('apiKeyRequired'),
                'request_parameters': response.get('requestParameters', {}),
                'request_models': response.get('requestModels', {}),
                'method_responses': response.get('methodResponses', {})
            }
        }

    def _put_method(self, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza un método en un recurso"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'resourceId': kwargs.get('resource_id'),
            'httpMethod': kwargs.get('method')
        }

        if kwargs.get('authorization_type'):
            api_kwargs['authorizationType'] = kwargs.get('authorization_type')
        if kwargs.get('api_key_required'):
            api_kwargs['apiKeyRequired'] = kwargs.get('api_key_required')
        if kwargs.get('operation_name'):
            api_kwargs['operationName'] = kwargs.get('operation_name')
        if kwargs.get('request_parameters'):
            api_kwargs['requestParameters'] = kwargs.get('request_parameters')
        if kwargs.get('request_models'):
            api_kwargs['requestModels'] = kwargs.get('request_models')

        response = client.put_method(**api_params)

        return {
            'message': f'Método {kwargs.get("method")} configurado en recurso {kwargs.get("resource_id")}',
            'method': response.get('httpMethod')
        }

    def _put_integration(self, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza una integración para un método"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'resourceId': kwargs.get('resource_id'),
            'httpMethod': kwargs.get('method'),
            'type': kwargs.get('type')
        }

        if kwargs.get('integration_method'):
            api_kwargs['integrationHttpMethod'] = kwargs.get('integration_method')
        if kwargs.get('uri'):
            api_kwargs['uri'] = kwargs.get('uri')
        if kwargs.get('credentials'):
            api_kwargs['credentials'] = kwargs.get('credentials')
        if kwargs.get('request_parameters'):
            api_kwargs['requestParameters'] = kwargs.get('request_parameters')
        if kwargs.get('request_templates'):
            api_kwargs['requestTemplates'] = kwargs.get('request_templates')
        if kwargs.get('passthrough_behavior'):
            api_kwargs['passthroughBehavior'] = kwargs.get('passthrough_behavior')
        if kwargs.get('content_handling'):
            api_kwargs['contentHandling'] = kwargs.get('content_handling')

        response = client.put_integration(**api_params)

        return {
            'message': f'Integración configurada para método {kwargs.get("method")} en recurso {kwargs.get("resource_id")}',
            'integration_type': response.get('type'),
            'uri': response.get('uri')
        }

    def _put_method_response(self, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza una respuesta de método"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'resourceId': kwargs.get('resource_id'),
            'httpMethod': kwargs.get('method'),
            'statusCode': kwargs.get('status_code')
        }

        if kwargs.get('response_parameters'):
            api_kwargs['responseParameters'] = kwargs.get('response_parameters')
        if kwargs.get('response_models'):
            api_kwargs['responseModels'] = kwargs.get('response_models')

        response = client.put_method_response(**api_params)

        return {
            'message': f'Respuesta de método {kwargs.get("status_code")} configurada',
            'status_code': response.get('statusCode')
        }

    def _put_integration_response(self, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza una respuesta de integración"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'resourceId': kwargs.get('resource_id'),
            'httpMethod': kwargs.get('method'),
            'statusCode': kwargs.get('status_code')
        }

        if kwargs.get('response_parameters'):
            api_kwargs['responseParameters'] = kwargs.get('response_parameters')
        if kwargs.get('response_templates'):
            api_kwargs['responseTemplates'] = kwargs.get('response_templates')
        if kwargs.get('content_handling'):
            api_kwargs['contentHandling'] = kwargs.get('content_handling')

        response = client.put_integration_response(**api_params)

        return {
            'message': f'Respuesta de integración {kwargs.get("status_code")} configurada',
            'status_code': response.get('statusCode')
        }

    def _create_deployment(self, **kwargs) -> Dict[str, Any]:
        """Crea un deployment de una API"""
        client = self._get_client()

        api_params = {
            'restApiId': kwargs.get('rest_api_id'),
            'stageName': kwargs.get('stage_name')
        }

        if kwargs.get('stage_description'):
            api_kwargs['stageDescription'] = kwargs.get('stage_description')
        if kwargs.get('description'):
            api_kwargs['description'] = kwargs.get('description')
        if kwargs.get('cache_cluster_enabled'):
            api_kwargs['cacheClusterEnabled'] = kwargs.get('cache_cluster_enabled')
        if kwargs.get('cache_cluster_size'):
            api_kwargs['cacheClusterSize'] = kwargs.get('cache_cluster_size')
        if kwargs.get('variables'):
            api_kwargs['variables'] = kwargs.get('variables')
        if kwargs.get('canary_settings'):
            api_kwargs['canarySettings'] = kwargs.get('canary_settings')

        response = client.create_deployment(**api_params)

        return {
            'message': f'Deployment creado para API {kwargs.get("rest_api_id")} en stage {kwargs.get("stage_name")}',
            'deployment_id': response.get('id'),
            'description': response.get('description')
        }

    def _get_stages(self, **kwargs) -> Dict[str, Any]:
        """Lista stages de una API"""
        client = self._get_client()

        api_params = {'restApiId': kwargs.get('rest_api_id')}
        if kwargs.get('deployment_id'):
            api_kwargs['deploymentId'] = kwargs.get('deployment_id')

        response = client.get_stages(**api_params)

        stages = []
        for stage in response.get('item', []):
            stages.append({
                'stage_name': stage.get('stageName'),
                'deployment_id': stage.get('deploymentId'),
                'description': stage.get('description'),
                'created_date': stage.get('createdDate'),
                'last_updated_date': stage.get('lastUpdatedDate'),
                'cache_cluster_enabled': stage.get('cacheClusterEnabled'),
                'cache_cluster_size': stage.get('cacheClusterSize'),
                'variables': stage.get('variables', {}),
                'method_settings': stage.get('methodSettings', {})
            })

        return {
            'stages': stages,
            'total_count': len(stages)
        }

    def _get_api_keys(self, **kwargs) -> Dict[str, Any]:
        """Lista API keys"""
        client = self._get_client()

        api_params = {}
        if kwargs.get('limit'):
            api_kwargs['limit'] = kwargs.get('limit')
        if kwargs.get('position'):
            api_kwargs['position'] = kwargs.get('position')
        if kwargs.get('name_query'):
            api_kwargs['nameQuery'] = kwargs.get('name_query')
        if kwargs.get('customer_id'):
            api_kwargs['customerId'] = kwargs.get('customer_id')

        response = client.get_api_keys(**api_params)

        api_keys = []
        for key in response.get('items', []):
            api_keys.append({
                'id': key.get('id'),
                'name': key.get('name'),
                'description': key.get('description'),
                'enabled': key.get('enabled'),
                'created_date': key.get('createdDate'),
                'last_updated_date': key.get('lastUpdatedDate'),
                'stage_keys': key.get('stageKeys', []),
                'customer_id': key.get('customerId'),
                'value': key.get('value')
            })

        return {
            'api_keys': api_keys,
            'total_count': len(api_keys),
            'position': response.get('position')
        }

    def _create_api_key(self, **kwargs) -> Dict[str, Any]:
        """Crea una API key"""
        client = self._get_client()

        api_params = {'name': kwargs.get('name')}

        if kwargs.get('description'):
            api_kwargs['description'] = kwargs.get('description')
        if kwargs.get('enabled'):
            api_kwargs['enabled'] = kwargs.get('enabled')
        if kwargs.get('generate_distinct_id'):
            api_kwargs['generateDistinctId'] = kwargs.get('generate_distinct_id')
        if kwargs.get('value'):
            api_kwargs['value'] = kwargs.get('value')
        if kwargs.get('stage_keys'):
            api_kwargs['stageKeys'] = kwargs.get('stage_keys')
        if kwargs.get('customer_id'):
            api_kwargs['customerId'] = kwargs.get('customer_id')
        if kwargs.get('tags'):
            api_kwargs['tags'] = kwargs.get('tags')

        response = client.create_api_key(**api_params)

        return {
            'message': f'API key {kwargs.get("name")} creada exitosamente',
            'api_key_id': response.get('id'),
            'api_key_value': response.get('value')
        }

    def _get_usage_plans(self, **kwargs) -> Dict[str, Any]:
        """Lista planes de uso"""
        client = self._get_client()

        api_params = {}
        if kwargs.get('limit'):
            api_kwargs['limit'] = kwargs.get('limit')
        if kwargs.get('position'):
            api_kwargs['position'] = kwargs.get('position')

        response = client.get_usage_plans(**api_params)

        usage_plans = []
        for plan in response.get('items', []):
            usage_plans.append({
                'id': plan.get('id'),
                'name': plan.get('name'),
                'description': plan.get('description'),
                'api_stages': plan.get('apiStages', []),
                'throttle': plan.get('throttle', {}),
                'quota': plan.get('quota', {})
            })

        return {
            'usage_plans': usage_plans,
            'total_count': len(usage_plans),
            'position': response.get('position')
        }

    def _create_usage_plan(self, **kwargs) -> Dict[str, Any]:
        """Crea un plan de uso"""
        client = self._get_client()

        api_params = {'name': kwargs.get('name')}

        if kwargs.get('description'):
            api_kwargs['description'] = kwargs.get('description')
        if kwargs.get('api_stages'):
            api_kwargs['apiStages'] = kwargs.get('api_stages')
        if kwargs.get('throttle'):
            api_kwargs['throttle'] = kwargs.get('throttle')
        if kwargs.get('quota'):
            api_kwargs['quota'] = kwargs.get('quota')

        response = client.create_usage_plan(**api_params)

        return {
            'message': f'Plan de uso {kwargs.get("name")} creado exitosamente',
            'usage_plan_id': response.get('id'),
            'usage_plan_name': response.get('name')
        }

    def _create_domain_name(self, **kwargs) -> Dict[str, Any]:
        """Crea un nombre de dominio personalizado"""
        client = self._get_client()

        api_params = {'domainName': kwargs.get('domain_name')}

        if kwargs.get('certificate_name'):
            api_kwargs['certificateName'] = kwargs.get('certificate_name')
        if kwargs.get('certificate_body'):
            api_kwargs['certificateBody'] = kwargs.get('certificate_body')
        if kwargs.get('certificate_private_key'):
            api_kwargs['certificatePrivateKey'] = kwargs.get('certificate_private_key')
        if kwargs.get('certificate_chain'):
            api_kwargs['certificateChain'] = kwargs.get('certificate_chain')
        if kwargs.get('certificate_arn'):
            api_kwargs['certificateArn'] = kwargs.get('certificate_arn')
        if kwargs.get('regional_certificate_name'):
            api_kwargs['regionalCertificateName'] = kwargs.get('regional_certificate_name')
        if kwargs.get('regional_certificate_arn'):
            api_kwargs['regionalCertificateArn'] = kwargs.get('regional_certificate_arn')
        if kwargs.get('endpoint_configuration'):
            api_kwargs['endpointConfiguration'] = kwargs.get('endpoint_configuration')
        if kwargs.get('tags'):
            api_kwargs['tags'] = kwargs.get('tags')
        if kwargs.get('security_policy'):
            api_kwargs['securityPolicy'] = kwargs.get('security_policy')

        response = client.create_domain_name(**api_params)

        return {
            'message': f'Dominio personalizado {kwargs.get("domain_name")} creado exitosamente',
            'domain_name': response.get('domainName'),
            'certificate_name': response.get('certificateName'),
            'certificate_arn': response.get('certificateArn'),
            'distribution_domain_name': response.get('distributionDomainName'),
            'regional_domain_name': response.get('regionalDomainName')
        }

    def _create_base_path_mapping(self, **kwargs) -> Dict[str, Any]:
        """Crea un mapeo de ruta base"""
        client = self._get_client()

        api_params = {
            'domainName': kwargs.get('domain_name'),
            'restApiId': kwargs.get('rest_api_id')
        }

        if kwargs.get('base_path'):
            api_kwargs['basePath'] = kwargs.get('base_path')
        if kwargs.get('stage'):
            api_kwargs['stage'] = kwargs.get('stage')

        response = client.create_base_path_mapping(**api_params)

        return {
            'message': f'Mapeo de ruta base creado para dominio {kwargs.get("domain_name")}',
            'base_path': response.get('basePath'),
            'rest_api_id': response.get('restApiId'),
            'stage': response.get('stage')
        }