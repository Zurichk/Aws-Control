"""
ECS MCP Tools for AWS Control
Provides Model Context Protocol tools for Amazon ECS operations
"""

import boto3
import json
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import os


class ECSTools:
    """ECS operations for MCP server"""

    def __init__(self):
        self.ecs_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ECS client"""
        try:
            self.ecs_client = boto3.client('ecs', region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
        except Exception as e:
            print(f"Error initializing ECS client: {e}")
            self.ecs_client = None

    def list_clusters(self) -> Dict[str, Any]:
        """List all ECS clusters"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            response = self.ecs_client.list_clusters()
            clusters = []

            if response.get('clusterArns'):
                # Get detailed cluster information
                describe_response = self.ecs_client.describe_clusters(
                    clusters=response['clusterArns']
                )

                for cluster in describe_response.get('clusters', []):
                    clusters.append({
                        'clusterName': cluster.get('clusterName'),
                        'clusterArn': cluster.get('clusterArn'),
                        'status': cluster.get('status'),
                        'registeredContainerInstancesCount': cluster.get('registeredContainerInstancesCount', 0),
                        'runningTasksCount': cluster.get('runningTasksCount', 0),
                        'pendingTasksCount': cluster.get('pendingTasksCount', 0),
                        'activeServicesCount': cluster.get('activeServicesCount', 0)
                    })

            return {
                "success": True,
                "clusters": clusters,
                "count": len(clusters)
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def create_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Create a new ECS cluster"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not cluster_name or not cluster_name.strip():
                return {"error": "Cluster name is required"}

            response = self.ecs_client.create_cluster(
                clusterName=cluster_name.strip()
            )

            cluster = response.get('cluster', {})
            return {
                "success": True,
                "message": f"Cluster '{cluster_name}' created successfully",
                "cluster": {
                    'clusterName': cluster.get('clusterName'),
                    'clusterArn': cluster.get('clusterArn'),
                    'status': cluster.get('status')
                }
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def delete_cluster(self, cluster_name: str) -> Dict[str, Any]:
        """Delete an ECS cluster"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not cluster_name or not cluster_name.strip():
                return {"error": "Cluster name is required"}

            # Check if cluster has running services or tasks
            describe_response = self.ecs_client.describe_clusters(
                clusters=[cluster_name.strip()]
            )

            if describe_response.get('clusters'):
                cluster = describe_response['clusters'][0]
                if cluster.get('activeServicesCount', 0) > 0:
                    return {"error": f"Cannot delete cluster '{cluster_name}' - it has {cluster['activeServicesCount']} active services"}
                if cluster.get('runningTasksCount', 0) > 0:
                    return {"error": f"Cannot delete cluster '{cluster_name}' - it has {cluster['runningTasksCount']} running tasks"}

            response = self.ecs_client.delete_cluster(
                cluster=cluster_name.strip()
            )

            return {
                "success": True,
                "message": f"Cluster '{cluster_name}' deleted successfully"
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def list_services(self, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """List ECS services"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            services = []

            if cluster_name:
                # List services in specific cluster
                response = self.ecs_client.list_services(
                    cluster=cluster_name
                )

                if response.get('serviceArns'):
                    describe_response = self.ecs_client.describe_services(
                        cluster=cluster_name,
                        services=response['serviceArns']
                    )

                    for service in describe_response.get('services', []):
                        services.append({
                            'serviceName': service.get('serviceName'),
                            'serviceArn': service.get('serviceArn'),
                            'clusterArn': service.get('clusterArn'),
                            'status': service.get('status'),
                            'desiredCount': service.get('desiredCount', 0),
                            'runningCount': service.get('runningCount', 0),
                            'pendingCount': service.get('pendingCount', 0),
                            'taskDefinition': service.get('taskDefinition'),
                            'createdAt': service.get('createdAt').isoformat() if service.get('createdAt') else None
                        })
            else:
                # List services across all clusters
                clusters_response = self.ecs_client.list_clusters()
                for cluster_arn in clusters_response.get('clusterArns', []):
                    cluster_services = self.list_services(cluster_arn.split('/')[-1])
                    if cluster_services.get('success'):
                        services.extend(cluster_services.get('services', []))

            return {
                "success": True,
                "services": services,
                "count": len(services)
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def create_service(self, cluster_name: str, service_name: str, task_definition: str, desired_count: int) -> Dict[str, Any]:
        """Create an ECS service"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not all([cluster_name, service_name, task_definition]):
                return {"error": "Cluster name, service name, and task definition are required"}

            if desired_count < 0:
                return {"error": "Desired count must be non-negative"}

            response = self.ecs_client.create_service(
                cluster=cluster_name,
                serviceName=service_name,
                taskDefinition=task_definition,
                desiredCount=desired_count
            )

            service = response.get('service', {})
            return {
                "success": True,
                "message": f"Service '{service_name}' created successfully in cluster '{cluster_name}'",
                "service": {
                    'serviceName': service.get('serviceName'),
                    'serviceArn': service.get('serviceArn'),
                    'status': service.get('status'),
                    'desiredCount': service.get('desiredCount'),
                    'runningCount': service.get('runningCount')
                }
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def update_service(self, cluster_name: str, service_name: str, desired_count: int, task_definition: Optional[str] = None) -> Dict[str, Any]:
        """Update an ECS service"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not all([cluster_name, service_name]):
                return {"error": "Cluster name and service name are required"}

            if desired_count < 0:
                return {"error": "Desired count must be non-negative"}

            update_params = {
                'cluster': cluster_name,
                'service': service_name,
                'desiredCount': desired_count
            }

            if task_definition:
                update_params['taskDefinition'] = task_definition

            response = self.ecs_client.update_service(**update_params)

            service = response.get('service', {})
            return {
                "success": True,
                "message": f"Service '{service_name}' updated successfully",
                "service": {
                    'serviceName': service.get('serviceName'),
                    'desiredCount': service.get('desiredCount'),
                    'runningCount': service.get('runningCount'),
                    'taskDefinition': service.get('taskDefinition')
                }
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def delete_service(self, cluster_name: str, service_name: str) -> Dict[str, Any]:
        """Delete an ECS service"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not all([cluster_name, service_name]):
                return {"error": "Cluster name and service name are required"}

            # First, set desired count to 0
            self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=0
            )

            # Then delete the service
            response = self.ecs_client.delete_service(
                cluster=cluster_name,
                service=service_name
            )

            return {
                "success": True,
                "message": f"Service '{service_name}' deletion initiated in cluster '{cluster_name}'"
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def list_tasks(self, cluster_name: Optional[str] = None) -> Dict[str, Any]:
        """List ECS tasks"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            tasks = []

            if cluster_name:
                response = self.ecs_client.list_tasks(
                    cluster=cluster_name
                )

                if response.get('taskArns'):
                    describe_response = self.ecs_client.describe_tasks(
                        cluster=cluster_name,
                        tasks=response['taskArns']
                    )

                    for task in describe_response.get('tasks', []):
                        tasks.append({
                            'taskArn': task.get('taskArn'),
                            'clusterArn': task.get('clusterArn'),
                            'taskDefinitionArn': task.get('taskDefinitionArn'),
                            'lastStatus': task.get('lastStatus'),
                            'desiredStatus': task.get('desiredStatus'),
                            'createdAt': task.get('createdAt').isoformat() if task.get('createdAt') else None,
                            'startedAt': task.get('startedAt').isoformat() if task.get('startedAt') else None,
                            'stoppedAt': task.get('stoppedAt').isoformat() if task.get('stoppedAt') else None
                        })
            else:
                # List tasks across all clusters
                clusters_response = self.ecs_client.list_clusters()
                for cluster_arn in clusters_response.get('clusterArns', []):
                    cluster_tasks = self.list_tasks(cluster_arn.split('/')[-1])
                    if cluster_tasks.get('success'):
                        tasks.extend(cluster_tasks.get('tasks', []))

            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def run_task(self, cluster_name: str, task_definition: str, count: int = 1, launch_type: str = 'FARGATE') -> Dict[str, Any]:
        """Run an ECS task"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not all([cluster_name, task_definition]):
                return {"error": "Cluster name and task definition are required"}

            if count < 1 or count > 10:
                return {"error": "Count must be between 1 and 10"}

            response = self.ecs_client.run_task(
                cluster=cluster_name,
                taskDefinition=task_definition,
                count=count,
                launchType=launch_type
            )

            tasks = response.get('tasks', [])
            failures = response.get('failures', [])

            return {
                "success": True,
                "message": f"Started {len(tasks)} task(s) in cluster '{cluster_name}'",
                "tasks": [{
                    'taskArn': task.get('taskArn'),
                    'lastStatus': task.get('lastStatus'),
                    'desiredStatus': task.get('desiredStatus')
                } for task in tasks],
                "failures": failures
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def stop_task(self, cluster_name: str, task_arn: str) -> Dict[str, Any]:
        """Stop an ECS task"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not all([cluster_name, task_arn]):
                return {"error": "Cluster name and task ARN are required"}

            response = self.ecs_client.stop_task(
                cluster=cluster_name,
                task=task_arn
            )

            task = response.get('task', {})
            return {
                "success": True,
                "message": f"Task stopped successfully",
                "task": {
                    'taskArn': task.get('taskArn'),
                    'lastStatus': task.get('lastStatus'),
                    'stoppedAt': task.get('stoppedAt').isoformat() if task.get('stoppedAt') else None
                }
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def list_task_definitions(self) -> Dict[str, Any]:
        """List ECS task definitions"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            response = self.ecs_client.list_task_definitions()

            task_definitions = []

            if response.get('taskDefinitionArns'):
                # Get detailed task definition information
                for arn in response['taskDefinitionArns'][:10]:  # Limit to latest 10
                    describe_response = self.ecs_client.describe_task_definition(
                        taskDefinition=arn
                    )

                    task_def = describe_response.get('taskDefinition', {})
                    task_definitions.append({
                        'taskDefinitionArn': task_def.get('taskDefinitionArn'),
                        'family': task_def.get('family'),
                        'revision': task_def.get('revision'),
                        'status': task_def.get('status'),
                        'cpu': task_def.get('cpu'),
                        'memory': task_def.get('memory'),
                        'containerDefinitions': len(task_def.get('containerDefinitions', [])),
                        'registeredAt': task_def.get('registeredAt').isoformat() if task_def.get('registeredAt') else None
                    })

            # Sort by family and revision (latest first)
            task_definitions.sort(key=lambda x: (x['family'], x['revision']), reverse=True)

            return {
                "success": True,
                "taskDefinitions": task_definitions,
                "count": len(task_definitions)
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def register_task_definition(self, family: str, container_definitions: List[Dict], cpu: Optional[str] = None, memory: Optional[str] = None) -> Dict[str, Any]:
        """Register a new ECS task definition"""
        try:
            if not self.ecs_client:
                return {"error": "ECS client not initialized"}

            if not family or not container_definitions:
                return {"error": "Family and container definitions are required"}

            task_def_params = {
                'family': family,
                'containerDefinitions': container_definitions
            }

            if cpu:
                task_def_params['cpu'] = cpu
            if memory:
                task_def_params['memory'] = memory

            response = self.ecs_client.register_task_definition(**task_def_params)

            task_def = response.get('taskDefinition', {})
            return {
                "success": True,
                "message": f"Task definition '{family}:{task_def.get('revision')}' registered successfully",
                "taskDefinition": {
                    'taskDefinitionArn': task_def.get('taskDefinitionArn'),
                    'family': task_def.get('family'),
                    'revision': task_def.get('revision'),
                    'status': task_def.get('status')
                }
            }

        except ClientError as e:
            return {"error": f"AWS API Error: {e.response['Error']['Message']}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


# Global ECS tools instance
ecs_tools = ECSTools()


# MCP Tool wrapper functions
def get_ecs_clusters() -> str:
    """Get all ECS clusters"""
    result = ecs_tools.list_clusters()
    return json.dumps(result, indent=2, default=str)


def create_ecs_cluster(cluster_name: str) -> str:
    """Create a new ECS cluster"""
    result = ecs_tools.create_cluster(cluster_name)
    return json.dumps(result, indent=2, default=str)


def delete_ecs_cluster(cluster_name: str) -> str:
    """Delete an ECS cluster"""
    result = ecs_tools.delete_cluster(cluster_name)
    return json.dumps(result, indent=2, default=str)


def get_ecs_services(cluster_name: str = None) -> str:
    """Get ECS services, optionally filtered by cluster"""
    result = ecs_tools.list_services(cluster_name)
    return json.dumps(result, indent=2, default=str)


def create_ecs_service(cluster_name: str, service_name: str, task_definition: str, desired_count: int) -> str:
    """Create a new ECS service"""
    result = ecs_tools.create_service(cluster_name, service_name, task_definition, desired_count)
    return json.dumps(result, indent=2, default=str)


def update_ecs_service(cluster_name: str, service_name: str, desired_count: int, task_definition: str = None) -> str:
    """Update an ECS service"""
    result = ecs_tools.update_service(cluster_name, service_name, desired_count, task_definition)
    return json.dumps(result, indent=2, default=str)


def delete_ecs_service(cluster_name: str, service_name: str) -> str:
    """Delete an ECS service"""
    result = ecs_tools.delete_service(cluster_name, service_name)
    return json.dumps(result, indent=2, default=str)


def get_ecs_tasks(cluster_name: str = None) -> str:
    """Get ECS tasks, optionally filtered by cluster"""
    result = ecs_tools.list_tasks(cluster_name)
    return json.dumps(result, indent=2, default=str)


def run_ecs_task(cluster_name: str, task_definition: str, count: int = 1, launch_type: str = 'FARGATE') -> str:
    """Run an ECS task"""
    result = ecs_tools.run_task(cluster_name, task_definition, count, launch_type)
    return json.dumps(result, indent=2, default=str)


def stop_ecs_task(cluster_name: str, task_arn: str) -> str:
    """Stop an ECS task"""
    result = ecs_tools.stop_task(cluster_name, task_arn)
    return json.dumps(result, indent=2, default=str)


def get_ecs_task_definitions() -> str:
    """Get all ECS task definitions"""
    result = ecs_tools.list_task_definitions()
    return json.dumps(result, indent=2, default=str)


def register_ecs_task_definition(family: str, container_name: str, image: str, cpu: str = None, memory: str = None) -> str:
    """Register a new ECS task definition with a single container"""
    container_definitions = [{
        'name': container_name,
        'image': image,
        'essential': True
    }]

    result = ecs_tools.register_task_definition(family, container_definitions, cpu, memory)
    return json.dumps(result, indent=2, default=str)


# MCP Tool definitions for external access
ECS_MCP_TOOLS = {
    'get_ecs_clusters': {
        'function': get_ecs_clusters,
        'description': 'List all ECS clusters in the account',
        'parameters': {}
    },
    'create_ecs_cluster': {
        'function': create_ecs_cluster,
        'description': 'Create a new ECS cluster',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster to create'}
        }
    },
    'delete_ecs_cluster': {
        'function': delete_ecs_cluster,
        'description': 'Delete an ECS cluster (must be empty)',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster to delete'}
        }
    },
    'get_ecs_services': {
        'function': get_ecs_services,
        'description': 'List ECS services, optionally filtered by cluster',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Optional cluster name to filter services', 'required': False}
        }
    },
    'create_ecs_service': {
        'function': create_ecs_service,
        'description': 'Create a new ECS service',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster'},
            'service_name': {'type': 'string', 'description': 'Name of the service'},
            'task_definition': {'type': 'string', 'description': 'Task definition ARN or family:revision'},
            'desired_count': {'type': 'integer', 'description': 'Desired number of tasks'}
        }
    },
    'update_ecs_service': {
        'function': update_ecs_service,
        'description': 'Update an ECS service',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster'},
            'service_name': {'type': 'string', 'description': 'Name of the service'},
            'desired_count': {'type': 'integer', 'description': 'New desired number of tasks'},
            'task_definition': {'type': 'string', 'description': 'Optional new task definition ARN', 'required': False}
        }
    },
    'delete_ecs_service': {
        'function': delete_ecs_service,
        'description': 'Delete an ECS service',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster'},
            'service_name': {'type': 'string', 'description': 'Name of the service'}
        }
    },
    'get_ecs_tasks': {
        'function': get_ecs_tasks,
        'description': 'List ECS tasks, optionally filtered by cluster',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Optional cluster name to filter tasks', 'required': False}
        }
    },
    'run_ecs_task': {
        'function': run_ecs_task,
        'description': 'Run an ECS task',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster'},
            'task_definition': {'type': 'string', 'description': 'Task definition ARN or family:revision'},
            'count': {'type': 'integer', 'description': 'Number of tasks to run (1-10)', 'default': 1},
            'launch_type': {'type': 'string', 'description': 'Launch type (FARGATE or EC2)', 'default': 'FARGATE'}
        }
    },
    'stop_ecs_task': {
        'function': stop_ecs_task,
        'description': 'Stop an ECS task',
        'parameters': {
            'cluster_name': {'type': 'string', 'description': 'Name of the cluster'},
            'task_arn': {'type': 'string', 'description': 'ARN of the task to stop'}
        }
    },
    'get_ecs_task_definitions': {
        'function': get_ecs_task_definitions,
        'description': 'List all ECS task definitions',
        'parameters': {}
    },
    'register_ecs_task_definition': {
        'function': register_ecs_task_definition,
        'description': 'Register a new ECS task definition',
        'parameters': {
            'family': {'type': 'string', 'description': 'Family name for the task definition'},
            'container_name': {'type': 'string', 'description': 'Name of the container'},
            'image': {'type': 'string', 'description': 'Docker image for the container'},
            'cpu': {'type': 'string', 'description': 'CPU units for FARGATE', 'required': False},
            'memory': {'type': 'string', 'description': 'Memory in MB for FARGATE', 'required': False}
        }
    }
}