import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import json


class EKSMCPTools:
    """
    MCP tools for Amazon Elastic Kubernetes Service (EKS) management.
    Provides comprehensive cluster and node group operations.
    """

    def __init__(self):
        self.client = boto3.client('eks')

    def list_eks_clusters(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all EKS clusters in the specified region.

        Args:
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of cluster names and metadata
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.list_clusters()

            return {
                'success': True,
                'clusters': response.get('clusters', []),
                'cluster_count': len(response.get('clusters', [])),
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

    def describe_eks_cluster(self, cluster_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific EKS cluster.

        Args:
            cluster_name: Name of the EKS cluster
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing detailed cluster information
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.describe_cluster(name=cluster_name)

            cluster = response.get('cluster', {})

            return {
                'success': True,
                'cluster': {
                    'name': cluster.get('name'),
                    'arn': cluster.get('arn'),
                    'status': cluster.get('status'),
                    'version': cluster.get('version'),
                    'platformVersion': cluster.get('platformVersion'),
                    'endpoint': cluster.get('endpoint'),
                    'roleArn': cluster.get('roleArn'),
                    'vpcConfig': cluster.get('vpcConfig', {}),
                    'kubernetesNetworkConfig': cluster.get('kubernetesNetworkConfig', {}),
                    'logging': cluster.get('logging', {}),
                    'createdAt': cluster.get('createdAt').isoformat() if cluster.get('createdAt') else None,
                    'tags': cluster.get('tags', {})
                }
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

    def create_eks_cluster(self, cluster_name: str, role_arn: str, vpc_config: Dict[str, Any],
                          kubernetes_version: str = '1.28', region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new EKS cluster.

        Args:
            cluster_name: Name of the cluster to create
            role_arn: ARN of the IAM role for the cluster
            vpc_config: VPC configuration with subnets and security groups
            kubernetes_version: Kubernetes version (default: 1.28)
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing cluster creation status
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            # Prepare cluster configuration
            cluster_config = {
                'name': cluster_name,
                'version': kubernetes_version,
                'roleArn': role_arn,
                'resourcesVpcConfig': vpc_config,
                'logging': {
                    'clusterLogging': [
                        {
                            'types': ['api', 'audit', 'authenticator', 'controllerManager', 'scheduler'],
                            'enabled': True
                        }
                    ]
                }
            }

            response = client.create_cluster(**cluster_config)

            return {
                'success': True,
                'cluster': {
                    'name': response.get('cluster', {}).get('name'),
                    'arn': response.get('cluster', {}).get('arn'),
                    'status': response.get('cluster', {}).get('status'),
                    'createdAt': response.get('cluster', {}).get('createdAt').isoformat() if response.get('cluster', {}).get('createdAt') else None
                },
                'message': f'EKS cluster {cluster_name} creation initiated'
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

    def delete_eks_cluster(self, cluster_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an EKS cluster.

        Args:
            cluster_name: Name of the cluster to delete
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing deletion status
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.delete_cluster(name=cluster_name)

            return {
                'success': True,
                'cluster_name': cluster_name,
                'message': f'EKS cluster {cluster_name} deletion initiated'
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

    def list_node_groups(self, cluster_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all node groups for a specific EKS cluster.

        Args:
            cluster_name: Name of the EKS cluster
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of node groups
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.list_nodegroups(clusterName=cluster_name)

            return {
                'success': True,
                'cluster_name': cluster_name,
                'nodegroups': response.get('nodegroups', []),
                'nodegroup_count': len(response.get('nodegroups', []))
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

    def describe_node_group(self, cluster_name: str, nodegroup_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific node group.

        Args:
            cluster_name: Name of the EKS cluster
            nodegroup_name: Name of the node group
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing detailed node group information
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )

            nodegroup = response.get('nodegroup', {})

            return {
                'success': True,
                'nodegroup': {
                    'clusterName': nodegroup.get('clusterName'),
                    'nodegroupName': nodegroup.get('nodegroupName'),
                    'status': nodegroup.get('status'),
                    'instanceTypes': nodegroup.get('instanceTypes', []),
                    'amiType': nodegroup.get('amiType'),
                    'nodeRole': nodegroup.get('nodeRole'),
                    'subnets': nodegroup.get('subnets', []),
                    'scalingConfig': nodegroup.get('scalingConfig', {}),
                    'createdAt': nodegroup.get('createdAt').isoformat() if nodegroup.get('createdAt') else None,
                    'modifiedAt': nodegroup.get('modifiedAt').isoformat() if nodegroup.get('modifiedAt') else None,
                    'tags': nodegroup.get('tags', {})
                }
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

    def create_node_group(self, cluster_name: str, nodegroup_name: str, node_role_arn: str,
                         subnets: List[str], instance_types: List[str] = None,
                         scaling_config: Dict[str, int] = None, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new node group for an EKS cluster.

        Args:
            cluster_name: Name of the EKS cluster
            nodegroup_name: Name of the node group to create
            node_role_arn: ARN of the IAM role for the node group
            subnets: List of subnet IDs for the node group
            instance_types: List of EC2 instance types (optional, defaults to t3.medium)
            scaling_config: Scaling configuration with min, max, desired sizes
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing node group creation status
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            # Set defaults
            if instance_types is None:
                instance_types = ['t3.medium']

            if scaling_config is None:
                scaling_config = {
                    'minSize': 1,
                    'maxSize': 3,
                    'desiredSize': 2
                }

            # Prepare node group configuration
            nodegroup_config = {
                'clusterName': cluster_name,
                'nodegroupName': nodegroup_name,
                'nodeRole': node_role_arn,
                'subnets': subnets,
                'instanceTypes': instance_types,
                'scalingConfig': scaling_config,
                'amiType': 'AL2_x86_64'  # Amazon Linux 2
            }

            response = client.create_nodegroup(**nodegroup_config)

            return {
                'success': True,
                'nodegroup': {
                    'clusterName': response.get('nodegroup', {}).get('clusterName'),
                    'nodegroupName': response.get('nodegroup', {}).get('nodegroupName'),
                    'status': response.get('nodegroup', {}).get('status'),
                    'createdAt': response.get('nodegroup', {}).get('createdAt').isoformat() if response.get('nodegroup', {}).get('createdAt') else None
                },
                'message': f'Node group {nodegroup_name} creation initiated for cluster {cluster_name}'
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

    def delete_node_group(self, cluster_name: str, nodegroup_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a node group from an EKS cluster.

        Args:
            cluster_name: Name of the EKS cluster
            nodegroup_name: Name of the node group to delete
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing deletion status
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.delete_nodegroup(
                clusterName=cluster_name,
                nodegroupName=nodegroup_name
            )

            return {
                'success': True,
                'cluster_name': cluster_name,
                'nodegroup_name': nodegroup_name,
                'message': f'Node group {nodegroup_name} deletion initiated from cluster {cluster_name}'
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

    def update_cluster_version(self, cluster_name: str, version: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the Kubernetes version of an EKS cluster.

        Args:
            cluster_name: Name of the EKS cluster
            version: Target Kubernetes version (e.g., '1.29')
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing update status
        """
        try:
            if region:
                client = boto3.client('eks', region_name=region)
            else:
                client = self.client

            response = client.update_cluster_version(
                name=cluster_name,
                version=version
            )

            return {
                'success': True,
                'cluster_name': cluster_name,
                'target_version': version,
                'update_id': response.get('update', {}).get('id'),
                'status': response.get('update', {}).get('status'),
                'message': f'Cluster {cluster_name} version update to {version} initiated'
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