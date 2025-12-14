"""
Herramientas MCP para AWS EventBridge
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class EventBridgeMCPTools:
    """Herramientas MCP para gestión de EventBridge (event buses, rules, targets)"""

    def __init__(self):
        self.events = None

    def _get_client(self):
        """Obtiene el cliente de EventBridge"""
        if self.events is None:
            self.events = get_aws_client('events')
        return self.events

    def list_event_buses(self) -> Dict[str, Any]:
        """
        Lista todos los event buses disponibles

        Returns:
            Dict con lista de event buses
        """
        try:
            client = self._get_client()
            response = client.list_event_buses()

            event_buses = []
            for bus in response['EventBuses']:
                bus_info = {
                    'name': bus['Name'],
                    'arn': bus['Arn'],
                    'description': bus.get('Description', ''),
                    'policy': bus.get('Policy', ''),
                    'creation_time': bus.get('CreationTime', 'N/A'),
                    'last_modified_time': bus.get('LastModifiedTime', 'N/A')
                }
                event_buses.append(bus_info)

            return {
                'success': True,
                'event_buses': event_buses,
                'total_count': len(event_buses)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'event_buses': []
            }

    def create_event_bus(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea un nuevo event bus personalizado

        Args:
            name: Nombre del event bus
            description: Descripción opcional

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            create_params = {'Name': name}
            if description:
                create_params['Description'] = description

            response = client.create_event_bus(**create_params)

            return {
                'success': True,
                'event_bus_arn': response.get('EventBusArn', ''),
                'message': f'Event bus {name} creado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_rules(self, event_bus_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista todas las reglas de EventBridge

        Args:
            event_bus_name: Nombre del event bus (opcional, default usa 'default')

        Returns:
            Dict con lista de reglas
        """
        try:
            client = self._get_client()

            list_params = {}
            if event_bus_name:
                list_params['EventBusName'] = event_bus_name

            response = client.list_rules(**list_params)

            rules = []
            for rule in response['Rules']:
                rule_info = {
                    'name': rule['Name'],
                    'arn': rule['Arn'],
                    'event_pattern': rule.get('EventPattern', ''),
                    'schedule_expression': rule.get('ScheduleExpression', ''),
                    'state': rule['State'],
                    'description': rule.get('Description', ''),
                    'managed_by': rule.get('ManagedBy', ''),
                    'role_arn': rule.get('RoleArn', ''),
                    'event_bus_name': rule.get('EventBusName', 'default'),
                    'created_by': rule.get('CreatedBy', ''),
                    'creation_time': rule.get('CreationTime', 'N/A')
                }
                rules.append(rule_info)

            return {
                'success': True,
                'rules': rules,
                'total_count': len(rules)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rules': []
            }

    def create_rule(self, name: str, event_bus_name: str = 'default',
                   description: Optional[str] = None, event_pattern: Optional[str] = None,
                   schedule_expression: Optional[str] = None, state: str = 'ENABLED',
                   role_arn: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una nueva regla de EventBridge

        Args:
            name: Nombre de la regla
            event_bus_name: Nombre del event bus
            description: Descripción opcional
            event_pattern: Patrón de evento en JSON
            schedule_expression: Expresión de schedule (rate o cron)
            state: Estado de la regla (ENABLED/DISABLED)
            role_arn: ARN del rol IAM

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            put_params = {
                'Name': name,
                'EventBusName': event_bus_name,
                'State': state
            }

            if description:
                put_params['Description'] = description

            if event_pattern:
                put_params['EventPattern'] = event_pattern

            if schedule_expression:
                put_params['ScheduleExpression'] = schedule_expression

            if role_arn:
                put_params['RoleArn'] = role_arn

            response = client.put_rule(**put_params)

            return {
                'success': True,
                'rule_arn': response.get('RuleArn', ''),
                'message': f'Regla {name} creada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_targets_by_rule(self, rule_name: str, event_bus_name: str = 'default') -> Dict[str, Any]:
        """
        Lista los targets de una regla específica

        Args:
            rule_name: Nombre de la regla
            event_bus_name: Nombre del event bus

        Returns:
            Dict con lista de targets
        """
        try:
            client = self._get_client()

            response = client.list_targets_by_rule(
                Rule=rule_name,
                EventBusName=event_bus_name
            )

            targets = []
            for target in response['Targets']:
                target_info = {
                    'id': target['Id'],
                    'arn': target['Arn'],
                    'role_arn': target.get('RoleArn', ''),
                    'input': target.get('Input', ''),
                    'input_path': target.get('InputPath', ''),
                    'input_transformer': target.get('InputTransformer', {}),
                    'kinesis_parameters': target.get('KinesisParameters', {}),
                    'run_command_parameters': target.get('RunCommandParameters', {}),
                    'ecs_parameters': target.get('EcsParameters', {}),
                    'batch_parameters': target.get('BatchParameters', {}),
                    'sqs_parameters': target.get('SqsParameters', {}),
                    'http_parameters': target.get('HttpParameters', {}),
                    'redshift_data_parameters': target.get('RedshiftDataParameters', {}),
                    'sage_maker_pipeline_parameters': target.get('SageMakerPipelineParameters', {})
                }
                targets.append(target_info)

            return {
                'success': True,
                'targets': targets,
                'total_count': len(targets)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'targets': []
            }

    def put_targets(self, rule_name: str, targets: List[Dict[str, Any]],
                   event_bus_name: str = 'default') -> Dict[str, Any]:
        """
        Agrega targets a una regla

        Args:
            rule_name: Nombre de la regla
            targets: Lista de targets a agregar
            event_bus_name: Nombre del event bus

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            # Formatear targets para la API
            formatted_targets = []
            for target in targets:
                formatted_target = {
                    'Id': target['id'],
                    'Arn': target['arn']
                }

                if 'role_arn' in target and target['role_arn']:
                    formatted_target['RoleArn'] = target['role_arn']

                if 'input' in target and target['input']:
                    formatted_target['Input'] = target['input']

                if 'input_path' in target and target['input_path']:
                    formatted_target['InputPath'] = target['input_path']

                formatted_targets.append(formatted_target)

            response = client.put_targets(
                Rule=rule_name,
                EventBusName=event_bus_name,
                Targets=formatted_targets
            )

            failed_count = response.get('FailedEntryCount', 0)
            if failed_count == 0:
                return {
                    'success': True,
                    'message': f'{len(targets)} targets agregados exitosamente a la regla {rule_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'{failed_count} targets fallaron al agregarse',
                    'failed_entries': response.get('FailedEntries', [])
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def remove_targets(self, rule_name: str, target_ids: List[str],
                      event_bus_name: str = 'default') -> Dict[str, Any]:
        """
        Remueve targets de una regla

        Args:
            rule_name: Nombre de la regla
            target_ids: Lista de IDs de targets a remover
            event_bus_name: Nombre del event bus

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            response = client.remove_targets(
                Rule=rule_name,
                EventBusName=event_bus_name,
                Ids=target_ids
            )

            failed_count = response.get('FailedEntryCount', 0)
            if failed_count == 0:
                return {
                    'success': True,
                    'message': f'{len(target_ids)} targets removidos exitosamente de la regla {rule_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'{failed_count} targets fallaron al removerse',
                    'failed_entries': response.get('FailedEntries', [])
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def put_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envía eventos personalizados al Event Bus

        Args:
            events: Lista de eventos a enviar

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            # Formatear eventos para la API
            formatted_events = []
            for event in events:
                formatted_event = {
                    'Source': event['source'],
                    'DetailType': event['detail_type'],
                    'Detail': event['detail']
                }

                if 'event_bus_name' in event and event['event_bus_name']:
                    formatted_event['EventBusName'] = event['event_bus_name']

                formatted_events.append(formatted_event)

            response = client.put_events(Entries=formatted_events)

            failed_count = response.get('FailedEntryCount', 0)
            if failed_count == 0:
                return {
                    'success': True,
                    'message': f'{len(events)} eventos enviados exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': f'{failed_count} eventos fallaron al enviarse',
                    'failed_entries': response.get('Entries', [])
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para EventBridge"""
        return [
            {
                'name': 'eventbridge_list_event_buses',
                'description': 'Lista todos los event buses disponibles',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                },
                'function': self.list_event_buses
            },
            {
                'name': 'eventbridge_create_event_bus',
                'description': 'Crea un nuevo event bus personalizado',
                'parameters': {
                    'type': 'object',
                    'required': ['name'],
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Nombre del event bus'
                        },
                        'description': {
                            'type': 'string',
                            'description': 'Descripción opcional del event bus'
                        }
                    }
                },
                'function': self.create_event_bus
            },
            {
                'name': 'eventbridge_list_rules',
                'description': 'Lista todas las reglas de EventBridge',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'event_bus_name': {
                            'type': 'string',
                            'description': 'Nombre del event bus (opcional)',
                            'default': 'default'
                        }
                    }
                },
                'function': self.list_rules
            },
            {
                'name': 'eventbridge_create_rule',
                'description': 'Crea una nueva regla de EventBridge',
                'parameters': {
                    'type': 'object',
                    'required': ['name'],
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Nombre de la regla'
                        },
                        'event_bus_name': {
                            'type': 'string',
                            'description': 'Nombre del event bus',
                            'default': 'default'
                        },
                        'description': {
                            'type': 'string',
                            'description': 'Descripción opcional de la regla'
                        },
                        'event_pattern': {
                            'type': 'string',
                            'description': 'Patrón de evento en JSON'
                        },
                        'schedule_expression': {
                            'type': 'string',
                            'description': 'Expresión de schedule (rate o cron)'
                        },
                        'state': {
                            'type': 'string',
                            'description': 'Estado de la regla',
                            'enum': ['ENABLED', 'DISABLED'],
                            'default': 'ENABLED'
                        },
                        'role_arn': {
                            'type': 'string',
                            'description': 'ARN del rol IAM'
                        }
                    }
                },
                'function': self.create_rule
            },
            {
                'name': 'eventbridge_list_targets_by_rule',
                'description': 'Lista los targets de una regla específica',
                'parameters': {
                    'type': 'object',
                    'required': ['rule_name'],
                    'properties': {
                        'rule_name': {
                            'type': 'string',
                            'description': 'Nombre de la regla'
                        },
                        'event_bus_name': {
                            'type': 'string',
                            'description': 'Nombre del event bus',
                            'default': 'default'
                        }
                    }
                },
                'function': self.list_targets_by_rule
            },
            {
                'name': 'eventbridge_put_targets',
                'description': 'Agrega targets a una regla de EventBridge',
                'parameters': {
                    'type': 'object',
                    'required': ['rule_name', 'targets'],
                    'properties': {
                        'rule_name': {
                            'type': 'string',
                            'description': 'Nombre de la regla'
                        },
                        'targets': {
                            'type': 'array',
                            'description': 'Lista de targets a agregar',
                            'items': {
                                'type': 'object',
                                'required': ['id', 'arn'],
                                'properties': {
                                    'id': {'type': 'string', 'description': 'ID del target'},
                                    'arn': {'type': 'string', 'description': 'ARN del target'},
                                    'role_arn': {'type': 'string', 'description': 'ARN del rol IAM'},
                                    'input': {'type': 'string', 'description': 'Input personalizado'},
                                    'input_path': {'type': 'string', 'description': 'JSONPath para input'}
                                }
                            }
                        },
                        'event_bus_name': {
                            'type': 'string',
                            'description': 'Nombre del event bus',
                            'default': 'default'
                        }
                    }
                },
                'function': self.put_targets
            },
            {
                'name': 'eventbridge_remove_targets',
                'description': 'Remueve targets de una regla de EventBridge',
                'parameters': {
                    'type': 'object',
                    'required': ['rule_name', 'target_ids'],
                    'properties': {
                        'rule_name': {
                            'type': 'string',
                            'description': 'Nombre de la regla'
                        },
                        'target_ids': {
                            'type': 'array',
                            'description': 'Lista de IDs de targets a remover',
                            'items': {'type': 'string'}
                        },
                        'event_bus_name': {
                            'type': 'string',
                            'description': 'Nombre del event bus',
                            'default': 'default'
                        }
                    }
                },
                'function': self.remove_targets
            },
            {
                'name': 'eventbridge_put_events',
                'description': 'Envía eventos personalizados al Event Bus',
                'parameters': {
                    'type': 'object',
                    'required': ['events'],
                    'properties': {
                        'events': {
                            'type': 'array',
                            'description': 'Lista de eventos a enviar',
                            'items': {
                                'type': 'object',
                                'required': ['source', 'detail_type', 'detail'],
                                'properties': {
                                    'source': {'type': 'string', 'description': 'Fuente del evento'},
                                    'detail_type': {'type': 'string', 'description': 'Tipo de detalle'},
                                    'detail': {'type': 'string', 'description': 'Detalle del evento en JSON'},
                                    'event_bus_name': {'type': 'string', 'description': 'Nombre del event bus'}
                                }
                            }
                        }
                    }
                },
                'function': self.put_events
            }
        ]