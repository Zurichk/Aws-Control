"""
MCP Tools para AWS DynamoDB
Herramientas para gestión de bases de datos NoSQL
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class DynamoDBMCPTools:
    """Herramientas MCP para operaciones con AWS DynamoDB"""

    # Constantes para descripciones
    DESC_TABLE_NAME = 'Nombre de la tabla DynamoDB'
    DESC_KEY_SCHEMA = 'Esquema de clave (hash_key, range_key opcional)'
    DESC_ATTRIBUTE_DEFINITIONS = 'Definiciones de atributos'
    DESC_BILLING_MODE = 'Modo de facturación (PROVISIONED, PAY_PER_REQUEST)'
    DESC_PROVISIONED_THROUGHPUT = 'Throughput provisionado (ReadCapacityUnits, WriteCapacityUnits)'
    DESC_STREAM_VIEW_TYPE = 'Tipo de vista del stream (NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES, KEYS_ONLY)'
    DESC_ITEM = 'Item de DynamoDB (objeto con atributos)'
    DESC_KEY = 'Clave del item (partition_key, sort_key opcional)'
    DESC_UPDATE_EXPRESSION = 'Expresión de actualización'
    DESC_CONDITION_EXPRESSION = 'Expresión de condición'
    DESC_FILTER_EXPRESSION = 'Expresión de filtro'
    DESC_PROJECTION_EXPRESSION = 'Expresión de proyección'
    DESC_MAX_ITEMS = 'Número máximo de elementos a retornar'
    DESC_INDEX_NAME = 'Nombre del índice'

    def __init__(self):
        self.dynamodb_client = None
        self.dynamodb_resource = None

    def _get_client(self):
        """Obtiene el cliente DynamoDB"""
        if self.dynamodb_client is None:
            self.dynamodb_client = get_aws_client('dynamodb')
        return self.dynamodb_client

    def _get_resource(self):
        """Obtiene el recurso DynamoDB"""
        if self.dynamodb_resource is None:
            self.dynamodb_resource = get_aws_client('dynamodb', use_resource=True)
        return self.dynamodb_resource

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para DynamoDB"""
        return [
            {
                'name': 'dynamodb_list_tables',
                'description': 'Lista tablas DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Límite de resultados', 'default': 100},
                        'exclusive_start_table_name': {'type': 'string', 'description': 'Nombre de tabla para continuar paginación'}
                    }
                }
            },
            {
                'name': 'dynamodb_describe_table',
                'description': 'Describe una tabla DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME}
                    },
                    'required': ['table_name']
                }
            },
            {
                'name': 'dynamodb_create_table',
                'description': 'Crea una nueva tabla DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'key_schema': {
                            'type': 'array',
                            'description': self.DESC_KEY_SCHEMA,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'attribute_name': {'type': 'string'},
                                    'key_type': {'type': 'string', 'enum': ['HASH', 'RANGE']}
                                },
                                'required': ['attribute_name', 'key_type']
                            }
                        },
                        'attribute_definitions': {
                            'type': 'array',
                            'description': self.DESC_ATTRIBUTE_DEFINITIONS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'attribute_name': {'type': 'string'},
                                    'attribute_type': {'type': 'string', 'enum': ['S', 'N', 'B']}
                                },
                                'required': ['attribute_name', 'attribute_type']
                            }
                        },
                        'billing_mode': {'type': 'string', 'description': self.DESC_BILLING_MODE, 'default': 'PAY_PER_REQUEST'},
                        'provisioned_throughput': {
                            'type': 'object',
                            'description': self.DESC_PROVISIONED_THROUGHPUT,
                            'properties': {
                                'read_capacity_units': {'type': 'integer'},
                                'write_capacity_units': {'type': 'integer'}
                            }
                        },
                        'stream_view_type': {'type': 'string', 'description': self.DESC_STREAM_VIEW_TYPE},
                        'tags': {'type': 'array', 'items': {'type': 'object'}, 'description': 'Tags para la tabla'}
                    },
                    'required': ['table_name', 'key_schema', 'attribute_definitions']
                }
            },
            {
                'name': 'dynamodb_delete_table',
                'description': 'Elimina una tabla DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME}
                    },
                    'required': ['table_name']
                }
            },
            {
                'name': 'dynamodb_put_item',
                'description': 'Inserta o reemplaza un item en DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'item': {'type': 'object', 'description': self.DESC_ITEM},
                        'condition_expression': {'type': 'string', 'description': self.DESC_CONDITION_EXPRESSION},
                        'return_values': {'type': 'string', 'description': 'Valores a retornar', 'enum': ['NONE', 'ALL_OLD', 'UPDATED_OLD', 'ALL_NEW', 'UPDATED_NEW']}
                    },
                    'required': ['table_name', 'item']
                }
            },
            {
                'name': 'dynamodb_get_item',
                'description': 'Obtiene un item de DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'key': {'type': 'object', 'description': self.DESC_KEY},
                        'projection_expression': {'type': 'string', 'description': self.DESC_PROJECTION_EXPRESSION},
                        'consistent_read': {'type': 'boolean', 'description': 'Lectura consistente', 'default': False}
                    },
                    'required': ['table_name', 'key']
                }
            },
            {
                'name': 'dynamodb_update_item',
                'description': 'Actualiza un item en DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'key': {'type': 'object', 'description': self.DESC_KEY},
                        'update_expression': {'type': 'string', 'description': self.DESC_UPDATE_EXPRESSION},
                        'condition_expression': {'type': 'string', 'description': self.DESC_CONDITION_EXPRESSION},
                        'return_values': {'type': 'string', 'description': 'Valores a retornar', 'enum': ['NONE', 'ALL_OLD', 'UPDATED_OLD', 'ALL_NEW', 'UPDATED_NEW']}
                    },
                    'required': ['table_name', 'key', 'update_expression']
                }
            },
            {
                'name': 'dynamodb_delete_item',
                'description': 'Elimina un item de DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'key': {'type': 'object', 'description': self.DESC_KEY},
                        'condition_expression': {'type': 'string', 'description': self.DESC_CONDITION_EXPRESSION},
                        'return_values': {'type': 'string', 'description': 'Valores a retornar', 'enum': ['NONE', 'ALL_OLD']}
                    },
                    'required': ['table_name', 'key']
                }
            },
            {
                'name': 'dynamodb_scan',
                'description': 'Escanea una tabla DynamoDB',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'filter_expression': {'type': 'string', 'description': self.DESC_FILTER_EXPRESSION},
                        'projection_expression': {'type': 'string', 'description': self.DESC_PROJECTION_EXPRESSION},
                        'limit': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100},
                        'exclusive_start_key': {'type': 'object', 'description': 'Clave exclusiva de inicio'},
                        'consistent_read': {'type': 'boolean', 'description': 'Lectura consistente', 'default': False}
                    },
                    'required': ['table_name']
                }
            },
            {
                'name': 'dynamodb_query',
                'description': 'Consulta una tabla DynamoDB usando la clave de partición',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'key_condition_expression': {'type': 'string', 'description': 'Expresión de condición de clave'},
                        'filter_expression': {'type': 'string', 'description': self.DESC_FILTER_EXPRESSION},
                        'projection_expression': {'type': 'string', 'description': self.DESC_PROJECTION_EXPRESSION},
                        'index_name': {'type': 'string', 'description': self.DESC_INDEX_NAME},
                        'limit': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100},
                        'exclusive_start_key': {'type': 'object', 'description': 'Clave exclusiva de inicio'},
                        'scan_index_forward': {'type': 'boolean', 'description': 'Orden ascendente', 'default': True},
                        'consistent_read': {'type': 'boolean', 'description': 'Lectura consistente', 'default': False}
                    },
                    'required': ['table_name', 'key_condition_expression']
                }
            },
            {
                'name': 'dynamodb_batch_write_item',
                'description': 'Escribe múltiples items en lote',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'request_items': {
                            'type': 'object',
                            'description': 'Items a escribir por tabla',
                            'additionalProperties': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'put_request': {'type': 'object', 'properties': {'item': {'type': 'object'}}},
                                        'delete_request': {'type': 'object', 'properties': {'key': {'type': 'object'}}}
                                    }
                                }
                            }
                        }
                    },
                    'required': ['request_items']
                }
            },
            {
                'name': 'dynamodb_batch_get_item',
                'description': 'Obtiene múltiples items en lote',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'request_items': {
                            'type': 'object',
                            'description': 'Claves a obtener por tabla',
                            'additionalProperties': {
                                'type': 'object',
                                'properties': {
                                    'keys': {'type': 'array', 'items': {'type': 'object'}},
                                    'projection_expression': {'type': 'string'}
                                },
                                'required': ['keys']
                            }
                        }
                    },
                    'required': ['request_items']
                }
            },
            {
                'name': 'dynamodb_update_table',
                'description': 'Actualiza la configuración de una tabla',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'billing_mode': {'type': 'string', 'description': self.DESC_BILLING_MODE},
                        'provisioned_throughput': {
                            'type': 'object',
                            'description': self.DESC_PROVISIONED_THROUGHPUT,
                            'properties': {
                                'read_capacity_units': {'type': 'integer'},
                                'write_capacity_units': {'type': 'integer'}
                            }
                        },
                        'stream_specification': {
                            'type': 'object',
                            'description': 'Especificación del stream',
                            'properties': {
                                'stream_enabled': {'type': 'boolean'},
                                'stream_view_type': {'type': 'string'}
                            }
                        }
                    },
                    'required': ['table_name']
                }
            },
            {
                'name': 'dynamodb_describe_continuous_backups',
                'description': 'Describe la configuración de backups continuos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME}
                    },
                    'required': ['table_name']
                }
            },
            {
                'name': 'dynamodb_update_continuous_backups',
                'description': 'Actualiza la configuración de backups continuos',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'point_in_time_recovery_specification': {
                            'type': 'object',
                            'properties': {
                                'point_in_time_recovery_enabled': {'type': 'boolean'}
                            },
                            'required': ['point_in_time_recovery_enabled']
                        }
                    },
                    'required': ['table_name', 'point_in_time_recovery_specification']
                }
            },
            {
                'name': 'dynamodb_list_backups',
                'description': 'Lista backups de una tabla',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'backup_type': {'type': 'string', 'description': 'Tipo de backup', 'enum': ['USER', 'SYSTEM', 'AWS_BACKUP', 'ALL']},
                        'limit': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100},
                        'exclusive_start_backup_arn': {'type': 'string', 'description': 'ARN de backup para paginación'}
                    }
                }
            },
            {
                'name': 'dynamodb_create_backup',
                'description': 'Crea un backup de una tabla',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'table_name': {'type': 'string', 'description': self.DESC_TABLE_NAME},
                        'backup_name': {'type': 'string', 'description': 'Nombre del backup'}
                    },
                    'required': ['table_name', 'backup_name']
                }
            },
            {
                'name': 'dynamodb_delete_backup',
                'description': 'Elimina un backup',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'backup_arn': {'type': 'string', 'description': 'ARN del backup'}
                    },
                    'required': ['backup_arn']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de DynamoDB"""
        try:
            if tool_name == 'dynamodb_list_tables':
                return self._list_tables(**parameters)
            elif tool_name == 'dynamodb_describe_table':
                return self._describe_table(**parameters)
            elif tool_name == 'dynamodb_create_table':
                return self._create_table(**parameters)
            elif tool_name == 'dynamodb_delete_table':
                return self._delete_table(**parameters)
            elif tool_name == 'dynamodb_put_item':
                return self._put_item(**parameters)
            elif tool_name == 'dynamodb_get_item':
                return self._get_item(**parameters)
            elif tool_name == 'dynamodb_update_item':
                return self._update_item(**parameters)
            elif tool_name == 'dynamodb_delete_item':
                return self._delete_item(**parameters)
            elif tool_name == 'dynamodb_scan':
                return self._scan(**parameters)
            elif tool_name == 'dynamodb_query':
                return self._query(**parameters)
            elif tool_name == 'dynamodb_batch_write_item':
                return self._batch_write_item(**parameters)
            elif tool_name == 'dynamodb_batch_get_item':
                return self._batch_get_item(**parameters)
            elif tool_name == 'dynamodb_update_table':
                return self._update_table(**parameters)
            elif tool_name == 'dynamodb_describe_continuous_backups':
                return self._describe_continuous_backups(**parameters)
            elif tool_name == 'dynamodb_update_continuous_backups':
                return self._update_continuous_backups(**parameters)
            elif tool_name == 'dynamodb_list_backups':
                return self._list_backups(**parameters)
            elif tool_name == 'dynamodb_create_backup':
                return self._create_backup(**parameters)
            elif tool_name == 'dynamodb_delete_backup':
                return self._delete_backup(**parameters)
            else:
                return {'error': f'Herramienta DynamoDB no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta DynamoDB {tool_name}: {str(e)}'}

    def _list_tables(self, **kwargs) -> Dict[str, Any]:
        """Lista tablas DynamoDB"""
        client = self._get_client()

        dynamo_params = {}
        if kwargs.get('limit'):
            dynamo_kwargs['Limit'] = kwargs.get('limit')
        if kwargs.get('exclusive_start_table_name'):
            dynamo_kwargs['ExclusiveStartTableName'] = kwargs.get('exclusive_start_table_name')

        response = client.list_tables(**dynamo_params)

        return {
            'table_names': response['TableNames'],
            'last_evaluated_table_name': response.get('LastEvaluatedTableName'),
            'total_count': len(response['TableNames'])
        }

    def _describe_table(self, **kwargs) -> Dict[str, Any]:
        """Describe una tabla"""
        client = self._get_client()

        response = client.describe_table(TableName=kwargs.get('table_name'))

        table = response['Table']
        return {
            'table': {
                'table_name': table['TableName'],
                'table_arn': table.get('TableArn'),
                'table_id': table.get('TableId'),
                'table_status': table.get('TableStatus'),
                'creation_date_time': table.get('CreationDateTime'),
                'key_schema': table.get('KeySchema', []),
                'attribute_definitions': table.get('AttributeDefinitions', []),
                'billing_mode_summary': table.get('BillingModeSummary'),
                'provisioned_throughput': table.get('ProvisionedThroughput'),
                'table_size_bytes': table.get('TableSizeBytes'),
                'item_count': table.get('ItemCount'),
                'table_class': table.get('TableClass'),
                'stream_specification': table.get('StreamSpecification'),
                'latest_stream_arn': table.get('LatestStreamArn'),
                'global_secondary_indexes': table.get('GlobalSecondaryIndexes', []),
                'local_secondary_indexes': table.get('LocalSecondaryIndexes', []),
                'replicas': table.get('Replicas', [])
            }
        }

    def _create_table(self, **kwargs) -> Dict[str, Any]:
        """Crea una nueva tabla"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'KeySchema': kwargs.get('key_schema'),
            'AttributeDefinitions': kwargs.get('attribute_definitions')
        }

        if kwargs.get('billing_mode'):
            dynamo_kwargs['BillingMode'] = kwargs.get('billing_mode')

        if kwargs.get('provisioned_throughput'):
            dynamo_kwargs['ProvisionedThroughput'] = {
                'ReadCapacityUnits': kwargs.get('provisioned_throughput')['read_capacity_units'],
                'WriteCapacityUnits': kwargs.get('provisioned_throughput')['write_capacity_units']
            }

        if kwargs.get('stream_view_type'):
            dynamo_kwargs['StreamSpecification'] = {
                'StreamEnabled': True,
                'StreamViewType': kwargs.get('stream_view_type')
            }

        if kwargs.get('tags'):
            dynamo_kwargs['Tags'] = kwargs.get('tags')

        response = client.create_table(**dynamo_params)

        return {
            'message': f'Tabla DynamoDB {kwargs.get("table_name")} creada exitosamente',
            'table_description': {
                'table_name': response['TableDescription']['TableName'],
                'table_arn': response['TableDescription'].get('TableArn'),
                'table_status': response['TableDescription'].get('TableStatus'),
                'key_schema': response['TableDescription'].get('KeySchema', []),
                'attribute_definitions': response['TableDescription'].get('AttributeDefinitions', [])
            }
        }

    def _delete_table(self, **kwargs) -> Dict[str, Any]:
        """Elimina una tabla"""
        client = self._get_client()

        response = client.delete_table(TableName=kwargs.get('table_name'))

        return {
            'message': f'Tabla DynamoDB {kwargs.get("table_name")} eliminada exitosamente',
            'table_description': {
                'table_name': response['TableDescription']['TableName'],
                'table_arn': response['TableDescription'].get('TableArn'),
                'table_status': response['TableDescription'].get('TableStatus')
            }
        }

    def _put_item(self, **kwargs) -> Dict[str, Any]:
        """Inserta o reemplaza un item"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'Item': kwargs.get('item')
        }

        if kwargs.get('condition_expression'):
            dynamo_kwargs['ConditionExpression'] = kwargs.get('condition_expression')
        if kwargs.get('return_values'):
            dynamo_kwargs['ReturnValues'] = kwargs.get('return_values')

        response = client.put_item(**dynamo_params)

        result = {
            'message': f'Item insertado en tabla {kwargs.get("table_name")}',
            'attributes': response.get('Attributes', {})
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _get_item(self, **kwargs) -> Dict[str, Any]:
        """Obtiene un item"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'Key': kwargs.get('key')
        }

        if kwargs.get('projection_expression'):
            dynamo_kwargs['ProjectionExpression'] = kwargs.get('projection_expression')
        if kwargs.get('consistent_read'):
            dynamo_kwargs['ConsistentRead'] = kwargs.get('consistent_read')

        response = client.get_item(**dynamo_params)

        result = {
            'item': response.get('Item', {}),
            'found': 'Item' in response
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _update_item(self, **kwargs) -> Dict[str, Any]:
        """Actualiza un item"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'Key': kwargs.get('key'),
            'UpdateExpression': kwargs.get('update_expression')
        }

        if kwargs.get('condition_expression'):
            dynamo_kwargs['ConditionExpression'] = kwargs.get('condition_expression')
        if kwargs.get('return_values'):
            dynamo_kwargs['ReturnValues'] = kwargs.get('return_values')

        response = client.update_item(**dynamo_params)

        result = {
            'message': f'Item actualizado en tabla {kwargs.get("table_name")}',
            'attributes': response.get('Attributes', {})
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _delete_item(self, **kwargs) -> Dict[str, Any]:
        """Elimina un item"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'Key': kwargs.get('key')
        }

        if kwargs.get('condition_expression'):
            dynamo_kwargs['ConditionExpression'] = kwargs.get('condition_expression')
        if kwargs.get('return_values'):
            dynamo_kwargs['ReturnValues'] = kwargs.get('return_values')

        response = client.delete_item(**dynamo_params)

        result = {
            'message': f'Item eliminado de tabla {kwargs.get("table_name")}',
            'attributes': response.get('Attributes', {})
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _scan(self, **kwargs) -> Dict[str, Any]:
        """Escanea una tabla"""
        client = self._get_client()

        dynamo_params = {'TableName': kwargs.get('table_name')}

        if kwargs.get('filter_expression'):
            dynamo_kwargs['FilterExpression'] = kwargs.get('filter_expression')
        if kwargs.get('projection_expression'):
            dynamo_kwargs['ProjectionExpression'] = kwargs.get('projection_expression')
        if kwargs.get('limit'):
            dynamo_kwargs['Limit'] = kwargs.get('limit')
        if kwargs.get('exclusive_start_key'):
            dynamo_kwargs['ExclusiveStartKey'] = kwargs.get('exclusive_start_key')
        if kwargs.get('consistent_read'):
            dynamo_kwargs['ConsistentRead'] = kwargs.get('consistent_read')

        response = client.scan(**dynamo_params)

        result = {
            'items': response.get('Items', []),
            'count': response.get('Count', 0),
            'scanned_count': response.get('ScannedCount', 0),
            'last_evaluated_key': response.get('LastEvaluatedKey')
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _query(self, **kwargs) -> Dict[str, Any]:
        """Consulta una tabla"""
        client = self._get_client()

        dynamo_params = {
            'TableName': kwargs.get('table_name'),
            'KeyConditionExpression': kwargs.get('key_condition_expression')
        }

        if kwargs.get('filter_expression'):
            dynamo_kwargs['FilterExpression'] = kwargs.get('filter_expression')
        if kwargs.get('projection_expression'):
            dynamo_kwargs['ProjectionExpression'] = kwargs.get('projection_expression')
        if kwargs.get('index_name'):
            dynamo_kwargs['IndexName'] = kwargs.get('index_name')
        if kwargs.get('limit'):
            dynamo_kwargs['Limit'] = kwargs.get('limit')
        if kwargs.get('exclusive_start_key'):
            dynamo_kwargs['ExclusiveStartKey'] = kwargs.get('exclusive_start_key')
        if kwargs.get('scan_index_forward'):
            dynamo_kwargs['ScanIndexForward'] = kwargs.get('scan_index_forward')
        if kwargs.get('consistent_read'):
            dynamo_kwargs['ConsistentRead'] = kwargs.get('consistent_read')

        response = client.query(**dynamo_params)

        result = {
            'items': response.get('Items', []),
            'count': response.get('Count', 0),
            'scanned_count': response.get('ScannedCount', 0),
            'last_evaluated_key': response.get('LastEvaluatedKey')
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _batch_write_item(self, **kwargs) -> Dict[str, Any]:
        """Escribe múltiples items en lote"""
        client = self._get_client()

        response = client.batch_write_item(RequestItems=kwargs.get('request_items'))

        result = {
            'message': 'Items escritos en lote exitosamente',
            'unprocessed_items': response.get('UnprocessedItems', {})
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _batch_get_item(self, **kwargs) -> Dict[str, Any]:
        """Obtiene múltiples items en lote"""
        client = self._get_client()

        response = client.batch_get_item(RequestItems=kwargs.get('request_items'))

        result = {
            'responses': response.get('Responses', {}),
            'unprocessed_keys': response.get('UnprocessedKeys', {})
        }

        if 'ConsumedCapacity' in response:
            result['consumed_capacity'] = response['ConsumedCapacity']

        return result

    def _update_table(self, **kwargs) -> Dict[str, Any]:
        """Actualiza la configuración de una tabla"""
        client = self._get_client()

        dynamo_params = {'TableName': kwargs.get('table_name')}

        if kwargs.get('billing_mode'):
            dynamo_kwargs['BillingMode'] = kwargs.get('billing_mode')

        if kwargs.get('provisioned_throughput'):
            dynamo_kwargs['ProvisionedThroughput'] = {
                'ReadCapacityUnits': kwargs.get('provisioned_throughput')['read_capacity_units'],
                'WriteCapacityUnits': kwargs.get('provisioned_throughput')['write_capacity_units']
            }

        if kwargs.get('stream_specification'):
            dynamo_kwargs['StreamSpecification'] = kwargs.get('stream_specification')

        response = client.update_table(**dynamo_params)

        return {
            'message': f'Tabla {kwargs.get("table_name")} actualizada exitosamente',
            'table_description': {
                'table_name': response['TableDescription']['TableName'],
                'table_arn': response['TableDescription'].get('TableArn'),
                'table_status': response['TableDescription'].get('TableStatus')
            }
        }

    def _describe_continuous_backups(self, **kwargs) -> Dict[str, Any]:
        """Describe backups continuos"""
        client = self._get_client()

        response = client.describe_continuous_backups(TableName=kwargs.get('table_name'))

        return {
            'continuous_backups_description': response.get('ContinuousBackupsDescription', {})
        }

    def _update_continuous_backups(self, **kwargs) -> Dict[str, Any]:
        """Actualiza backups continuos"""
        client = self._get_client()

        response = client.update_continuous_backups(
            TableName=kwargs.get('table_name'),
            PointInTimeRecoverySpecification=kwargs.get('point_in_time_recovery_specification')
        )

        return {
            'message': f'Backups continuos actualizados para tabla {kwargs.get("table_name")}',
            'continuous_backups_description': response.get('ContinuousBackupsDescription', {})
        }

    def _list_backups(self, **kwargs) -> Dict[str, Any]:
        """Lista backups"""
        client = self._get_client()

        dynamo_params = {}
        if kwargs.get('table_name'):
            dynamo_kwargs['TableName'] = kwargs.get('table_name')
        if kwargs.get('backup_type'):
            dynamo_kwargs['BackupType'] = kwargs.get('backup_type')
        if kwargs.get('limit'):
            dynamo_kwargs['Limit'] = kwargs.get('limit')
        if kwargs.get('exclusive_start_backup_arn'):
            dynamo_kwargs['ExclusiveStartBackupArn'] = kwargs.get('exclusive_start_backup_arn')

        response = client.list_backups(**dynamo_params)

        backups = []
        for backup in response.get('BackupSummaries', []):
            backups.append({
                'backup_arn': backup.get('BackupArn'),
                'backup_name': backup.get('BackupName'),
                'backup_status': backup.get('BackupStatus'),
                'backup_type': backup.get('BackupType'),
                'backup_creation_date_time': backup.get('BackupCreationDateTime'),
                'backup_expiry_date_time': backup.get('BackupExpiryDateTime'),
                'table_name': backup.get('TableName'),
                'table_arn': backup.get('TableArn')
            })

        return {
            'backups': backups,
            'total_count': len(backups),
            'last_evaluated_backup_arn': response.get('LastEvaluatedBackupArn')
        }

    def _create_backup(self, **kwargs) -> Dict[str, Any]:
        """Crea un backup"""
        client = self._get_client()

        response = client.create_backup(
            TableName=kwargs.get('table_name'),
            BackupName=kwargs.get('backup_name')
        )

        return {
            'message': f'Backup {kwargs.get("backup_name")} creado para tabla {kwargs.get("table_name")}',
            'backup_details': {
                'backup_arn': response['BackupDetails'].get('BackupArn'),
                'backup_name': response['BackupDetails'].get('BackupName'),
                'backup_status': response['BackupDetails'].get('BackupStatus'),
                'backup_type': response['BackupDetails'].get('BackupType'),
                'backup_creation_date_time': response['BackupDetails'].get('BackupCreationDateTime'),
                'table_name': response['BackupDetails'].get('TableName'),
                'table_arn': response['BackupDetails'].get('TableArn')
            }
        }

    def _delete_backup(self, **kwargs) -> Dict[str, Any]:
        """Elimina un backup"""
        client = self._get_client()

        response = client.delete_backup(BackupArn=kwargs.get('backup_arn'))

        return {
            'message': f'Backup {kwargs.get("backup_arn")} eliminado exitosamente',
            'backup_arn': kwargs.get('backup_arn')
        }