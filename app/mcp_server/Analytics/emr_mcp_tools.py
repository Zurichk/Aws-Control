import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError, NoRegionError
import json
import logging

logger = logging.getLogger(__name__)


class EMRMCPTools:
    """
    MCP tools for Amazon Elastic MapReduce (EMR) management.
    Provides comprehensive cluster operations for big data processing.
    """

    def __init__(self):
        try:
            self.client = boto3.client('emr')
        except NoRegionError:
            self.client = boto3.client('emr', region_name='us-east-1')

    def list_emr_clusters(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all EMR clusters in the specified region.

        Args:
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of EMR clusters with their details
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            response = client.list_clusters()
            clusters = response.get('Clusters', [])

            # Get detailed information for each cluster
            detailed_clusters = []
            for cluster in clusters:
                try:
                    cluster_detail = client.describe_cluster(ClusterId=cluster['Id'])
                    detailed_clusters.append(cluster_detail['Cluster'])
                except ClientError as e:
                    logger.error(f"Error getting cluster details for {cluster['Id']}: {e}")
                    detailed_clusters.append(cluster)

            return {
                'success': True,
                'clusters': detailed_clusters,
                'cluster_count': len(detailed_clusters),
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

    def describe_emr_cluster(self, cluster_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific EMR cluster.

        Args:
            cluster_id: ID of the EMR cluster
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing detailed cluster information
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            response = client.describe_cluster(ClusterId=cluster_id)
            cluster = response.get('Cluster', {})

            return {
                'success': True,
                'cluster': {
                    'Id': cluster.get('Id'),
                    'Name': cluster.get('Name'),
                    'Status': cluster.get('Status', {}),
                    'Ec2InstanceAttributes': cluster.get('Ec2InstanceAttributes', {}),
                    'InstanceGroups': cluster.get('InstanceGroups', []),
                    'MasterPublicDnsName': cluster.get('MasterPublicDnsName'),
                    'ReleaseLabel': cluster.get('ReleaseLabel'),
                    'ServiceRole': cluster.get('ServiceRole'),
                    'AutoTerminate': cluster.get('AutoTerminate'),
                    'TerminationProtected': cluster.get('TerminationProtected'),
                    'Applications': cluster.get('Applications', []),
                    'Tags': cluster.get('Tags', [])
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

    def create_emr_cluster(self, cluster_name: str, instance_count: int = 3,
                          instance_type: str = 'm5.xlarge', release_label: str = 'emr-6.4.0',
                          region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new EMR cluster.

        Args:
            cluster_name: Name of the EMR cluster
            instance_count: Number of EC2 instances (default: 3)
            instance_type: EC2 instance type (default: m5.xlarge)
            release_label: EMR release version (default: emr-6.4.0)
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing cluster creation status
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            if not cluster_name:
                return {
                    'success': False,
                    'error': 'Cluster name is required'
                }

            # Create the cluster
            response = client.run_job_flow(
                Name=cluster_name,
                ReleaseLabel=release_label,
                Instances={
                    'MasterInstanceType': instance_type,
                    'SlaveInstanceType': instance_type,
                    'InstanceCount': instance_count,
                    'KeepJobFlowAliveWhenNoSteps': True,
                    'TerminationProtected': False
                },
                ServiceRole='EMR_DefaultRole',
                JobFlowRole='EMR_EC2_DefaultRole',
                Steps=[]
            )

            cluster_id = response['JobFlowId']

            return {
                'success': True,
                'cluster_id': cluster_id,
                'cluster_name': cluster_name,
                'status': 'CREATED',
                'message': f'EMR cluster {cluster_name} creation initiated'
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

    def terminate_emr_cluster(self, cluster_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Terminate an EMR cluster.

        Args:
            cluster_id: ID of the EMR cluster to terminate
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing termination status
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            if not cluster_id:
                return {
                    'success': False,
                    'error': 'Cluster ID is required'
                }

            # Terminate the cluster
            client.terminate_job_flows(JobFlowIds=[cluster_id])

            return {
                'success': True,
                'cluster_id': cluster_id,
                'status': 'TERMINATION_INITIATED',
                'message': f'EMR cluster {cluster_id} termination initiated'
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

    def add_emr_steps(self, cluster_id: str, steps: List[Dict[str, Any]], region: Optional[str] = None) -> Dict[str, Any]:
        """
        Add steps to a running EMR cluster.

        Args:
            cluster_id: ID of the EMR cluster
            steps: List of step configurations to add
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing step addition status
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            if not cluster_id:
                return {
                    'success': False,
                    'error': 'Cluster ID is required'
                }

            if not steps:
                return {
                    'success': False,
                    'error': 'Steps configuration is required'
                }

            response = client.add_job_flow_steps(
                JobFlowId=cluster_id,
                Steps=steps
            )

            return {
                'success': True,
                'cluster_id': cluster_id,
                'step_ids': response.get('StepIds', []),
                'message': f'Added {len(steps)} steps to EMR cluster {cluster_id}'
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

    def list_emr_steps(self, cluster_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List all steps for a specific EMR cluster.

        Args:
            cluster_id: ID of the EMR cluster
            region: AWS region name (optional, uses default if not specified)

        Returns:
            Dict containing list of cluster steps
        """
        try:
            if region:
                client = boto3.client('emr', region_name=region)
            else:
                client = self.client

            response = client.list_steps(ClusterId=cluster_id)
            steps = response.get('Steps', [])

            return {
                'success': True,
                'cluster_id': cluster_id,
                'steps': steps,
                'step_count': len(steps)
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