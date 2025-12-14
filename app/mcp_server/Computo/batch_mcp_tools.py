"""
MCP Tools para AWS Batch
Herramientas para gestión de trabajos, colas de trabajos y entornos de computo
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class BatchMCPTools:
    """Herramientas MCP para AWS Batch"""

    def __init__(self):
        self.batch = None

    def _get_batch_client(self):
        """Obtiene el cliente Batch"""
        if self.batch is None:
            self.batch = get_aws_client('batch')
        return self.batch

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para AWS Batch"""
        return [
            {
                'name': 'batch_list_jobs',
                'description': 'Lista trabajos de AWS Batch con filtros opcionales',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'job_queue': {
                            'type': 'string',
                            'description': 'Nombre de la cola de trabajos para filtrar'
                        },
                        'job_status': {
                            'type': 'string',
                            'description': 'Estado de los trabajos (SUBMITTED, RUNNING, SUCCEEDED, FAILED, etc.)'
                        },
                        'max_results': {
                            'type': 'integer',
                            'description': 'Número máximo de resultados',
                            'default': 100
                        }
                    }
                },
                'function': self.list_batch_jobs
            },
            {
                'name': 'batch_submit_job',
                'description': 'Envía un nuevo trabajo de AWS Batch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'job_name': {
                            'type': 'string',
                            'description': 'Nombre del trabajo'
                        },
                        'job_queue': {
                            'type': 'string',
                            'description': 'Nombre de la cola de trabajos'
                        },
                        'job_definition': {
                            'type': 'string',
                            'description': 'Nombre de la definición del trabajo'
                        },
                        'container_overrides': {
                            'type': 'object',
                            'description': 'Overrides para el contenedor',
                            'properties': {
                                'vcpus': {'type': 'integer'},
                                'memory': {'type': 'integer'},
                                'command': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        },
                        'parameters': {
                            'type': 'object',
                            'description': 'Parámetros del trabajo'
                        }
                    },
                    'required': ['job_name', 'job_queue', 'job_definition']
                },
                'function': self.submit_batch_job
            },
            {
                'name': 'batch_terminate_job',
                'description': 'Termina un trabajo de AWS Batch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'job_id': {
                            'type': 'string',
                            'description': 'ID del trabajo a terminar'
                        },
                        'reason': {
                            'type': 'string',
                            'description': 'Razón para terminar el trabajo',
                            'default': 'Terminado por usuario'
                        }
                    },
                    'required': ['job_id']
                },
                'function': self.terminate_batch_job
            },
            {
                'name': 'batch_list_compute_environments',
                'description': 'Lista todos los entornos de computo de AWS Batch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'compute_environment_names': {
                            'type': 'array',
                            'description': 'Lista de nombres de entornos de computo para filtrar',
                            'items': {'type': 'string'}
                        },
                        'max_results': {
                            'type': 'integer',
                            'description': 'Número máximo de resultados'
                        }
                    }
                },
                'function': self.list_compute_environments
            },
            {
                'name': 'batch_create_compute_environment',
                'description': 'Crea un nuevo entorno de computo para AWS Batch',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'compute_environment_name': {
                            'type': 'string',
                            'description': 'Nombre del entorno de computo'
                        },
                        'type': {
                            'type': 'string',
                            'description': 'Tipo de entorno (MANAGED o UNMANAGED)',
                            'enum': ['MANAGED', 'UNMANAGED']
                        },
                        'state': {
                            'type': 'string',
                            'description': 'Estado del entorno',
                            'enum': ['ENABLED', 'DISABLED'],
                            'default': 'ENABLED'
                        },
                        'compute_resources': {
                            'type': 'object',
                            'description': 'Recursos de computo (solo para MANAGED)',
                            'properties': {
                                'instance_types': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'description': 'Tipos de instancia EC2'
                                },
                                'minv_cpus': {
                                    'type': 'integer',
                                    'description': 'Mínimo de vCPUs'
                                },
                                'maxv_cpus': {
                                    'type': 'integer',
                                    'description': 'Máximo de vCPUs'
                                },
                                'desiredv_cpus': {
                                    'type': 'integer',
                                    'description': 'vCPUs deseadas'
                                },
                                'subnets': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'description': 'IDs de subnets'
                                },
                                'security_group_ids': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'description': 'IDs de security groups'
                                }
                            }
                        }
                    },
                    'required': ['compute_environment_name', 'type']
                },
                'function': self.create_compute_environment
            }
        ]

    def list_batch_jobs(self, job_queue: Optional[str] = None, job_status: Optional[str] = None,
                       max_results: int = 100) -> Dict[str, Any]:
        """Lista trabajos de AWS Batch"""
        try:
            batch = self._get_batch_client()

            # Obtener todas las colas si no se especifica una
            if not job_queue:
                queues_response = batch.describe_job_queues()
                job_queues = [q['jobQueueName'] for q in queues_response.get('jobQueues', [])]
            else:
                job_queues = [job_queue]

            all_jobs = []

            # Obtener trabajos de cada cola
            for queue_name in job_queues:
                try:
                    # Obtener trabajos de diferentes estados
                    statuses = [job_status] if job_status else ['SUBMITTED', 'RUNNING', 'SUCCEEDED', 'FAILED']

                    for status in statuses:
                        response = batch.list_jobs(
                            jobQueue=queue_name,
                            jobStatus=status,
                            maxResults=min(max_results, 100)
                        )

                        for job in response.get('jobSummaryList', []):
                            job['queueName'] = queue_name
                            all_jobs.append(job)

                            if len(all_jobs) >= max_results:
                                break

                        if len(all_jobs) >= max_results:
                            break

                    if len(all_jobs) >= max_results:
                        break

                except Exception as e:
                    continue  # Continuar con la siguiente cola si hay error

            # Remover duplicados y ordenar
            unique_jobs = []
            seen_ids = set()
            for job in all_jobs:
                if job['jobId'] not in seen_ids:
                    unique_jobs.append(job)
                    seen_ids.add(job['jobId'])

            unique_jobs.sort(key=lambda x: x.get('createdAt', 0), reverse=True)

            return {
                'jobs': unique_jobs[:max_results],
                'total_count': len(unique_jobs),
                'message': f'Se encontraron {len(unique_jobs)} trabajos'
            }

        except Exception as e:
            return {
                'error': f'Error listando trabajos: {str(e)}',
                'jobs': [],
                'total_count': 0
            }

    def submit_batch_job(self, job_name: str, job_queue: str, job_definition: str,
                        container_overrides: Optional[Dict[str, Any]] = None,
                        parameters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Envía un nuevo trabajo de AWS Batch"""
        try:
            batch = self._get_batch_client()

            submit_params = {
                'jobName': job_name,
                'jobQueue': job_queue,
                'jobDefinition': job_definition
            }

            if container_overrides:
                submit_params['containerOverrides'] = container_overrides

            if parameters:
                submit_params['parameters'] = parameters

            response = batch.submit_job(**submit_params)

            return {
                'job_id': response['jobId'],
                'job_arn': response['jobArn'],
                'job_name': response['jobName'],
                'message': f'Trabajo {response["jobName"]} enviado exitosamente'
            }

        except Exception as e:
            return {
                'error': f'Error enviando trabajo: {str(e)}'
            }

    def terminate_batch_job(self, job_id: str, reason: str = 'Terminado por usuario') -> Dict[str, Any]:
        """Termina un trabajo de AWS Batch"""
        try:
            batch = self._get_batch_client()

            batch.terminate_job(
                jobId=job_id,
                reason=reason
            )

            return {
                'job_id': job_id,
                'message': f'Trabajo {job_id} terminado exitosamente',
                'reason': reason
            }

        except Exception as e:
            return {
                'error': f'Error terminando trabajo: {str(e)}',
                'job_id': job_id
            }

    def list_compute_environments(self, compute_environment_names: Optional[List[str]] = None,
                                max_results: Optional[int] = None) -> Dict[str, Any]:
        """Lista entornos de computo de AWS Batch"""
        try:
            batch = self._get_batch_client()

            params = {}
            if compute_environment_names:
                params['computeEnvironments'] = compute_environment_names
            if max_results:
                params['maxResults'] = max_results

            response = batch.describe_compute_environments(**params)

            compute_environments = []
            for ce in response.get('computeEnvironments', []):
                compute_environments.append({
                    'compute_environment_name': ce['computeEnvironmentName'],
                    'compute_environment_arn': ce['computeEnvironmentArn'],
                    'status': ce['status'],
                    'state': ce['state'],
                    'type': ce['type'],
                    'ecs_cluster_arn': ce.get('ecsClusterArn', ''),
                    'service_role': ce.get('serviceRole', ''),
                    'compute_resources': ce.get('computeResources', {})
                })

            return {
                'compute_environments': compute_environments,
                'total_count': len(compute_environments),
                'message': f'Se encontraron {len(compute_environments)} entornos de computo'
            }

        except Exception as e:
            return {
                'error': f'Error listando entornos de computo: {str(e)}',
                'compute_environments': [],
                'total_count': 0
            }

    def create_compute_environment(self, compute_environment_name: str, type: str,
                                 state: str = 'ENABLED',
                                 compute_resources: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crea un nuevo entorno de computo para AWS Batch"""
        try:
            batch = self._get_batch_client()

            create_params = {
                'computeEnvironmentName': compute_environment_name,
                'type': type,
                'state': state
            }

            if type == 'MANAGED' and compute_resources:
                create_params['computeResources'] = compute_resources

            response = batch.create_compute_environment(**create_params)

            return {
                'compute_environment_arn': response['computeEnvironmentArn'],
                'compute_environment_name': response['computeEnvironmentName'],
                'message': f'Entorno de computo {compute_environment_name} creado exitosamente'
            }

        except Exception as e:
            return {
                'error': f'Error creando entorno de computo: {str(e)}'
            }