import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import json
import logging

logger = logging.getLogger(__name__)


class SageMakerMCPTools:
    """
    MCP tools for Amazon SageMaker management.
    Provides comprehensive machine learning model training and deployment operations.
    """

    def __init__(self):
        self.client = boto3.client('sagemaker')

    def list_notebook_instances(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all SageMaker notebook instances.

        Args:
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of notebook instances
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.list_notebook_instances()

            return {
                'success': True,
                'notebook_instances': response.get('NotebookInstances', []),
                'count': len(response.get('NotebookInstances', [])),
                'region': region or 'default'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def describe_notebook_instance(self, notebook_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a SageMaker notebook instance.

        Args:
            notebook_name: Name of the notebook instance
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing detailed notebook instance information
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.describe_notebook_instance(NotebookInstanceName=notebook_name)

            return {
                'success': True,
                'notebook_instance': response
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def create_notebook_instance(self, notebook_name: str, instance_type: str = 'ml.t2.medium',
                               role_arn: str = None, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new SageMaker notebook instance.

        Args:
            notebook_name: Name of the notebook instance to create
            instance_type: EC2 instance type (default: ml.t2.medium)
            role_arn: ARN of the IAM role for the notebook
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing notebook instance creation status
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            if not role_arn:
                # Try to use a default SageMaker role
                role_arn = 'arn:aws:iam::123456789012:role/SageMakerRole'  # This should be configured properly

            response = client.create_notebook_instance(
                NotebookInstanceName=notebook_name,
                InstanceType=instance_type,
                RoleArn=role_arn
            )

            return {
                'success': True,
                'notebook_name': notebook_name,
                'status': 'InService',  # Notebooks start in InService state
                'message': f'SageMaker notebook instance {notebook_name} created successfully'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def stop_notebook_instance(self, notebook_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a SageMaker notebook instance.

        Args:
            notebook_name: Name of the notebook instance to stop
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing stop operation status
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            client.stop_notebook_instance(NotebookInstanceName=notebook_name)

            return {
                'success': True,
                'notebook_name': notebook_name,
                'status': 'Stopping',
                'message': f'SageMaker notebook instance {notebook_name} stop initiated'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def start_notebook_instance(self, notebook_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a SageMaker notebook instance.

        Args:
            notebook_name: Name of the notebook instance to start
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing start operation status
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            client.start_notebook_instance(NotebookInstanceName=notebook_name)

            return {
                'success': True,
                'notebook_name': notebook_name,
                'status': 'Starting',
                'message': f'SageMaker notebook instance {notebook_name} start initiated'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def delete_notebook_instance(self, notebook_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a SageMaker notebook instance.

        Args:
            notebook_name: Name of the notebook instance to delete
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing deletion status
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            client.delete_notebook_instance(NotebookInstanceName=notebook_name)

            return {
                'success': True,
                'notebook_name': notebook_name,
                'message': f'SageMaker notebook instance {notebook_name} deletion initiated'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def list_training_jobs(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all SageMaker training jobs.

        Args:
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of training jobs
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.list_training_jobs()

            return {
                'success': True,
                'training_jobs': response.get('TrainingJobSummaries', []),
                'count': len(response.get('TrainingJobSummaries', [])),
                'region': region or 'default'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def create_training_job(self, job_name: str, algorithm_specification: Dict[str, Any],
                          input_data_config: List[Dict[str, Any]], output_data_config: Dict[str, Any],
                          resource_config: Dict[str, Any], role_arn: str,
                          stopping_condition: Dict[str, Any], region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a SageMaker training job.

        Args:
            job_name: Name of the training job
            algorithm_specification: Algorithm specification
            input_data_config: Input data configuration
            output_data_config: Output data configuration
            resource_config: Resource configuration
            role_arn: ARN of the IAM role
            stopping_condition: Stopping condition
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing training job creation status
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.create_training_job(
                TrainingJobName=job_name,
                AlgorithmSpecification=algorithm_specification,
                InputDataConfig=input_data_config,
                OutputDataConfig=output_data_config,
                ResourceConfig=resource_config,
                RoleArn=role_arn,
                StoppingCondition=stopping_condition
            )

            return {
                'success': True,
                'training_job_arn': response.get('TrainingJobArn'),
                'message': f'SageMaker training job {job_name} created successfully'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def list_endpoints(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all SageMaker endpoints.

        Args:
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of endpoints
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.list_endpoints()

            return {
                'success': True,
                'endpoints': response.get('Endpoints', []),
                'count': len(response.get('Endpoints', [])),
                'region': region or 'default'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def create_endpoint(self, endpoint_name: str, endpoint_config_name: str,
                       region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a SageMaker endpoint.

        Args:
            endpoint_name: Name for the endpoint
            endpoint_config_name: Name of the endpoint configuration
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing endpoint creation result
        """
        try:
            if region:
                client = boto3.client('sagemaker', region_name=region)
            else:
                client = self.client

            response = client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )

            return {
                'success': True,
                'endpoint_arn': response.get('EndpointArn'),
                'message': f'SageMaker endpoint {endpoint_name} created successfully'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def invoke_endpoint(self, endpoint_name: str, input_data: str,
                       content_type: str = 'application/json', region: Optional[str] = None) -> Dict[str, Any]:
        """
        Invoke a SageMaker endpoint for inference.

        Args:
            endpoint_name: Name of the endpoint to invoke
            input_data: Input data for the model (JSON string)
            content_type: Content type of the input data
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing inference result
        """
        try:
            if region:
                runtime_client = boto3.client('sagemaker-runtime', region_name=region)
            else:
                runtime_client = boto3.client('sagemaker-runtime')

            response = runtime_client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType=content_type,
                Body=input_data
            )

            # Read the response
            result = response['Body'].read().decode('utf-8')

            return {
                'success': True,
                'result': result,
                'content_type': response.get('ContentType', 'unknown'),
                'message': f'Endpoint {endpoint_name} invoked successfully'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS ClientError: {str(e)}',
                'error_code': e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except BotoCoreError as e:
            return {
                'success': False,
                'error': f'BotoCore Error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of available SageMaker MCP tools"""
        return [
            {
                'name': 'sagemaker_list_notebook_instances',
                'description': 'List all SageMaker notebook instances',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.list_notebook_instances
            },
            {
                'name': 'sagemaker_describe_notebook_instance',
                'description': 'Get detailed information about a specific SageMaker notebook instance',
                'parameters': {
                    'type': 'object',
                    'required': ['notebook_instance_name'],
                    'properties': {
                        'notebook_instance_name': {
                            'type': 'string',
                            'description': 'Name of the notebook instance'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.describe_notebook_instance
            },
            {
                'name': 'sagemaker_create_notebook_instance',
                'description': 'Create a new SageMaker notebook instance',
                'parameters': {
                    'type': 'object',
                    'required': ['notebook_instance_name', 'instance_type', 'role_arn'],
                    'properties': {
                        'notebook_instance_name': {
                            'type': 'string',
                            'description': 'Name for the notebook instance'
                        },
                        'instance_type': {
                            'type': 'string',
                            'description': 'Instance type (e.g., ml.t2.medium)'
                        },
                        'role_arn': {
                            'type': 'string',
                            'description': 'ARN of the IAM role'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.create_notebook_instance
            },
            {
                'name': 'sagemaker_start_notebook_instance',
                'description': 'Start a SageMaker notebook instance',
                'parameters': {
                    'type': 'object',
                    'required': ['notebook_instance_name'],
                    'properties': {
                        'notebook_instance_name': {
                            'type': 'string',
                            'description': 'Name of the notebook instance'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.start_notebook_instance
            },
            {
                'name': 'sagemaker_stop_notebook_instance',
                'description': 'Stop a SageMaker notebook instance',
                'parameters': {
                    'type': 'object',
                    'required': ['notebook_instance_name'],
                    'properties': {
                        'notebook_instance_name': {
                            'type': 'string',
                            'description': 'Name of the notebook instance'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.stop_notebook_instance
            },
            {
                'name': 'sagemaker_delete_notebook_instance',
                'description': 'Delete a SageMaker notebook instance',
                'parameters': {
                    'type': 'object',
                    'required': ['notebook_instance_name'],
                    'properties': {
                        'notebook_instance_name': {
                            'type': 'string',
                            'description': 'Name of the notebook instance'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.delete_notebook_instance
            },
            {
                'name': 'sagemaker_list_training_jobs',
                'description': 'List SageMaker training jobs',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.list_training_jobs
            },
            {
                'name': 'sagemaker_create_training_job',
                'description': 'Create a SageMaker training job',
                'parameters': {
                    'type': 'object',
                    'required': ['job_name', 'algorithm_specification', 'input_data_config', 'output_data_config', 'resource_config', 'role_arn', 'stopping_condition'],
                    'properties': {
                        'job_name': {
                            'type': 'string',
                            'description': 'Name for the training job'
                        },
                        'algorithm_specification': {
                            'type': 'object',
                            'description': 'Algorithm specification'
                        },
                        'input_data_config': {
                            'type': 'array',
                            'description': 'Input data configuration'
                        },
                        'output_data_config': {
                            'type': 'object',
                            'description': 'Output data configuration'
                        },
                        'resource_config': {
                            'type': 'object',
                            'description': 'Resource configuration'
                        },
                        'role_arn': {
                            'type': 'string',
                            'description': 'ARN of the IAM role'
                        },
                        'stopping_condition': {
                            'type': 'object',
                            'description': 'Stopping condition'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.create_training_job
            },
            {
                'name': 'sagemaker_list_endpoints',
                'description': 'List all SageMaker endpoints',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.list_endpoints
            },
            {
                'name': 'sagemaker_create_endpoint',
                'description': 'Create a SageMaker endpoint for model deployment',
                'parameters': {
                    'type': 'object',
                    'required': ['endpoint_name', 'endpoint_config_name'],
                    'properties': {
                        'endpoint_name': {
                            'type': 'string',
                            'description': 'Name for the endpoint'
                        },
                        'endpoint_config_name': {
                            'type': 'string',
                            'description': 'Name of the endpoint configuration'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.create_endpoint
            },
            {
                'name': 'sagemaker_invoke_endpoint',
                'description': 'Invoke a SageMaker endpoint for inference',
                'parameters': {
                    'type': 'object',
                    'required': ['endpoint_name', 'input_data'],
                    'properties': {
                        'endpoint_name': {
                            'type': 'string',
                            'description': 'Name of the endpoint to invoke'
                        },
                        'input_data': {
                            'type': 'string',
                            'description': 'Input data for the model (JSON string)'
                        },
                        'content_type': {
                            'type': 'string',
                            'description': 'Content type of the input data',
                            'default': 'application/json'
                        },
                        'region': {
                            'type': 'string',
                            'description': 'AWS region name (optional)'
                        }
                    }
                },
                'function': self.invoke_endpoint
            }
        ]