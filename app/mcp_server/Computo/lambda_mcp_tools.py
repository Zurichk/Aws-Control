"""
MCP Tools para AWS Lambda
Herramientas para gestión de funciones serverless
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class LambdaMCPTools:
    """Herramientas MCP para operaciones con AWS Lambda"""

    # Constantes para descripciones
    DESC_FUNCTION_NAME = 'Nombre de la función Lambda'
    DESC_RUNTIME = 'Runtime de la función (python3.8, python3.9, python3.10, python3.11, nodejs14.x, nodejs16.x, nodejs18.x, etc.)'
    DESC_HANDLER = 'Handler de la función (ej: lambda_function.lambda_handler)'
    DESC_ROLE_ARN = 'ARN del rol IAM para la función'
    DESC_CODE = 'Código de la función (ZIP en base64 o bucket S3)'
    DESC_DESCRIPTION = 'Descripción de la función'
    DESC_TIMEOUT = 'Timeout en segundos (1-900)'
    DESC_MEMORY_SIZE = 'Tamaño de memoria en MB (128-3008)'
    DESC_ENVIRONMENT = 'Variables de entorno'
    DESC_MAX_ITEMS = 'Número máximo de elementos a retornar'

    def __init__(self):
        self.lambda_client = None

    def _get_client(self):
        """Obtiene el cliente Lambda"""
        if self.lambda_client is None:
            self.lambda_client = get_aws_client('lambda')
        return self.lambda_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para Lambda"""
        return [
            {
                'name': 'lambda_list_functions',
                'description': 'Lista funciones Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_version': {'type': 'string', 'description': 'Versión específica ($LATEST, etc.)', 'default': 'ALL'},
                        'marker': {'type': 'string', 'description': 'Marcador para paginación'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 50}
                    }
                }
            },
            {
                'name': 'lambda_get_function',
                'description': 'Obtiene detalles completos de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'qualifier': {'type': 'string', 'description': 'Calificador ($LATEST, versión, alias)'}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_create_function',
                'description': 'Crea una nueva función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'runtime': {'type': 'string', 'description': self.DESC_RUNTIME},
                        'role': {'type': 'string', 'description': self.DESC_ROLE_ARN},
                        'handler': {'type': 'string', 'description': self.DESC_HANDLER},
                        'code': {
                            'type': 'object',
                            'description': self.DESC_CODE,
                            'properties': {
                                'zip_file': {'type': 'string', 'description': 'Código ZIP en base64'},
                                's3_bucket': {'type': 'string', 'description': 'Bucket S3'},
                                's3_key': {'type': 'string', 'description': 'Key S3'},
                                's3_object_version': {'type': 'string', 'description': 'Versión del objeto S3'}
                            }
                        },
                        'description': {'type': 'string', 'description': self.DESC_DESCRIPTION},
                        'timeout': {'type': 'integer', 'description': self.DESC_TIMEOUT, 'default': 30},
                        'memory_size': {'type': 'integer', 'description': self.DESC_MEMORY_SIZE, 'default': 128},
                        'environment': {'type': 'object', 'description': self.DESC_ENVIRONMENT},
                        'vpc_config': {
                            'type': 'object',
                            'description': 'Configuración VPC',
                            'properties': {
                                'subnet_ids': {'type': 'array', 'items': {'type': 'string'}},
                                'security_group_ids': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        },
                        'tags': {'type': 'object', 'description': 'Tags para la función'}
                    },
                    'required': ['function_name', 'runtime', 'role', 'handler', 'code']
                }
            },
            {
                'name': 'lambda_update_function_code',
                'description': 'Actualiza el código de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'zip_file': {'type': 'string', 'description': 'Código ZIP en base64'},
                        's3_bucket': {'type': 'string', 'description': 'Bucket S3'},
                        's3_key': {'type': 'string', 'description': 'Key S3'},
                        's3_object_version': {'type': 'string', 'description': 'Versión del objeto S3'},
                        'architectures': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Arquitecturas (x86_64, arm64)'}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_update_function_configuration',
                'description': 'Actualiza la configuración de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'description': {'type': 'string', 'description': self.DESC_DESCRIPTION},
                        'role': {'type': 'string', 'description': self.DESC_ROLE_ARN},
                        'handler': {'type': 'string', 'description': self.DESC_HANDLER},
                        'timeout': {'type': 'integer', 'description': self.DESC_TIMEOUT},
                        'memory_size': {'type': 'integer', 'description': self.DESC_MEMORY_SIZE},
                        'environment': {'type': 'object', 'description': self.DESC_ENVIRONMENT},
                        'vpc_config': {
                            'type': 'object',
                            'description': 'Configuración VPC',
                            'properties': {
                                'subnet_ids': {'type': 'array', 'items': {'type': 'string'}},
                                'security_group_ids': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        }
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_invoke_function',
                'description': 'Invoca una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'invocation_type': {'type': 'string', 'description': 'Tipo de invocación', 'enum': ['RequestResponse', 'Event', 'DryRun'], 'default': 'RequestResponse'},
                        'payload': {'type': 'string', 'description': 'Payload JSON para la función'},
                        'qualifier': {'type': 'string', 'description': 'Calificador ($LATEST, versión, alias)'}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_delete_function',
                'description': 'Elimina una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'qualifier': {'type': 'string', 'description': 'Calificador ($LATEST, versión, alias)'}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_publish_version',
                'description': 'Publica una nueva versión de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'code_sha256': {'type': 'string', 'description': 'SHA256 del código'},
                        'description': {'type': 'string', 'description': self.DESC_DESCRIPTION}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_list_versions_by_function',
                'description': 'Lista versiones de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'marker': {'type': 'string', 'description': 'Marcador para paginación'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 50}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_create_alias',
                'description': 'Crea un alias para una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'name': {'type': 'string', 'description': 'Nombre del alias'},
                        'function_version': {'type': 'string', 'description': 'Versión de la función'},
                        'description': {'type': 'string', 'description': self.DESC_DESCRIPTION}
                    },
                    'required': ['function_name', 'name', 'function_version']
                }
            },
            {
                'name': 'lambda_list_aliases',
                'description': 'Lista aliases de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'function_version': {'type': 'string', 'description': 'Versión específica'},
                        'marker': {'type': 'string', 'description': 'Marcador para paginación'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 50}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_list_event_source_mappings',
                'description': 'Lista mapeos de fuentes de eventos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'event_source_arn': {'type': 'string', 'description': 'ARN de la fuente de eventos'},
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'marker': {'type': 'string', 'description': 'Marcador para paginación'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 50}
                    }
                }
            },
            {
                'name': 'lambda_create_event_source_mapping',
                'description': 'Crea un mapeo de fuente de eventos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'event_source_arn': {'type': 'string', 'description': 'ARN de la fuente de eventos'},
                        'enabled': {'type': 'boolean', 'description': 'Habilitar el mapeo', 'default': True},
                        'batch_size': {'type': 'integer', 'description': 'Tamaño del batch', 'default': 100},
                        'starting_position': {'type': 'string', 'description': 'Posición inicial', 'enum': ['TRIM_HORIZON', 'LATEST', 'AT_TIMESTAMP']},
                        'starting_position_timestamp': {'type': 'number', 'description': 'Timestamp inicial (Unix)'}
                    },
                    'required': ['function_name', 'event_source_arn']
                }
            },
            {
                'name': 'lambda_delete_event_source_mapping',
                'description': 'Elimina un mapeo de fuente de eventos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'uuid': {'type': 'string', 'description': 'UUID del mapeo de fuente de eventos'}
                    },
                    'required': ['uuid']
                }
            },
            {
                'name': 'lambda_get_function_configuration',
                'description': 'Obtiene la configuración de una función Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'function_name': {'type': 'string', 'description': self.DESC_FUNCTION_NAME},
                        'qualifier': {'type': 'string', 'description': 'Calificador ($LATEST, versión, alias)'}
                    },
                    'required': ['function_name']
                }
            },
            {
                'name': 'lambda_list_layers',
                'description': 'Lista capas Lambda disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'compatible_runtime': {'type': 'string', 'description': self.DESC_RUNTIME},
                        'marker': {'type': 'string', 'description': 'Marcador para paginación'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 50}
                    }
                }
            },
            {
                'name': 'lambda_publish_layer_version',
                'description': 'Publica una nueva versión de una capa Lambda',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'layer_name': {'type': 'string', 'description': 'Nombre de la capa'},
                        'content': {
                            'type': 'object',
                            'description': 'Contenido de la capa',
                            'properties': {
                                'zip_file': {'type': 'string', 'description': 'Código ZIP en base64'},
                                's3_bucket': {'type': 'string', 'description': 'Bucket S3'},
                                's3_key': {'type': 'string', 'description': 'Key S3'}
                            }
                        },
                        'compatible_runtimes': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Runtimes compatibles'},
                        'description': {'type': 'string', 'description': self.DESC_DESCRIPTION}
                    },
                    'required': ['layer_name', 'content']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de Lambda"""
        try:
            if tool_name == 'lambda_list_functions':
                return self._list_functions(**parameters)
            elif tool_name == 'lambda_get_function':
                return self._get_function(**parameters)
            elif tool_name == 'lambda_create_function':
                return self._create_function(**parameters)
            elif tool_name == 'lambda_update_function_code':
                return self._update_function_code(**parameters)
            elif tool_name == 'lambda_update_function_configuration':
                return self._update_function_configuration(**parameters)
            elif tool_name == 'lambda_invoke_function':
                return self._invoke_function(**parameters)
            elif tool_name == 'lambda_delete_function':
                return self._delete_function(**parameters)
            elif tool_name == 'lambda_publish_version':
                return self._publish_version(**parameters)
            elif tool_name == 'lambda_list_versions_by_function':
                return self._list_versions_by_function(**parameters)
            elif tool_name == 'lambda_create_alias':
                return self._create_alias(**parameters)
            elif tool_name == 'lambda_list_aliases':
                return self._list_aliases(**parameters)
            elif tool_name == 'lambda_list_event_source_mappings':
                return self._list_event_source_mappings(**parameters)
            elif tool_name == 'lambda_create_event_source_mapping':
                return self._create_event_source_mapping(**parameters)
            elif tool_name == 'lambda_delete_event_source_mapping':
                return self._delete_event_source_mapping(**parameters)
            elif tool_name == 'lambda_get_function_configuration':
                return self._get_function_configuration(**parameters)
            elif tool_name == 'lambda_list_layers':
                return self._list_layers(**parameters)
            elif tool_name == 'lambda_publish_layer_version':
                return self._publish_layer_version(**parameters)
            else:
                return {'error': f'Herramienta Lambda no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta Lambda {tool_name}: {str(e)}'}

    def _list_functions(self, **kwargs) -> Dict[str, Any]:
        """Lista funciones Lambda"""
        client = self._get_client()

        lambda_params = {}
        if kwargs.get('function_version'):
            lambda_kwargs['FunctionVersion'] = kwargs.get('function_version')
        if kwargs.get('marker'):
            lambda_kwargs['Marker'] = kwargs.get('marker')
        if kwargs.get('max_items'):
            lambda_kwargs['MaxItems'] = kwargs.get('max_items')

        response = client.list_functions(**lambda_params)

        functions = []
        for func in response['Functions']:
            functions.append({
                'function_name': func['FunctionName'],
                'function_arn': func['FunctionArn'],
                'runtime': func.get('Runtime'),
                'role': func.get('Role'),
                'handler': func.get('Handler'),
                'code_size': func.get('CodeSize'),
                'code_sha256': func.get('CodeSha256'),
                'description': func.get('Description'),
                'timeout': func.get('Timeout'),
                'memory_size': func.get('MemorySize'),
                'last_modified': func.get('LastModified'),
                'version': func.get('Version'),
                'environment': func.get('Environment', {}).get('Variables', {}),
                'vpc_config': func.get('VpcConfig'),
                'state': func.get('State'),
                'state_reason': func.get('StateReason'),
                'state_reason_code': func.get('StateReasonCode')
            })

        return {
            'functions': functions,
            'total_count': len(functions),
            'next_marker': response.get('NextMarker')
        }

    def _get_function(self, **kwargs) -> Dict[str, Any]:
        """Obtiene detalles completos de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}
        if kwargs.get('qualifier'):
            lambda_kwargs['Qualifier'] = kwargs.get('qualifier')

        response = client.get_function(**lambda_params)

        func = response['Configuration']
        code = response.get('Code', {})

        return {
            'function': {
                'function_name': func['FunctionName'],
                'function_arn': func['FunctionArn'],
                'runtime': func.get('Runtime'),
                'role': func.get('Role'),
                'handler': func.get('Handler'),
                'code_size': func.get('CodeSize'),
                'code_sha256': func.get('CodeSha256'),
                'description': func.get('Description'),
                'timeout': func.get('Timeout'),
                'memory_size': func.get('MemorySize'),
                'last_modified': func.get('LastModified'),
                'version': func.get('Version'),
                'environment': func.get('Environment', {}).get('Variables', {}),
                'vpc_config': func.get('VpcConfig'),
                'state': func.get('State'),
                'state_reason': func.get('StateReason'),
                'state_reason_code': func.get('StateReasonCode'),
                'architectures': func.get('Architectures', []),
                'package_type': func.get('PackageType'),
                'image_config_response': func.get('ImageConfigResponse'),
                'signing_profile_version_arn': func.get('SigningProfileVersionArn'),
                'signing_job_arn': func.get('SigningJobArn'),
                'code_repository_type': code.get('RepositoryType'),
                'code_location': code.get('Location'),
                'code_image_uri': code.get('ImageUri')
            }
        }

    def _create_function(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva función Lambda"""
        client = self._get_client()

        lambda_params = {
            'FunctionName': kwargs.get('function_name'),
            'Runtime': kwargs.get('runtime'),
            'Role': kwargs.get('role'),
            'Handler': kwargs.get('handler'),
            'Code': self._prepare_code(kwargs.get('code'))
        }

        if kwargs.get('description'):
            lambda_kwargs['Description'] = kwargs.get('description')
        if kwargs.get('timeout'):
            lambda_kwargs['Timeout'] = kwargs.get('timeout')
        if kwargs.get('memory_size'):
            lambda_kwargs['MemorySize'] = kwargs.get('memory_size')
        if kwargs.get('environment'):
            lambda_kwargs['Environment'] = {'Variables': kwargs.get('environment')}
        if kwargs.get('vpc_config'):
            lambda_kwargs['VpcConfig'] = {
                'SubnetIds': kwargs.get('vpc_config').get('subnet_ids', []),
                'SecurityGroupIds': kwargs.get('vpc_config').get('security_group_ids', [])
            }
        if kwargs.get('tags'):
            lambda_kwargs['Tags'] = kwargs.get('tags')

        response = client.create_function(**lambda_params)

        return {
            'message': f'Función Lambda {kwargs.get("function_name")} creada exitosamente',
            'function_name': kwargs.get('function_name'),
            'function_arn': response['FunctionArn'],
            'version': response['Version'],
            'code_sha256': response['CodeSha256']
        }

    def _prepare_code(self, code_params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara el código para la función Lambda"""
        if 'zip_file' in code_params:
            import base64
            return {'ZipFile': base64.b64decode(code_params['zip_file'])}
        elif 's3_bucket' in code_params and 's3_key' in code_params:
            s3_config = {
                'S3Bucket': code_params['s3_bucket'],
                'S3Key': code_params['s3_key']
            }
            if 's3_object_version' in code_params:
                s3_config['S3ObjectVersion'] = code_params['s3_object_version']
            return {'S3Bucket': s3_config['S3Bucket'], 'S3Key': s3_config['S3Key']}
        else:
            raise ValueError('Se debe proporcionar zip_file o configuración S3')

    def _update_function_code(self, **kwargs) -> Dict[str, Any]:
        """Actualiza el código de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}

        if kwargs.get('zip_file'):
            import base64
            lambda_kwargs['ZipFile'] = base64.b64decode(kwargs.get('zip_file'))
        elif kwargs.get('s3_bucket') and kwargs.get('s3_key'):
            lambda_kwargs['S3Bucket'] = kwargs.get('s3_bucket')
            lambda_kwargs['S3Key'] = kwargs.get('s3_key')
            if kwargs.get('s3_object_version'):
                lambda_kwargs['S3ObjectVersion'] = kwargs.get('s3_object_version')

        if kwargs.get('architectures'):
            lambda_kwargs['Architectures'] = kwargs.get('architectures')

        response = client.update_function_code(**lambda_params)

        return {
            'message': f'Código de función {kwargs.get("function_name")} actualizado',
            'function_name': kwargs.get('function_name'),
            'version': response['Version'],
            'code_sha256': response['CodeSha256'],
            'last_modified': response['LastModified']
        }

    def _update_function_configuration(self, **kwargs) -> Dict[str, Any]:
        """Actualiza la configuración de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}

        if kwargs.get('description'):
            lambda_kwargs['Description'] = kwargs.get('description')
        if kwargs.get('role'):
            lambda_kwargs['Role'] = kwargs.get('role')
        if kwargs.get('handler'):
            lambda_kwargs['Handler'] = kwargs.get('handler')
        if kwargs.get('timeout'):
            lambda_kwargs['Timeout'] = kwargs.get('timeout')
        if kwargs.get('memory_size'):
            lambda_kwargs['MemorySize'] = kwargs.get('memory_size')
        if kwargs.get('environment'):
            lambda_kwargs['Environment'] = {'Variables': kwargs.get('environment')}
        if kwargs.get('vpc_config'):
            lambda_kwargs['VpcConfig'] = {
                'SubnetIds': kwargs.get('vpc_config').get('subnet_ids', []),
                'SecurityGroupIds': kwargs.get('vpc_config').get('security_group_ids', [])
            }

        response = client.update_function_configuration(**lambda_params)

        return {
            'message': f'Configuración de función {kwargs.get("function_name")} actualizada',
            'function_name': kwargs.get('function_name'),
            'version': response['Version'],
            'last_modified': response['LastModified']
        }

    def _invoke_function(self, **kwargs) -> Dict[str, Any]:
        """Invoca una función Lambda"""
        client = self._get_client()

        lambda_params = {
            'FunctionName': kwargs.get('function_name'),
            'InvocationType': kwargs.get('invocation_type', 'RequestResponse')
        }

        if kwargs.get('payload'):
            lambda_kwargs['Payload'] = kwargs.get('payload')
        if kwargs.get('qualifier'):
            lambda_kwargs['Qualifier'] = kwargs.get('qualifier')

        response = client.invoke(**lambda_params)

        result = {
            'function_name': kwargs.get('function_name'),
            'status_code': response['StatusCode'],
            'executed_version': response.get('ExecutedVersion'),
            'payload': response['Payload'].read().decode('utf-8') if response.get('Payload') else None
        }

        if 'LogResult' in response:
            import base64
            result['log_result'] = base64.b64decode(response['LogResult']).decode('utf-8')

        return result

    def _delete_function(self, **kwargs) -> Dict[str, Any]:
        """Elimina una función Lambda"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}
        if kwargs.get('qualifier'):
            lambda_kwargs['Qualifier'] = kwargs.get('qualifier')

        client.delete_function(**lambda_params)

        return {
            'message': f'Función Lambda {kwargs.get("function_name")} eliminada exitosamente',
            'function_name': kwargs.get('function_name')
        }

    def _publish_version(self, **kwargs) -> Dict[str, Any]:
        """Publica una nueva versión de función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}

        if kwargs.get('code_sha256'):
            lambda_kwargs['CodeSha256'] = kwargs.get('code_sha256')
        if kwargs.get('description'):
            lambda_kwargs['Description'] = kwargs.get('description')

        response = client.publish_version(**lambda_params)

        return {
            'message': f'Versión {response["Version"]} publicada para función {kwargs.get("function_name")}',
            'function_name': kwargs.get('function_name'),
            'version': response['Version'],
            'code_sha256': response['CodeSha256'],
            'description': response.get('Description')
        }

    def _list_versions_by_function(self, **kwargs) -> Dict[str, Any]:
        """Lista versiones de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}

        if kwargs.get('marker'):
            lambda_kwargs['Marker'] = kwargs.get('marker')
        if kwargs.get('max_items'):
            lambda_kwargs['MaxItems'] = kwargs.get('max_items')

        response = client.list_versions_by_function(**lambda_params)

        versions = []
        for version in response['Versions']:
            versions.append({
                'version': version['Version'],
                'code_sha256': version.get('CodeSha256'),
                'description': version.get('Description'),
                'last_modified': version.get('LastModified')
            })

        return {
            'function_name': kwargs.get('function_name'),
            'versions': versions,
            'total_count': len(versions),
            'next_marker': response.get('NextMarker')
        }

    def _create_alias(self, **kwargs) -> Dict[str, Any]:
        """Crea un alias para una función"""
        client = self._get_client()

        lambda_params = {
            'FunctionName': kwargs.get('function_name'),
            'Name': kwargs.get('name'),
            'FunctionVersion': kwargs.get('function_version')
        }

        if kwargs.get('description'):
            lambda_kwargs['Description'] = kwargs.get('description')

        response = client.create_alias(**lambda_params)

        return {
            'message': f'Alias {kwargs.get("name")} creado para función {kwargs.get("function_name")}',
            'function_name': kwargs.get('function_name'),
            'alias_name': kwargs.get('name'),
            'alias_arn': response['AliasArn'],
            'function_version': response['FunctionVersion']
        }

    def _list_aliases(self, **kwargs) -> Dict[str, Any]:
        """Lista aliases de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}

        if kwargs.get('function_version'):
            lambda_kwargs['FunctionVersion'] = kwargs.get('function_version')
        if kwargs.get('marker'):
            lambda_kwargs['Marker'] = kwargs.get('marker')
        if kwargs.get('max_items'):
            lambda_kwargs['MaxItems'] = kwargs.get('max_items')

        response = client.list_aliases(**lambda_params)

        aliases = []
        for alias in response['Aliases']:
            aliases.append({
                'name': alias['Name'],
                'alias_arn': alias['AliasArn'],
                'function_version': alias['FunctionVersion'],
                'description': alias.get('Description')
            })

        return {
            'function_name': kwargs.get('function_name'),
            'aliases': aliases,
            'total_count': len(aliases),
            'next_marker': response.get('NextMarker')
        }

    def _list_event_source_mappings(self, **kwargs) -> Dict[str, Any]:
        """Lista mapeos de fuentes de eventos"""
        client = self._get_client()

        lambda_params = {}
        if kwargs.get('event_source_arn'):
            lambda_kwargs['EventSourceArn'] = kwargs.get('event_source_arn')
        if kwargs.get('function_name'):
            lambda_kwargs['FunctionName'] = kwargs.get('function_name')
        if kwargs.get('marker'):
            lambda_kwargs['Marker'] = kwargs.get('marker')
        if kwargs.get('max_items'):
            lambda_kwargs['MaxItems'] = kwargs.get('max_items')

        response = client.list_event_source_mappings(**lambda_params)

        mappings = []
        for mapping in response['EventSourceMappings']:
            mappings.append({
                'uuid': mapping['UUID'],
                'function_arn': mapping.get('FunctionArn'),
                'event_source_arn': mapping.get('EventSourceArn'),
                'state': mapping.get('State'),
                'state_transition_reason': mapping.get('StateTransitionReason'),
                'last_modified': mapping.get('LastModified'),
                'last_processing_result': mapping.get('LastProcessingResult'),
                'batch_size': mapping.get('BatchSize'),
                'maximum_batching_window_in_seconds': mapping.get('MaximumBatchingWindowInSeconds')
            })

        return {
            'event_source_mappings': mappings,
            'total_count': len(mappings),
            'next_marker': response.get('NextMarker')
        }

    def _create_event_source_mapping(self, **kwargs) -> Dict[str, Any]:
        """Crea un mapeo de fuente de eventos"""
        client = self._get_client()

        lambda_params = {
            'FunctionName': kwargs.get('function_name'),
            'EventSourceArn': kwargs.get('event_source_arn')
        }

        if kwargs.get('enabled'):
            lambda_kwargs['Enabled'] = kwargs.get('enabled')
        if kwargs.get('batch_size'):
            lambda_kwargs['BatchSize'] = kwargs.get('batch_size')
        if kwargs.get('starting_position'):
            lambda_kwargs['StartingPosition'] = kwargs.get('starting_position')
        if kwargs.get('starting_position_timestamp'):
            lambda_kwargs['StartingPositionTimestamp'] = kwargs.get('starting_position_timestamp')

        response = client.create_event_source_mapping(**lambda_params)

        return {
            'message': f'Mapeo de fuente de eventos creado para función {kwargs.get("function_name")}',
            'uuid': response['UUID'],
            'function_arn': response['FunctionArn'],
            'event_source_arn': response['EventSourceArn'],
            'state': response['State']
        }

    def _delete_event_source_mapping(self, **kwargs) -> Dict[str, Any]:
        """Elimina un mapeo de fuente de eventos"""
        client = self._get_client()

        client.delete_event_source_mapping(UUID=kwargs.get('uuid'))

        return {
            'message': f'Mapeo de fuente de eventos {kwargs.get("uuid")} eliminado',
            'uuid': kwargs.get('uuid')
        }

    def _get_function_configuration(self, **kwargs) -> Dict[str, Any]:
        """Obtiene la configuración de una función"""
        client = self._get_client()

        lambda_params = {'FunctionName': kwargs.get('function_name')}
        if kwargs.get('qualifier'):
            lambda_kwargs['Qualifier'] = kwargs.get('qualifier')

        response = client.get_function_configuration(**lambda_params)

        return {
            'function_configuration': {
                'function_name': response['FunctionName'],
                'function_arn': response['FunctionArn'],
                'runtime': response.get('Runtime'),
                'role': response.get('Role'),
                'handler': response.get('Handler'),
                'code_size': response.get('CodeSize'),
                'code_sha256': response.get('CodeSha256'),
                'description': response.get('Description'),
                'timeout': response.get('Timeout'),
                'memory_size': response.get('MemorySize'),
                'last_modified': response.get('LastModified'),
                'version': response.get('Version'),
                'environment': response.get('Environment', {}).get('Variables', {}),
                'vpc_config': response.get('VpcConfig'),
                'state': response.get('State'),
                'state_reason': response.get('StateReason'),
                'state_reason_code': response.get('StateReasonCode'),
                'architectures': response.get('Architectures', []),
                'package_type': response.get('PackageType')
            }
        }

    def _list_layers(self, **kwargs) -> Dict[str, Any]:
        """Lista capas Lambda disponibles"""
        client = self._get_client()

        lambda_params = {}
        if kwargs.get('compatible_runtime'):
            lambda_kwargs['CompatibleRuntime'] = kwargs.get('compatible_runtime')
        if kwargs.get('marker'):
            lambda_kwargs['Marker'] = kwargs.get('marker')
        if kwargs.get('max_items'):
            lambda_kwargs['MaxItems'] = kwargs.get('max_items')

        response = client.list_layers(**lambda_params)

        layers = []
        for layer in response['Layers']:
            layer_versions = []
            for version in layer.get('LayerVersions', []):
                layer_versions.append({
                    'version': version.get('Version'),
                    'description': version.get('Description'),
                    'created_date': version.get('CreatedDate'),
                    'compatible_runtimes': version.get('CompatibleRuntimes', [])
                })

            layers.append({
                'layer_name': layer.get('LayerName'),
                'layer_arn': layer.get('LayerArn'),
                'latest_matching_version': layer.get('LatestMatchingVersion'),
                'layer_versions': layer_versions
            })

        return {
            'layers': layers,
            'total_count': len(layers),
            'next_marker': response.get('NextMarker')
        }

    def _publish_layer_version(self, **kwargs) -> Dict[str, Any]:
        """Publica una nueva versión de capa"""
        client = self._get_client()

        lambda_params = {
            'LayerName': kwargs.get('layer_name'),
            'Content': self._prepare_layer_content(kwargs.get('content'))
        }

        if kwargs.get('compatible_runtimes'):
            lambda_kwargs['CompatibleRuntimes'] = kwargs.get('compatible_runtimes')
        if kwargs.get('description'):
            lambda_kwargs['Description'] = kwargs.get('description')

        response = client.publish_layer_version(**lambda_params)

        return {
            'message': f'Versión de capa {kwargs.get("layer_name")} publicada',
            'layer_name': kwargs.get('layer_name'),
            'layer_arn': response['LayerArn'],
            'layer_version_arn': response['LayerVersionArn'],
            'version': response['Version'],
            'description': response.get('Description'),
            'compatible_runtimes': response.get('CompatibleRuntimes', [])
        }

    def _prepare_layer_content(self, content_params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara el contenido para la capa Lambda"""
        if 'zip_file' in content_params:
            import base64
            return {'ZipFile': base64.b64decode(content_params['zip_file'])}
        elif 's3_bucket' in content_params and 's3_key' in content_params:
            return {
                'S3Bucket': content_params['s3_bucket'],
                'S3Key': content_params['s3_key']
            }
        else:
            raise ValueError('Se debe proporcionar zip_file o configuración S3 para el contenido de la capa')