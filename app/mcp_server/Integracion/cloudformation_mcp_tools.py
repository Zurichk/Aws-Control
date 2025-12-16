"""
MCP Tools para AWS CloudFormation
Herramientas para gestión de infraestructura como código
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class CloudFormationMCPTools:
    """Herramientas MCP para operaciones con AWS CloudFormation"""

    # Constantes para descripciones
    DESC_STACK_NAME = 'Nombre del stack CloudFormation'
    DESC_TEMPLATE_BODY = 'Cuerpo del template CloudFormation (JSON/YAML)'
    DESC_TEMPLATE_URL = 'URL del template CloudFormation'
    DESC_PARAMETERS = 'Parámetros del stack'
    DESC_CAPABILITIES = 'Capacidades requeridas (CAPABILITY_IAM, CAPABILITY_NAMED_IAM, CAPABILITY_AUTO_EXPAND)'
    DESC_TAGS = 'Tags para el stack'
    DESC_CHANGE_SET_NAME = 'Nombre del change set'
    DESC_STACK_POLICY_BODY = 'Política del stack (JSON)'
    DESC_NOTIFICATION_ARNS = 'ARNs de temas SNS para notificaciones'

    def __init__(self):
        self.cf_client = None

    def _get_client(self):
        """Obtiene el cliente CloudFormation"""
        if self.cf_client is None:
            self.cf_client = get_aws_client('cloudformation')
        return self.cf_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para CloudFormation"""
        return [
            {
                'name': 'cloudformation_list_stacks',
                'description': 'Lista stacks CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_status_filter': {
                            'type': 'array',
                            'description': 'Filtro de estados de stack',
                            'items': {
                                'type': 'string',
                                'enum': ['CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
                                        'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_IN_PROGRESS', 'DELETE_FAILED',
                                        'DELETE_COMPLETE', 'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
                                        'UPDATE_COMPLETE', 'UPDATE_FAILED', 'UPDATE_ROLLBACK_IN_PROGRESS',
                                        'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                                        'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS', 'IMPORT_IN_PROGRESS',
                                        'IMPORT_COMPLETE', 'IMPORT_ROLLBACK_IN_PROGRESS', 'IMPORT_ROLLBACK_FAILED',
                                        'IMPORT_ROLLBACK_COMPLETE']
                            }
                        },
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    }
                }
            },
            {
                'name': 'cloudformation_describe_stacks',
                'description': 'Describe uno o más stacks CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    }
                }
            },
            {
                'name': 'cloudformation_create_stack',
                'description': 'Crea un nuevo stack CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'template_body': {'type': 'string', 'description': self.DESC_TEMPLATE_BODY},
                        'template_url': {'type': 'string', 'description': self.DESC_TEMPLATE_URL},
                        'parameters': {
                            'type': 'array',
                            'description': self.DESC_PARAMETERS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'parameter_key': {'type': 'string'},
                                    'parameter_value': {'type': 'string'},
                                    'use_previous_value': {'type': 'boolean'},
                                    'resolved_value': {'type': 'string'}
                                },
                                'required': ['parameter_key']
                            }
                        },
                        'capabilities': {
                            'type': 'array',
                            'description': self.DESC_CAPABILITIES,
                            'items': {'type': 'string'}
                        },
                        'tags': {
                            'type': 'array',
                            'description': self.DESC_TAGS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'key': {'type': 'string'},
                                    'value': {'type': 'string'}
                                },
                                'required': ['key', 'value']
                            }
                        },
                        'notification_arns': {
                            'type': 'array',
                            'description': self.DESC_NOTIFICATION_ARNS,
                            'items': {'type': 'string'}
                        },
                        'timeout_in_minutes': {'type': 'integer', 'description': 'Timeout en minutos'},
                        'on_failure': {
                            'type': 'string',
                            'description': 'Acción en caso de fallo',
                            'enum': ['DO_NOTHING', 'ROLLBACK', 'DELETE']
                        }
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_update_stack',
                'description': 'Actualiza un stack CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'template_body': {'type': 'string', 'description': self.DESC_TEMPLATE_BODY},
                        'template_url': {'type': 'string', 'description': self.DESC_TEMPLATE_URL},
                        'parameters': {
                            'type': 'array',
                            'description': self.DESC_PARAMETERS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'parameter_key': {'type': 'string'},
                                    'parameter_value': {'type': 'string'},
                                    'use_previous_value': {'type': 'boolean'}
                                },
                                'required': ['parameter_key']
                            }
                        },
                        'capabilities': {
                            'type': 'array',
                            'description': self.DESC_CAPABILITIES,
                            'items': {'type': 'string'}
                        },
                        'tags': {
                            'type': 'array',
                            'description': self.DESC_TAGS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'key': {'type': 'string'},
                                    'value': {'type': 'string'}
                                },
                                'required': ['key', 'value']
                            }
                        },
                        'notification_arns': {
                            'type': 'array',
                            'description': self.DESC_NOTIFICATION_ARNS,
                            'items': {'type': 'string'}
                        }
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_delete_stack',
                'description': 'Elimina un stack CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'retain_resources': {
                            'type': 'array',
                            'description': 'Recursos a retener',
                            'items': {'type': 'string'}
                        },
                        'role_arn': {'type': 'string', 'description': 'ARN del rol IAM'},
                        'client_request_token': {'type': 'string', 'description': 'Token de solicitud del cliente'}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_create_change_set',
                'description': 'Crea un change set para un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'change_set_name': {'type': 'string', 'description': self.DESC_CHANGE_SET_NAME},
                        'template_body': {'type': 'string', 'description': self.DESC_TEMPLATE_BODY},
                        'template_url': {'type': 'string', 'description': self.DESC_TEMPLATE_URL},
                        'parameters': {
                            'type': 'array',
                            'description': self.DESC_PARAMETERS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'parameter_key': {'type': 'string'},
                                    'parameter_value': {'type': 'string'},
                                    'use_previous_value': {'type': 'boolean'}
                                },
                                'required': ['parameter_key']
                            }
                        },
                        'capabilities': {
                            'type': 'array',
                            'description': self.DESC_CAPABILITIES,
                            'items': {'type': 'string'}
                        },
                        'tags': {
                            'type': 'array',
                            'description': self.DESC_TAGS,
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'key': {'type': 'string'},
                                    'value': {'type': 'string'}
                                },
                                'required': ['key', 'value']
                            }
                        },
                        'change_set_type': {
                            'type': 'string',
                            'description': 'Tipo de change set',
                            'enum': ['CREATE', 'UPDATE'],
                            'default': 'UPDATE'
                        }
                    },
                    'required': ['stack_name', 'change_set_name']
                }
            },
            {
                'name': 'cloudformation_describe_change_set',
                'description': 'Describe un change set',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'change_set_name': {'type': 'string', 'description': self.DESC_CHANGE_SET_NAME}
                    },
                    'required': ['stack_name', 'change_set_name']
                }
            },
            {
                'name': 'cloudformation_execute_change_set',
                'description': 'Ejecuta un change set',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'change_set_name': {'type': 'string', 'description': self.DESC_CHANGE_SET_NAME},
                        'client_request_token': {'type': 'string', 'description': 'Token de solicitud del cliente'}
                    },
                    'required': ['stack_name', 'change_set_name']
                }
            },
            {
                'name': 'cloudformation_delete_change_set',
                'description': 'Elimina un change set',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'change_set_name': {'type': 'string', 'description': self.DESC_CHANGE_SET_NAME}
                    },
                    'required': ['stack_name', 'change_set_name']
                }
            },
            {
                'name': 'cloudformation_list_stack_resources',
                'description': 'Lista recursos de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_describe_stack_resources',
                'description': 'Describe recursos específicos de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'logical_resource_id': {'type': 'string', 'description': 'ID lógico del recurso'},
                        'physical_resource_id': {'type': 'string', 'description': 'ID físico del recurso'}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_get_template',
                'description': 'Obtiene el template de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'change_set_name': {'type': 'string', 'description': self.DESC_CHANGE_SET_NAME}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_validate_template',
                'description': 'Valida un template CloudFormation',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'template_body': {'type': 'string', 'description': self.DESC_TEMPLATE_BODY},
                        'template_url': {'type': 'string', 'description': self.DESC_TEMPLATE_URL}
                    }
                }
            },
            {
                'name': 'cloudformation_list_exports',
                'description': 'Lista exports de stacks',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    }
                }
            },
            {
                'name': 'cloudformation_list_imports',
                'description': 'Lista imports de un export',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'export_name': {'type': 'string', 'description': 'Nombre del export'},
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    },
                    'required': ['export_name']
                }
            },
            {
                'name': 'cloudformation_describe_stack_events',
                'description': 'Describe eventos de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'next_token': {'type': 'string', 'description': 'Token para paginación'}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_set_stack_policy',
                'description': 'Establece la política de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME},
                        'stack_policy_body': {'type': 'string', 'description': self.DESC_STACK_POLICY_BODY},
                        'stack_policy_url': {'type': 'string', 'description': 'URL de la política del stack'}
                    },
                    'required': ['stack_name']
                }
            },
            {
                'name': 'cloudformation_get_stack_policy',
                'description': 'Obtiene la política de un stack',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'stack_name': {'type': 'string', 'description': self.DESC_STACK_NAME}
                    },
                    'required': ['stack_name']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de CloudFormation"""
        try:
            if tool_name == 'cloudformation_list_stacks':
                return self._list_stacks(**parameters)
            elif tool_name == 'cloudformation_describe_stacks':
                return self._describe_stacks(**parameters)
            elif tool_name == 'cloudformation_create_stack':
                return self._create_stack(**parameters)
            elif tool_name == 'cloudformation_update_stack':
                return self._update_stack(**parameters)
            elif tool_name == 'cloudformation_delete_stack':
                return self._delete_stack(**parameters)
            elif tool_name == 'cloudformation_create_change_set':
                return self._create_change_set(**parameters)
            elif tool_name == 'cloudformation_describe_change_set':
                return self._describe_change_set(**parameters)
            elif tool_name == 'cloudformation_execute_change_set':
                return self._execute_change_set(**parameters)
            elif tool_name == 'cloudformation_delete_change_set':
                return self._delete_change_set(**parameters)
            elif tool_name == 'cloudformation_list_stack_resources':
                return self._list_stack_resources(**parameters)
            elif tool_name == 'cloudformation_describe_stack_resources':
                return self._describe_stack_resources(**parameters)
            elif tool_name == 'cloudformation_get_template':
                return self._get_template(**parameters)
            elif tool_name == 'cloudformation_validate_template':
                return self._validate_template(**parameters)
            elif tool_name == 'cloudformation_list_exports':
                return self._list_exports(**parameters)
            elif tool_name == 'cloudformation_list_imports':
                return self._list_imports(**parameters)
            elif tool_name == 'cloudformation_describe_stack_events':
                return self._describe_stack_events(**parameters)
            elif tool_name == 'cloudformation_set_stack_policy':
                return self._set_stack_policy(**parameters)
            elif tool_name == 'cloudformation_get_stack_policy':
                return self._get_stack_policy(**parameters)
            else:
                return {'error': f'Herramienta CloudFormation no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta CloudFormation {tool_name}: {str(e)}'}

    def _list_stacks(self, **kwargs) -> Dict[str, Any]:
        """Lista stacks CloudFormation"""
        client = self._get_client()

        cf_params = {}
        if kwargs.get('stack_status_filter'):
            cf_kwargs.get('StackStatusFilter') = kwargs.get('stack_status_filter')
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.list_stacks(**cf_params)

        stacks = []
        for stack in response.get('StackSummaries', []):
            stacks.append({
                'stack_name': stack.get('StackName'),
                'stack_id': stack.get('StackId'),
                'stack_status': stack.get('StackStatus'),
                'creation_time': stack.get('CreationTime'),
                'last_updated_time': stack.get('LastUpdatedTime'),
                'deletion_time': stack.get('DeletionTime'),
                'template_description': stack.get('TemplateDescription'),
                'stack_status_reason': stack.get('StackStatusReason'),
                'parent_id': stack.get('ParentId'),
                'root_id': stack.get('RootId'),
                'drift_information': stack.get('DriftInformation')
            })

        return {
            'stacks': stacks,
            'total_count': len(stacks),
            'next_token': response.get('NextToken')
        }

    def _describe_stacks(self, **kwargs) -> Dict[str, Any]:
        """Describe stacks CloudFormation"""
        client = self._get_client()

        cf_params = {}
        if kwargs.get('stack_name'):
            cf_kwargs.get('StackName') = kwargs.get('stack_name')
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.describe_stacks(**cf_params)

        stacks = []
        for stack in response.get('Stacks', []):
            stacks.append({
                'stack_name': stack.get('StackName'),
                'stack_id': stack.get('StackId'),
                'stack_status': stack.get('StackStatus'),
                'creation_time': stack.get('CreationTime'),
                'last_updated_time': stack.get('LastUpdatedTime'),
                'description': stack.get('Description'),
                'parameters': stack.get('Parameters', []),
                'outputs': stack.get('Outputs', []),
                'tags': stack.get('Tags', []),
                'capabilities': stack.get('Capabilities', []),
                'notification_arns': stack.get('NotificationARNs', []),
                'timeout_in_minutes': stack.get('TimeoutInMinutes'),
                'stack_status_reason': stack.get('StackStatusReason'),
                'disable_rollback': stack.get('DisableRollback'),
                'parent_id': stack.get('ParentId'),
                'root_id': stack.get('RootId'),
                'drift_information': stack.get('DriftInformation'),
                'retain_except_on_create': stack.get('RetainExceptOnCreate'),
                'enable_termination_protection': stack.get('EnableTerminationProtection')
            })

        return {
            'stacks': stacks,
            'total_count': len(stacks),
            'next_token': response.get('NextToken')
        }

    def _create_stack(self, **kwargs) -> Dict[str, Any]:
        """Crea un nuevo stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}

        if kwargs.get('template_body'):
            cf_kwargs.get('TemplateBody') = kwargs.get('template_body')
        if kwargs.get('template_url'):
            cf_kwargs.get('TemplateURL') = kwargs.get('template_url')
        if kwargs.get('parameters'):
            cf_kwargs.get('Parameters') = kwargs.get('parameters')
        if kwargs.get('capabilities'):
            cf_kwargs.get('Capabilities') = kwargs.get('capabilities')
        if kwargs.get('tags'):
            cf_kwargs.get('Tags') = kwargs.get('tags')
        if kwargs.get('notification_arns'):
            cf_kwargs.get('NotificationARNs') = kwargs.get('notification_arns')
        if kwargs.get('timeout_in_minutes'):
            cf_kwargs.get('TimeoutInMinutes') = kwargs.get('timeout_in_minutes')
        if kwargs.get('on_failure'):
            cf_kwargs.get('OnFailure') = kwargs.get('on_failure')

        response = client.create_stack(**cf_params)

        return {
            'message': f'Stack CloudFormation {kwargs.get('stack_name')} creado exitosamente',
            'stack_id': response.get('StackId')
        }

    def _update_stack(self, **kwargs) -> Dict[str, Any]:
        """Actualiza un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}

        if kwargs.get('template_body'):
            cf_kwargs.get('TemplateBody') = kwargs.get('template_body')
        if kwargs.get('template_url'):
            cf_kwargs.get('TemplateURL') = kwargs.get('template_url')
        if kwargs.get('parameters'):
            cf_kwargs.get('Parameters') = kwargs.get('parameters')
        if kwargs.get('capabilities'):
            cf_kwargs.get('Capabilities') = kwargs.get('capabilities')
        if kwargs.get('tags'):
            cf_kwargs.get('Tags') = kwargs.get('tags')
        if kwargs.get('notification_arns'):
            cf_kwargs.get('NotificationARNs') = kwargs.get('notification_arns')

        response = client.update_stack(**cf_params)

        return {
            'message': f'Stack CloudFormation {kwargs.get('stack_name')} actualizado exitosamente',
            'stack_id': response.get('StackId')
        }

    def _delete_stack(self, **kwargs) -> Dict[str, Any]:
        """Elimina un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}

        if kwargs.get('retain_resources'):
            cf_kwargs.get('RetainResources') = kwargs.get('retain_resources')
        if kwargs.get('role_arn'):
            cf_kwargs.get('RoleARN') = kwargs.get('role_arn')
        if kwargs.get('client_request_token'):
            cf_kwargs.get('ClientRequestToken') = kwargs.get('client_request_token')

        client.delete_stack(**cf_params)

        return {
            'message': f'Stack CloudFormation {kwargs.get('stack_name')} eliminado exitosamente'
        }

    def _create_change_set(self, **kwargs) -> Dict[str, Any]:
        """Crea un change set"""
        client = self._get_client()

        cf_params = {
            'StackName': kwargs.get('stack_name'),
            'ChangeSetName': kwargs.get('change_set_name')
        }

        if kwargs.get('template_body'):
            cf_kwargs.get('TemplateBody') = kwargs.get('template_body')
        if kwargs.get('template_url'):
            cf_kwargs.get('TemplateURL') = kwargs.get('template_url')
        if kwargs.get('parameters'):
            cf_kwargs.get('Parameters') = kwargs.get('parameters')
        if kwargs.get('capabilities'):
            cf_kwargs.get('Capabilities') = kwargs.get('capabilities')
        if kwargs.get('tags'):
            cf_kwargs.get('Tags') = kwargs.get('tags')
        if kwargs.get('change_set_type'):
            cf_kwargs.get('ChangeSetType') = kwargs.get('change_set_type')

        response = client.create_change_set(**cf_params)

        return {
            'message': f'Change set {kwargs.get('change_set_name')} creado para stack {kwargs.get('stack_name')}',
            'change_set_id': response.get('Id'),
            'stack_id': response.get('StackId')
        }

    def _describe_change_set(self, **kwargs) -> Dict[str, Any]:
        """Describe un change set"""
        client = self._get_client()

        response = client.describe_change_set(
            StackName=kwargs.get('stack_name'),
            ChangeSetName=kwargs.get('change_set_name')
        )

        changes = []
        for change in response.get('Changes', []):
            changes.append({
                'type': change.get('Type'),
                'resource_change': {
                    'action': change.get('ResourceChange', {}).get('Action'),
                    'logical_resource_id': change.get('ResourceChange', {}).get('LogicalResourceId'),
                    'physical_resource_id': change.get('ResourceChange', {}).get('PhysicalResourceId'),
                    'resource_type': change.get('ResourceChange', {}).get('ResourceType'),
                    'replacement': change.get('ResourceChange', {}).get('Replacement'),
                    'scope': change.get('ResourceChange', {}).get('Scope', []),
                    'details': change.get('ResourceChange', {}).get('Details', [])
                }
            })

        return {
            'change_set_name': response.get('ChangeSetName'),
            'stack_name': response.get('StackName'),
            'status': response.get('Status'),
            'status_reason': response.get('StatusReason'),
            'description': response.get('Description'),
            'parameters': response.get('Parameters', []),
            'creation_time': response.get('CreationTime'),
            'execution_status': response.get('ExecutionStatus'),
            'changes': changes,
            'next_token': response.get('NextToken')
        }

    def _execute_change_set(self, **kwargs) -> Dict[str, Any]:
        """Ejecuta un change set"""
        client = self._get_client()

        cf_params = {
            'StackName': kwargs.get('stack_name'),
            'ChangeSetName': kwargs.get('change_set_name')
        }

        if kwargs.get('client_request_token'):
            cf_kwargs.get('ClientRequestToken') = kwargs.get('client_request_token')

        client.execute_change_set(**cf_params)

        return {
            'message': f'Change set {kwargs.get('change_set_name')} ejecutado para stack {kwargs.get('stack_name')}'
        }

    def _delete_change_set(self, **kwargs) -> Dict[str, Any]:
        """Elimina un change set"""
        client = self._get_client()

        client.delete_change_set(
            StackName=kwargs.get('stack_name'),
            ChangeSetName=kwargs.get('change_set_name')
        )

        return {
            'message': f'Change set {kwargs.get('change_set_name')} eliminado del stack {kwargs.get('stack_name')}'
        }

    def _list_stack_resources(self, **kwargs) -> Dict[str, Any]:
        """Lista recursos de un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.list_stack_resources(**cf_params)

        resources = []
        for resource in response.get('StackResourceSummaries', []):
            resources.append({
                'logical_resource_id': resource.get('LogicalResourceId'),
                'physical_resource_id': resource.get('PhysicalResourceId'),
                'resource_type': resource.get('ResourceType'),
                'last_updated_timestamp': resource.get('LastUpdatedTimestamp'),
                'resource_status': resource.get('ResourceStatus'),
                'resource_status_reason': resource.get('ResourceStatusReason'),
                'description': resource.get('Description'),
                'drift_information': resource.get('DriftInformation')
            })

        return {
            'stack_name': kwargs.get('stack_name'),
            'resources': resources,
            'total_count': len(resources),
            'next_token': response.get('NextToken')
        }

    def _describe_stack_resources(self, **kwargs) -> Dict[str, Any]:
        """Describe recursos específicos de un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}

        if kwargs.get('logical_resource_id'):
            cf_kwargs.get('LogicalResourceId') = kwargs.get('logical_resource_id')
        if kwargs.get('physical_resource_id'):
            cf_kwargs.get('PhysicalResourceId') = kwargs.get('physical_resource_id')

        response = client.describe_stack_resources(**cf_params)

        resources = []
        for resource in response.get('StackResources', []):
            resources.append({
                'stack_name': resource.get('StackName'),
                'stack_id': resource.get('StackId'),
                'logical_resource_id': resource.get('LogicalResourceId'),
                'physical_resource_id': resource.get('PhysicalResourceId'),
                'resource_type': resource.get('ResourceType'),
                'timestamp': resource.get('Timestamp'),
                'resource_status': resource.get('ResourceStatus'),
                'resource_status_reason': resource.get('ResourceStatusReason'),
                'description': resource.get('Description'),
                'drift_information': resource.get('DriftInformation'),
                'module_info': resource.get('ModuleInfo'),
                'resource_attributes': resource.get('ResourceAttributes', [])
            })

        return {
            'resources': resources,
            'total_count': len(resources)
        }

    def _get_template(self, **kwargs) -> Dict[str, Any]:
        """Obtiene el template de un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}
        if kwargs.get('change_set_name'):
            cf_kwargs.get('ChangeSetName') = kwargs.get('change_set_name')

        response = client.get_template(**cf_params)

        return {
            'stack_name': kwargs.get('stack_name'),
            'template_body': response.get('TemplateBody'),
            'stages_available': response.get('StagesAvailable', [])
        }

    def _validate_template(self, **kwargs) -> Dict[str, Any]:
        """Valida un template CloudFormation"""
        client = self._get_client()

        cf_params = {}
        if kwargs.get('template_body'):
            cf_kwargs.get('TemplateBody') = kwargs.get('template_body')
        if kwargs.get('template_url'):
            cf_kwargs.get('TemplateURL') = kwargs.get('template_url')

        response = client.validate_template(**cf_params)

        return {
            'description': response.get('Description'),
            'parameters': response.get('Parameters', []),
            'capabilities': response.get('Capabilities', []),
            'capabilities_reason': response.get('CapabilitiesReason')
        }

    def _list_exports(self, **kwargs) -> Dict[str, Any]:
        """Lista exports de stacks"""
        client = self._get_client()

        cf_params = {}
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.list_exports(**cf_params)

        exports = []
        for export in response.get('Exports', []):
            exports.append({
                'exporting_stack_id': export.get('ExportingStackId'),
                'name': export.get('Name'),
                'value': export.get('Value'),
                'description': export.get('Description')
            })

        return {
            'exports': exports,
            'total_count': len(exports),
            'next_token': response.get('NextToken')
        }

    def _list_imports(self, **kwargs) -> Dict[str, Any]:
        """Lista imports de un export"""
        client = self._get_client()

        cf_params = {'ExportName': kwargs.get('export_name')}
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.list_imports(**cf_params)

        return {
            'export_name': kwargs.get('export_name'),
            'imports': response.get('Imports', []),
            'total_count': len(response.get('Imports', [])),
            'next_token': response.get('NextToken')
        }

    def _describe_stack_events(self, **kwargs) -> Dict[str, Any]:
        """Describe eventos de un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}
        if kwargs.get('next_token'):
            cf_kwargs.get('NextToken') = kwargs.get('next_token')

        response = client.describe_stack_events(**cf_params)

        events = []
        for event in response.get('StackEvents', []):
            events.append({
                'timestamp': event.get('Timestamp'),
                'logical_resource_id': event.get('LogicalResourceId'),
                'physical_resource_id': event.get('PhysicalResourceId'),
                'resource_type': event.get('ResourceType'),
                'resource_status': event.get('ResourceStatus'),
                'resource_status_reason': event.get('ResourceStatusReason'),
                'resource_properties': event.get('ResourceProperties'),
                'stack_id': event.get('StackId'),
                'stack_name': event.get('StackName'),
                'client_request_token': event.get('ClientRequestToken'),
                'hook_type': event.get('HookType'),
                'hook_status': event.get('HookStatus'),
                'hook_status_reason': event.get('HookStatusReason'),
                'hook_invocation_point': event.get('HookInvocationPoint'),
                'hook_failure_mode': event.get('HookFailureMode')
            })

        return {
            'stack_name': kwargs.get('stack_name'),
            'events': events,
            'total_count': len(events),
            'next_token': response.get('NextToken')
        }

    def _set_stack_policy(self, **kwargs) -> Dict[str, Any]:
        """Establece la política de un stack"""
        client = self._get_client()

        cf_params = {'StackName': kwargs.get('stack_name')}

        if kwargs.get('stack_policy_body'):
            cf_kwargs.get('StackPolicyBody') = kwargs.get('stack_policy_body')
        if kwargs.get('stack_policy_url'):
            cf_kwargs.get('StackPolicyURL') = kwargs.get('stack_policy_url')

        client.set_stack_policy(**cf_params)

        return {
            'message': f'Política del stack {kwargs.get('stack_name')} establecida exitosamente'
        }

    def _get_stack_policy(self, **kwargs) -> Dict[str, Any]:
        """Obtiene la política de un stack"""
        client = self._get_client()

        response = client.get_stack_policy(StackName=kwargs.get('stack_name'))

        return {
            'stack_name': kwargs.get('stack_name'),
            'stack_policy_body': response.get('StackPolicyBody')
        }