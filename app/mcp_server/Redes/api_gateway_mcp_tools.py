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
                return self._get_rest_apis(parameters)
            elif tool_name == 'apigateway_get_rest_api':
                return self._get_rest_api(parameters)
            elif tool_name == 'apigateway_create_rest_api':
                return self._create_rest_api(parameters)
            elif tool_name == 'apigateway_delete_rest_api':
                return self._delete_rest_api(parameters)
            elif tool_name == 'apigateway_get_resources':
                return self._get_resources(parameters)
            elif tool_name == 'apigateway_create_resource':
                return self._create_resource(parameters)
            elif tool_name == 'apigateway_delete_resource':
                return self._delete_resource(parameters)
            elif tool_name == 'apigateway_get_method':
                return self._get_method(parameters)
            elif tool_name == 'apigateway_put_method':
                return self._put_method(parameters)
            elif tool_name == 'apigateway_put_integration':
                return self._put_integration(parameters)
            elif tool_name == 'apigateway_put_method_response':
                return self._put_method_response(parameters)
            elif tool_name == 'apigateway_put_integration_response':
                return self._put_integration_response(parameters)
            elif tool_name == 'apigateway_create_deployment':
                return self._create_deployment(parameters)
            elif tool_name == 'apigateway_get_stages':
                return self._get_stages(parameters)
            elif tool_name == 'apigateway_get_api_keys':
                return self._get_api_keys(parameters)
            elif tool_name == 'apigateway_create_api_key':
                return self._create_api_key(parameters)
            elif tool_name == 'apigateway_get_usage_plans':
                return self._get_usage_plans(parameters)
            elif tool_name == 'apigateway_create_usage_plan':
                return self._create_usage_plan(parameters)
            elif tool_name == 'apigateway_create_domain_name':
                return self._create_domain_name(parameters)
            elif tool_name == 'apigateway_create_base_path_mapping':
                return self._create_base_path_mapping(parameters)
            else:
                return {'error': f'Herramienta API Gateway no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta API Gateway {tool_name}: {str(e)}'}

    def _get_rest_apis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista APIs REST"""
        client = self._get_client()

        api_params = {}
        if 'limit' in params:
            api_params['limit'] = params['limit']
        if 'position' in params:
            api_params['position'] = params['position']

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

    def _get_rest_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene detalles de una API REST"""
        client = self._get_client()

        response = client.get_rest_api(restApiId=params['rest_api_id'])

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

    def _create_rest_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva API REST"""
        client = self._get_client()

        api_params = {
            'name': params['name']
        }

        if 'description' in params:
            api_params['description'] = params['description']
        if 'endpoint_configuration' in params:
            api_params['endpointConfiguration'] = params['endpoint_configuration']
        if 'api_key_source_type' in params:
            api_params['apiKeySourceType'] = params['api_key_source_type']
        if 'binary_media_types' in params:
            api_params['binaryMediaTypes'] = params['binary_media_types']

        response = client.create_rest_api(**api_params)

        return {
            'message': f'API REST {params["name"]} creada exitosamente',
            'api_id': response.get('id'),
            'api_name': response.get('name')
        }

    def _delete_rest_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una API REST"""
        client = self._get_client()

        client.delete_rest_api(restApiId=params['rest_api_id'])

        return {
            'message': f'API REST {params["rest_api_id"]} eliminada exitosamente'
        }

    def _get_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista recursos de una API"""
        client = self._get_client()

        api_params = {'restApiId': params['rest_api_id']}
        if 'limit' in params:
            api_params['limit'] = params['limit']
        if 'position' in params:
            api_params['position'] = params['position']

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

    def _create_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un recurso en una API"""
        client = self._get_client()

        response = client.create_resource(
            restApiId=params['rest_api_id'],
            parentId=params['parent_id'],
            pathPart=params['path_part']
        )

        return {
            'message': f'Recurso {params["path_part"]} creado en API {params["rest_api_id"]}',
            'resource_id': response.get('id'),
            'path': response.get('path')
        }

    def _delete_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un recurso de una API"""
        client = self._get_client()

        client.delete_resource(
            restApiId=params['rest_api_id'],
            resourceId=params['resource_id']
        )

        return {
            'message': f'Recurso {params["resource_id"]} eliminado de API {params["rest_api_id"]}'
        }

    def _get_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene un método de un recurso"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'resourceId': params['resource_id'],
            'httpMethod': params['method']
        }
        if 'position' in params:
            api_params['position'] = params['position']

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

    def _put_method(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza un método en un recurso"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'resourceId': params['resource_id'],
            'httpMethod': params['method']
        }

        if 'authorization_type' in params:
            api_params['authorizationType'] = params['authorization_type']
        if 'api_key_required' in params:
            api_params['apiKeyRequired'] = params['api_key_required']
        if 'operation_name' in params:
            api_params['operationName'] = params['operation_name']
        if 'request_parameters' in params:
            api_params['requestParameters'] = params['request_parameters']
        if 'request_models' in params:
            api_params['requestModels'] = params['request_models']

        response = client.put_method(**api_params)

        return {
            'message': f'Método {params["method"]} configurado en recurso {params["resource_id"]}',
            'method': response.get('httpMethod')
        }

    def _put_integration(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza una integración para un método"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'resourceId': params['resource_id'],
            'httpMethod': params['method'],
            'type': params['type']
        }

        if 'integration_method' in params:
            api_params['integrationHttpMethod'] = params['integration_method']
        if 'uri' in params:
            api_params['uri'] = params['uri']
        if 'credentials' in params:
            api_params['credentials'] = params['credentials']
        if 'request_parameters' in params:
            api_params['requestParameters'] = params['request_parameters']
        if 'request_templates' in params:
            api_params['requestTemplates'] = params['request_templates']
        if 'passthrough_behavior' in params:
            api_params['passthroughBehavior'] = params['passthrough_behavior']
        if 'content_handling' in params:
            api_params['contentHandling'] = params['content_handling']

        response = client.put_integration(**api_params)

        return {
            'message': f'Integración configurada para método {params["method"]} en recurso {params["resource_id"]}',
            'integration_type': response.get('type'),
            'uri': response.get('uri')
        }

    def _put_method_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza una respuesta de método"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'resourceId': params['resource_id'],
            'httpMethod': params['method'],
            'statusCode': params['status_code']
        }

        if 'response_parameters' in params:
            api_params['responseParameters'] = params['response_parameters']
        if 'response_models' in params:
            api_params['responseModels'] = params['response_models']

        response = client.put_method_response(**api_params)

        return {
            'message': f'Respuesta de método {params["status_code"]} configurada',
            'status_code': response.get('statusCode')
        }

    def _put_integration_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza una respuesta de integración"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'resourceId': params['resource_id'],
            'httpMethod': params['method'],
            'statusCode': params['status_code']
        }

        if 'response_parameters' in params:
            api_params['responseParameters'] = params['response_parameters']
        if 'response_templates' in params:
            api_params['responseTemplates'] = params['response_templates']
        if 'content_handling' in params:
            api_params['contentHandling'] = params['content_handling']

        response = client.put_integration_response(**api_params)

        return {
            'message': f'Respuesta de integración {params["status_code"]} configurada',
            'status_code': response.get('statusCode')
        }

    def _create_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un deployment de una API"""
        client = self._get_client()

        api_params = {
            'restApiId': params['rest_api_id'],
            'stageName': params['stage_name']
        }

        if 'stage_description' in params:
            api_params['stageDescription'] = params['stage_description']
        if 'description' in params:
            api_params['description'] = params['description']
        if 'cache_cluster_enabled' in params:
            api_params['cacheClusterEnabled'] = params['cache_cluster_enabled']
        if 'cache_cluster_size' in params:
            api_params['cacheClusterSize'] = params['cache_cluster_size']
        if 'variables' in params:
            api_params['variables'] = params['variables']
        if 'canary_settings' in params:
            api_params['canarySettings'] = params['canary_settings']

        response = client.create_deployment(**api_params)

        return {
            'message': f'Deployment creado para API {params["rest_api_id"]} en stage {params["stage_name"]}',
            'deployment_id': response.get('id'),
            'description': response.get('description')
        }

    def _get_stages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista stages de una API"""
        client = self._get_client()

        api_params = {'restApiId': params['rest_api_id']}
        if 'deployment_id' in params:
            api_params['deploymentId'] = params['deployment_id']

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

    def _get_api_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista API keys"""
        client = self._get_client()

        api_params = {}
        if 'limit' in params:
            api_params['limit'] = params['limit']
        if 'position' in params:
            api_params['position'] = params['position']
        if 'name_query' in params:
            api_params['nameQuery'] = params['name_query']
        if 'customer_id' in params:
            api_params['customerId'] = params['customer_id']

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

    def _create_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una API key"""
        client = self._get_client()

        api_params = {'name': params['name']}

        if 'description' in params:
            api_params['description'] = params['description']
        if 'enabled' in params:
            api_params['enabled'] = params['enabled']
        if 'generate_distinct_id' in params:
            api_params['generateDistinctId'] = params['generate_distinct_id']
        if 'value' in params:
            api_params['value'] = params['value']
        if 'stage_keys' in params:
            api_params['stageKeys'] = params['stage_keys']
        if 'customer_id' in params:
            api_params['customerId'] = params['customer_id']
        if 'tags' in params:
            api_params['tags'] = params['tags']

        response = client.create_api_key(**api_params)

        return {
            'message': f'API key {params["name"]} creada exitosamente',
            'api_key_id': response.get('id'),
            'api_key_value': response.get('value')
        }

    def _get_usage_plans(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista planes de uso"""
        client = self._get_client()

        api_params = {}
        if 'limit' in params:
            api_params['limit'] = params['limit']
        if 'position' in params:
            api_params['position'] = params['position']

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

    def _create_usage_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un plan de uso"""
        client = self._get_client()

        api_params = {'name': params['name']}

        if 'description' in params:
            api_params['description'] = params['description']
        if 'api_stages' in params:
            api_params['apiStages'] = params['api_stages']
        if 'throttle' in params:
            api_params['throttle'] = params['throttle']
        if 'quota' in params:
            api_params['quota'] = params['quota']

        response = client.create_usage_plan(**api_params)

        return {
            'message': f'Plan de uso {params["name"]} creado exitosamente',
            'usage_plan_id': response.get('id'),
            'usage_plan_name': response.get('name')
        }

    def _create_domain_name(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nombre de dominio personalizado"""
        client = self._get_client()

        api_params = {'domainName': params['domain_name']}

        if 'certificate_name' in params:
            api_params['certificateName'] = params['certificate_name']
        if 'certificate_body' in params:
            api_params['certificateBody'] = params['certificate_body']
        if 'certificate_private_key' in params:
            api_params['certificatePrivateKey'] = params['certificate_private_key']
        if 'certificate_chain' in params:
            api_params['certificateChain'] = params['certificate_chain']
        if 'certificate_arn' in params:
            api_params['certificateArn'] = params['certificate_arn']
        if 'regional_certificate_name' in params:
            api_params['regionalCertificateName'] = params['regional_certificate_name']
        if 'regional_certificate_arn' in params:
            api_params['regionalCertificateArn'] = params['regional_certificate_arn']
        if 'endpoint_configuration' in params:
            api_params['endpointConfiguration'] = params['endpoint_configuration']
        if 'tags' in params:
            api_params['tags'] = params['tags']
        if 'security_policy' in params:
            api_params['securityPolicy'] = params['security_policy']

        response = client.create_domain_name(**api_params)

        return {
            'message': f'Dominio personalizado {params["domain_name"]} creado exitosamente',
            'domain_name': response.get('domainName'),
            'certificate_name': response.get('certificateName'),
            'certificate_arn': response.get('certificateArn'),
            'distribution_domain_name': response.get('distributionDomainName'),
            'regional_domain_name': response.get('regionalDomainName')
        }

    def _create_base_path_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un mapeo de ruta base"""
        client = self._get_client()

        api_params = {
            'domainName': params['domain_name'],
            'restApiId': params['rest_api_id']
        }

        if 'base_path' in params:
            api_params['basePath'] = params['base_path']
        if 'stage' in params:
            api_params['stage'] = params['stage']

        response = client.create_base_path_mapping(**api_params)

        return {
            'message': f'Mapeo de ruta base creado para dominio {params["domain_name"]}',
            'base_path': response.get('basePath'),
            'rest_api_id': response.get('restApiId'),
            'stage': response.get('stage')
        }