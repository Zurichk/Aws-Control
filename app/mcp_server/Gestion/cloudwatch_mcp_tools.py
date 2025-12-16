"""
MCP Tools para AWS CloudWatch
Herramientas para gestión de monitoreo, métricas y logs
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class CloudWatchMCPTools:
    """Herramientas MCP para operaciones con AWS CloudWatch"""

    # Constantes para descripciones
    DESC_ALARM_NAME = 'Nombre de la alarma'
    DESC_METRIC_NAME = 'Nombre de la métrica'
    DESC_NAMESPACE = 'Namespace de la métrica'
    DESC_LOG_GROUP_NAME = 'Nombre del grupo de logs'
    DESC_LOG_STREAM_NAME = 'Nombre del stream de logs'
    DESC_DASHBOARD_NAME = 'Nombre del dashboard'

    def __init__(self):
        self.cw_client = None
        self.logs_client = None

    def _get_cw_client(self):
        """Obtiene el cliente CloudWatch"""
        if self.cw_client is None:
            self.cw_client = get_aws_client('cloudwatch')
        return self.cw_client

    def _get_logs_client(self):
        """Obtiene el cliente CloudWatch Logs"""
        if self.logs_client is None:
            self.logs_client = get_aws_client('logs')
        return self.logs_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para CloudWatch"""
        return [
            {
                'name': 'cloudwatch_put_metric_alarm',
                'description': 'Crear una nueva alarma métrica en CloudWatch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'alarm_name': {'type': 'string', 'description': self.DESC_ALARM_NAME},
                        'alarm_description': {'type': 'string', 'description': 'Descripción de la alarma'},
                        'metric_name': {'type': 'string', 'description': self.DESC_METRIC_NAME},
                        'namespace': {'type': 'string', 'description': self.DESC_NAMESPACE},
                        'statistic': {'type': 'string', 'description': 'Estadística', 'enum': ['Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']},
                        'comparison_operator': {'type': 'string', 'description': 'Operador de comparación', 'enum': ['GreaterThanThreshold', 'GreaterThanOrEqualToThreshold', 'LessThanThreshold', 'LessThanOrEqualToThreshold']},
                        'threshold': {'type': 'number', 'description': 'Valor umbral'},
                        'period': {'type': 'integer', 'description': 'Período en segundos', 'default': 300},
                        'evaluation_periods': {'type': 'integer', 'description': 'Número de períodos de evaluación', 'default': 2},
                        'alarm_actions': {'type': 'array', 'items': {'type': 'string'}, 'description': 'ARNs de acciones para estado ALARM'},
                        'ok_actions': {'type': 'array', 'items': {'type': 'string'}, 'description': 'ARNs de acciones para estado OK'}
                    },
                    'required': ['alarm_name', 'metric_name', 'namespace', 'statistic', 'comparison_operator', 'threshold']
                }
            },
            {
                'name': 'cloudwatch_delete_alarms',
                'description': 'Eliminar alarmas de CloudWatch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'alarm_names': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Lista de nombres de alarmas a eliminar'}
                    },
                    'required': ['alarm_names']
                }
            },
            {
                'name': 'cloudwatch_describe_alarms',
                'description': 'Describir alarmas de CloudWatch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'alarm_names': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Lista de nombres de alarmas (opcional)'},
                        'alarm_name_prefix': {'type': 'string', 'description': 'Prefijo de nombre de alarma'},
                        'state_value': {'type': 'string', 'description': 'Estado de la alarma', 'enum': ['OK', 'ALARM', 'INSUFFICIENT_DATA']},
                        'max_records': {'type': 'integer', 'description': 'Máximo número de registros', 'default': 100}
                    }
                }
            },
            {
                'name': 'cloudwatch_put_metric_data',
                'description': 'Enviar datos métricos personalizados a CloudWatch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'namespace': {'type': 'string', 'description': self.DESC_NAMESPACE},
                        'metric_data': {
                            'type': 'array',
                            'description': 'Lista de datos métricos',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'metric_name': {'type': 'string', 'description': self.DESC_METRIC_NAME},
                                    'value': {'type': 'number', 'description': 'Valor de la métrica'},
                                    'unit': {'type': 'string', 'description': 'Unidad de medida', 'enum': ['Count', 'Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes', 'Terabytes', 'Bits', 'Kilobits', 'Megabits', 'Gigabits', 'Terabits', 'Percent', 'Count/Second', 'Bytes/Second', 'Kilobytes/Second', 'Megabytes/Second', 'Gigabytes/Second', 'Terabytes/Second', 'Bits/Second', 'Kilobits/Second', 'Megabits/Second', 'Gigabits/Second', 'Terabits/Second', 'None']},
                                    'timestamp': {'type': 'string', 'description': 'Timestamp (ISO format)'},
                                    'dimensions': {
                                        'type': 'array',
                                        'description': 'Dimensiones de la métrica',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'name': {'type': 'string'},
                                                'value': {'type': 'string'}
                                            },
                                            'required': ['name', 'value']
                                        }
                                    }
                                },
                                'required': ['metric_name', 'value']
                            }
                        }
                    },
                    'required': ['namespace', 'metric_data']
                }
            },
            {
                'name': 'cloudwatch_get_metric_statistics',
                'description': 'Obtener estadísticas de una métrica específica',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'namespace': {'type': 'string', 'description': self.DESC_NAMESPACE},
                        'metric_name': {'type': 'string', 'description': self.DESC_METRIC_NAME},
                        'dimensions': {
                            'type': 'array',
                            'description': 'Dimensiones de la métrica',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'value': {'type': 'string'}
                                },
                                'required': ['name', 'value']
                            }
                        },
                        'start_time': {'type': 'string', 'description': 'Fecha/hora de inicio (ISO format)'},
                        'end_time': {'type': 'string', 'description': 'Fecha/hora de fin (ISO format)'},
                        'period': {'type': 'integer', 'description': 'Período en segundos', 'default': 300},
                        'statistics': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Lista de estadísticas', 'enum': ['Average', 'Sum', 'Maximum', 'Minimum', 'SampleCount']}
                    },
                    'required': ['namespace', 'metric_name', 'start_time', 'end_time', 'statistics']
                }
            },
            {
                'name': 'cloudwatch_list_metrics',
                'description': 'Listar métricas disponibles en CloudWatch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'namespace': {'type': 'string', 'description': 'Filtrar por namespace'},
                        'metric_name': {'type': 'string', 'description': 'Filtrar por nombre de métrica'},
                        'dimensions': {
                            'type': 'array',
                            'description': 'Filtrar por dimensiones',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'value': {'type': 'string'}
                                },
                                'required': ['name', 'value']
                            }
                        },
                        'max_records': {'type': 'integer', 'description': 'Máximo número de registros', 'default': 500}
                    }
                }
            },
            {
                'name': 'cloudwatch_create_log_group',
                'description': 'Crear un grupo de logs en CloudWatch Logs',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name': {'type': 'string', 'description': self.DESC_LOG_GROUP_NAME},
                        'kms_key_id': {'type': 'string', 'description': 'ID de la clave KMS para encriptación'},
                        'tags': {'type': 'object', 'description': 'Tags para el grupo de logs'}
                    },
                    'required': ['log_group_name']
                }
            },
            {
                'name': 'cloudwatch_delete_log_group',
                'description': 'Eliminar un grupo de logs',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name': {'type': 'string', 'description': self.DESC_LOG_GROUP_NAME}
                    },
                    'required': ['log_group_name']
                }
            },
            {
                'name': 'cloudwatch_describe_log_groups',
                'description': 'Describir grupos de logs',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name_prefix': {'type': 'string', 'description': 'Prefijo del nombre del grupo'},
                        'max_results': {'type': 'integer', 'description': 'Máximo número de resultados', 'default': 50}
                    }
                }
            },
            {
                'name': 'cloudwatch_create_log_stream',
                'description': 'Crear un stream de logs en un grupo',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name': {'type': 'string', 'description': self.DESC_LOG_GROUP_NAME},
                        'log_stream_name': {'type': 'string', 'description': self.DESC_LOG_STREAM_NAME}
                    },
                    'required': ['log_group_name', 'log_stream_name']
                }
            },
            {
                'name': 'cloudwatch_put_log_events',
                'description': 'Enviar eventos de log a un stream',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name': {'type': 'string', 'description': self.DESC_LOG_GROUP_NAME},
                        'log_stream_name': {'type': 'string', 'description': self.DESC_LOG_STREAM_NAME},
                        'log_events': {
                            'type': 'array',
                            'description': 'Lista de eventos de log',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'timestamp': {'type': 'integer', 'description': 'Timestamp en milisegundos'},
                                    'message': {'type': 'string', 'description': 'Mensaje del log'}
                                },
                                'required': ['timestamp', 'message']
                            }
                        },
                        'sequence_token': {'type': 'string', 'description': 'Token de secuencia para ordenamiento'}
                    },
                    'required': ['log_group_name', 'log_stream_name', 'log_events']
                }
            },
            {
                'name': 'cloudwatch_get_log_events',
                'description': 'Obtener eventos de log de un stream',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'log_group_name': {'type': 'string', 'description': self.DESC_LOG_GROUP_NAME},
                        'log_stream_name': {'type': 'string', 'description': self.DESC_LOG_STREAM_NAME},
                        'start_time': {'type': 'integer', 'description': 'Timestamp de inicio en milisegundos'},
                        'end_time': {'type': 'integer', 'description': 'Timestamp de fin en milisegundos'},
                        'start_from_head': {'type': 'boolean', 'description': 'Empezar desde el inicio', 'default': True},
                        'limit': {'type': 'integer', 'description': 'Límite de eventos', 'default': 100}
                    },
                    'required': ['log_group_name', 'log_stream_name']
                }
            },
            {
                'name': 'cloudwatch_put_dashboard',
                'description': 'Crear o actualizar un dashboard',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'dashboard_name': {'type': 'string', 'description': self.DESC_DASHBOARD_NAME},
                        'dashboard_body': {'type': 'string', 'description': 'Cuerpo del dashboard en JSON'}
                    },
                    'required': ['dashboard_name', 'dashboard_body']
                }
            },
            {
                'name': 'cloudwatch_get_dashboard',
                'description': 'Obtener un dashboard',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'dashboard_name': {'type': 'string', 'description': self.DESC_DASHBOARD_NAME}
                    },
                    'required': ['dashboard_name']
                }
            },
            {
                'name': 'cloudwatch_list_dashboards',
                'description': 'Listar dashboards',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'dashboard_name_prefix': {'type': 'string', 'description': 'Prefijo del nombre del dashboard'},
                        'max_records': {'type': 'integer', 'description': 'Máximo número de registros', 'default': 100}
                    }
                }
            },
            {
                'name': 'cloudwatch_delete_dashboard',
                'description': 'Eliminar un dashboard',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'dashboard_name': {'type': 'string', 'description': self.DESC_DASHBOARD_NAME}
                    },
                    'required': ['dashboard_name']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de CloudWatch"""
        try:
            if tool_name == 'cloudwatch_put_metric_alarm':
                return self._put_metric_alarm(**parameters)
            elif tool_name == 'cloudwatch_delete_alarms':
                return self._delete_alarms(**parameters)
            elif tool_name == 'cloudwatch_describe_alarms':
                return self._describe_alarms(**parameters)
            elif tool_name == 'cloudwatch_put_metric_data':
                return self._put_metric_data(**parameters)
            elif tool_name == 'cloudwatch_get_metric_statistics':
                return self._get_metric_statistics(**parameters)
            elif tool_name == 'cloudwatch_list_metrics':
                return self._list_metrics(**parameters)
            elif tool_name == 'cloudwatch_create_log_group':
                return self._create_log_group(**parameters)
            elif tool_name == 'cloudwatch_delete_log_group':
                return self._delete_log_group(**parameters)
            elif tool_name == 'cloudwatch_describe_log_groups':
                return self._describe_log_groups(**parameters)
            elif tool_name == 'cloudwatch_create_log_stream':
                return self._create_log_stream(**parameters)
            elif tool_name == 'cloudwatch_put_log_events':
                return self._put_log_events(**parameters)
            elif tool_name == 'cloudwatch_get_log_events':
                return self._get_log_events(**parameters)
            elif tool_name == 'cloudwatch_put_dashboard':
                return self._put_dashboard(**parameters)
            elif tool_name == 'cloudwatch_get_dashboard':
                return self._get_dashboard(**parameters)
            elif tool_name == 'cloudwatch_list_dashboards':
                return self._list_dashboards(**parameters)
            elif tool_name == 'cloudwatch_delete_dashboard':
                return self._delete_dashboard(**parameters)
            else:
                return {'error': f'Herramienta CloudWatch no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta CloudWatch {tool_name}: {str(e)}'}

    def _put_metric_alarm(self, **kwargs) -> Dict[str, Any]:
        """Crear una nueva alarma métrica en CloudWatch"""
        client = self._get_cw_client()

        api_params = {
            'AlarmName': kwargs.get('alarm_name'),
            'MetricName': kwargs.get('metric_name'),
            'Namespace': kwargs.get('namespace'),
            'Statistic': kwargs.get('statistic'),
            'ComparisonOperator': kwargs.get('comparison_operator'),
            'Threshold': kwargs.get('threshold'),
            'Period': kwargs.get('period', 300),
            'EvaluationPeriods': kwargs.get('evaluation_periods', 2)
        }

        if kwargs.get('alarm_description'):
            api_kwargs.get('AlarmDescription') = kwargs.get('alarm_description')
        if kwargs.get('alarm_actions'):
            api_kwargs.get('AlarmActions') = kwargs.get('alarm_actions')
        if kwargs.get('ok_actions'):
            api_kwargs.get('OKActions') = kwargs.get('ok_actions')

        client.put_metric_alarm(**api_params)

        return {
            'message': f'Alarma métrica {kwargs.get('alarm_name')} creada exitosamente'
        }

    def _delete_alarms(self, **kwargs) -> Dict[str, Any]:
        """Eliminar alarmas de CloudWatch"""
        client = self._get_cw_client()

        client.delete_alarms(AlarmNames=kwargs.get('alarm_names'))

        return {
            'message': f'Alarmas eliminadas exitosamente: {", ".join(kwargs.get('alarm_names'))}'
        }

    def _describe_alarms(self, **kwargs) -> Dict[str, Any]:
        """Describir alarmas de CloudWatch"""
        client = self._get_cw_client()

        api_params = {}
        if kwargs.get('alarm_names'):
            api_kwargs.get('AlarmNames') = kwargs.get('alarm_names')
        if kwargs.get('alarm_name_prefix'):
            api_kwargs.get('AlarmNamePrefix') = kwargs.get('alarm_name_prefix')
        if kwargs.get('state_value'):
            api_kwargs.get('StateValue') = kwargs.get('state_value')
        if kwargs.get('max_records'):
            api_kwargs.get('MaxRecords') = kwargs.get('max_records', 100)

        response = client.describe_alarms(**api_params)

        alarms = []
        for alarm in response.get('MetricAlarms', []):
            alarms.append({
                'alarm_name': alarm.get('AlarmName'),
                'alarm_description': alarm.get('AlarmDescription'),
                'state_value': alarm.get('StateValue'),
                'state_reason': alarm.get('StateReason'),
                'metric_name': alarm.get('MetricName'),
                'namespace': alarm.get('Namespace'),
                'statistic': alarm.get('Statistic'),
                'comparison_operator': alarm.get('ComparisonOperator'),
                'threshold': alarm.get('Threshold'),
                'evaluation_periods': alarm.get('EvaluationPeriods')
            })

        return {
            'alarms': alarms,
            'total_count': len(alarms)
        }

    def _put_metric_data(self, **kwargs) -> Dict[str, Any]:
        """Enviar datos métricos personalizados a CloudWatch"""
        client = self._get_cw_client()

        metric_data = []
        for data in kwargs.get('metric_data'):
            metric = {
                'MetricName': data['metric_name'],
                'Value': data['value']
            }

            if 'unit' in data:
                metric['Unit'] = data['unit']
            if 'timestamp' in data:
                from datetime import datetime
                metric['Timestamp'] = datetime.fromisoformat(data['timestamp'])
            if 'dimensions' in data:
                metric['Dimensions'] = [{'Name': d['name'], 'Value': d['value']} for d in data['dimensions']]

            metric_data.append(metric)

        client.put_metric_data(
            Namespace=kwargs.get('namespace'),
            MetricData=metric_data
        )

        return {
            'message': f'Datos métricos enviados exitosamente al namespace {kwargs.get('namespace')}',
            'metrics_count': len(metric_data)
        }

    def _get_metric_statistics(self, **kwargs) -> Dict[str, Any]:
        """Obtener estadísticas de una métrica específica"""
        client = self._get_cw_client()

        api_params = {
            'Namespace': kwargs.get('namespace'),
            'MetricName': kwargs.get('metric_name'),
            'StartTime': kwargs.get('start_time'),
            'EndTime': kwargs.get('end_time'),
            'Period': kwargs.get('period', 300),
            'Statistics': kwargs.get('statistics')
        }

        if kwargs.get('dimensions'):
            api_kwargs.get('Dimensions') = [{'Name': d['name'], 'Value': d['value']} for d in kwargs.get('dimensions')]

        response = client.get_metric_statistics(**api_params)

        datapoints = []
        for dp in response.get('Datapoints', []):
            datapoints.append({
                'timestamp': dp.get('Timestamp'),
                'average': dp.get('Average'),
                'sum': dp.get('Sum'),
                'maximum': dp.get('Maximum'),
                'minimum': dp.get('Minimum'),
                'sample_count': dp.get('SampleCount'),
                'unit': dp.get('Unit')
            })

        return {
            'label': response.get('Label'),
            'datapoints': sorted(datapoints, key=lambda x: x['timestamp']),
            'total_datapoints': len(datapoints)
        }

    def _list_metrics(self, **kwargs) -> Dict[str, Any]:
        """Listar métricas disponibles en CloudWatch"""
        client = self._get_cw_client()

        api_params = {}
        if kwargs.get('namespace'):
            api_kwargs.get('Namespace') = kwargs.get('namespace')
        if kwargs.get('metric_name'):
            api_kwargs.get('MetricName') = kwargs.get('metric_name')
        if kwargs.get('dimensions'):
            api_kwargs.get('Dimensions') = [{'Name': d['name'], 'Value': d['value']} for d in kwargs.get('dimensions')]

        response = client.list_metrics(**api_params)

        metrics = []
        max_records = kwargs.get('max_records', 500)
        for metric in response.get('Metrics', [])[:max_records]:
            metrics.append({
                'namespace': metric.get('Namespace'),
                'metric_name': metric.get('MetricName'),
                'dimensions': [{'name': d['Name'], 'value': d['Value']} for d in metric.get('Dimensions', [])]
            })

        return {
            'metrics': metrics,
            'total_count': len(metrics),
            'truncated': len(response.get('Metrics', [])) > max_records
        }

    def _create_log_group(self, **kwargs) -> Dict[str, Any]:
        """Crear un grupo de logs en CloudWatch Logs"""
        client = self._get_logs_client()

        api_params = {'logGroupName': kwargs.get('log_group_name')}

        if kwargs.get('kms_key_id'):
            api_kwargs.get('kmsKeyId') = kwargs.get('kms_key_id')
        if kwargs.get('tags'):
            api_kwargs.get('tags') = kwargs.get('tags')

        client.create_log_group(**api_params)

        return {
            'message': f'Grupo de logs {kwargs.get('log_group_name')} creado exitosamente'
        }

    def _delete_log_group(self, **kwargs) -> Dict[str, Any]:
        """Eliminar un grupo de logs"""
        client = self._get_logs_client()

        client.delete_log_group(logGroupName=kwargs.get('log_group_name'))

        return {
            'message': f'Grupo de logs {kwargs.get('log_group_name')} eliminado exitosamente'
        }

    def _describe_log_groups(self, **kwargs) -> Dict[str, Any]:
        """Describir grupos de logs"""
        client = self._get_logs_client()

        api_params = {}
        if kwargs.get('log_group_name_prefix'):
            api_kwargs.get('logGroupNamePrefix') = kwargs.get('log_group_name_prefix')
        if kwargs.get('max_results'):
            api_kwargs.get('maxResults') = kwargs.get('max_results', 50)

        response = client.describe_log_groups(**api_params)

        log_groups = []
        for lg in response.get('logGroups', []):
            log_groups.append({
                'log_group_name': lg.get('logGroupName'),
                'creation_time': lg.get('creationTime'),
                'retention_in_days': lg.get('retentionInDays'),
                'metric_filter_count': lg.get('metricFilterCount', 0),
                'arn': lg.get('arn'),
                'stored_bytes': lg.get('storedBytes')
            })

        return {
            'log_groups': log_groups,
            'total_count': len(log_groups)
        }

    def _create_log_stream(self, **kwargs) -> Dict[str, Any]:
        """Crear un stream de logs en un grupo"""
        client = self._get_logs_client()

        client.create_log_stream(
            logGroupName=kwargs.get('log_group_name'),
            logStreamName=kwargs.get('log_stream_name')
        )

        return {
            'message': f'Stream de logs {kwargs.get('log_stream_name')} creado en grupo {kwargs.get('log_group_name')}'
        }

    def _put_log_events(self, **kwargs) -> Dict[str, Any]:
        """Enviar eventos de log a un stream"""
        client = self._get_logs_client()

        log_events = [{'timestamp': event['timestamp'], 'message': event['message']} for event in kwargs.get('log_events')]

        api_params = {
            'logGroupName': kwargs.get('log_group_name'),
            'logStreamName': kwargs.get('log_stream_name'),
            'logEvents': log_events
        }

        if kwargs.get('sequence_token'):
            api_kwargs.get('sequenceToken') = kwargs.get('sequence_token')

        response = client.put_log_events(**api_params)

        return {
            'message': f'{len(log_events)} eventos de log enviados exitosamente',
            'next_sequence_token': response.get('nextSequenceToken')
        }

    def _get_log_events(self, **kwargs) -> Dict[str, Any]:
        """Obtener eventos de log de un stream"""
        client = self._get_logs_client()

        api_params = {
            'logGroupName': kwargs.get('log_group_name'),
            'logStreamName': kwargs.get('log_stream_name')
        }

        if kwargs.get('start_time'):
            api_kwargs.get('startTime') = kwargs.get('start_time')
        if kwargs.get('end_time'):
            api_kwargs.get('endTime') = kwargs.get('end_time')
        if kwargs.get('start_from_head'):
            api_kwargs.get('startFromHead') = kwargs.get('start_from_head', True)
        if kwargs.get('limit'):
            api_kwargs.get('limit') = kwargs.get('limit', 100)

        response = client.get_log_events(**api_params)

        events = []
        for event in response.get('events', []):
            events.append({
                'timestamp': event.get('timestamp'),
                'message': event.get('message'),
                'ingestion_time': event.get('ingestionTime')
            })

        return {
            'events': events,
            'total_count': len(events),
            'next_forward_token': response.get('nextForwardToken'),
            'next_backward_token': response.get('nextBackwardToken')
        }

    def _put_dashboard(self, **kwargs) -> Dict[str, Any]:
        """Crear o actualizar un dashboard"""
        client = self._get_cw_client()

        client.put_dashboard(
            DashboardName=kwargs.get('dashboard_name'),
            DashboardBody=kwargs.get('dashboard_body')
        )

        return {
            'message': f'Dashboard {kwargs.get('dashboard_name')} creado/actualizado exitosamente'
        }

    def _get_dashboard(self, **kwargs) -> Dict[str, Any]:
        """Obtener un dashboard"""
        client = self._get_cw_client()

        response = client.get_dashboard(DashboardName=kwargs.get('dashboard_name'))

        return {
            'dashboard_name': response.get('DashboardName'),
            'dashboard_arn': response.get('DashboardArn'),
            'dashboard_body': response.get('DashboardBody')
        }

    def _list_dashboards(self, **kwargs) -> Dict[str, Any]:
        """Listar dashboards"""
        client = self._get_cw_client()

        api_params = {}
        if kwargs.get('dashboard_name_prefix'):
            api_kwargs.get('DashboardNamePrefix') = kwargs.get('dashboard_name_prefix')
        if kwargs.get('max_records'):
            api_kwargs.get('MaxRecords') = kwargs.get('max_records', 100)

        response = client.list_dashboards(**api_params)

        dashboards = []
        for db in response.get('DashboardEntries', []):
            dashboards.append({
                'dashboard_name': db.get('DashboardName'),
                'dashboard_arn': db.get('DashboardArn'),
                'last_modified': db.get('LastModified'),
                'size': db.get('Size')
            })

        return {
            'dashboards': dashboards,
            'total_count': len(dashboards)
        }

    def _delete_dashboard(self, **kwargs) -> Dict[str, Any]:
        """Eliminar un dashboard"""
        client = self._get_cw_client()

        client.delete_dashboards(DashboardNames=[kwargs.get('dashboard_name')])

        return {
            'message': f'Dashboard {kwargs.get('dashboard_name')} eliminado exitosamente'
        }


# Mantener compatibilidad con código existente
CLOUDWATCH_MCP_TOOLS = CloudWatchMCPTools()