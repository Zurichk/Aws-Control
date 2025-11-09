import boto3
from botocore.exceptions import ClientError
import json
import logging

logger = logging.getLogger(__name__)

def get_emr_client():
    """Get EMR client with error handling"""
    try:
        return boto3.client('emr', region_name='us-east-1')
    except Exception as e:
        logger.error(f"Error creating EMR client: {e}")
        return None

def list_emr_clusters():
    """
    List all EMR clusters in the account.

    Returns:
        dict: Dictionary containing list of EMR clusters with their details
    """
    try:
        client = get_emr_client()
        if not client:
            return {"error": "Failed to create EMR client"}

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
            "clusters": detailed_clusters,
            "count": len(detailed_clusters)
        }

    except ClientError as e:
        logger.error(f"Error listing EMR clusters: {e}")
        return {"error": f"Failed to list EMR clusters: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_emr_clusters: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def create_emr_cluster(cluster_name, instance_count=3, instance_type='m5.xlarge', release_label='emr-6.4.0'):
    """
    Create a new EMR cluster.

    Args:
        cluster_name (str): Name of the EMR cluster
        instance_count (int): Number of EC2 instances (default: 3)
        instance_type (str): EC2 instance type (default: m5.xlarge)
        release_label (str): EMR release version (default: emr-6.4.0)

    Returns:
        dict: Dictionary containing cluster creation result
    """
    try:
        client = get_emr_client()
        if not client:
            return {"error": "Failed to create EMR client"}

        if not cluster_name:
            return {"error": "Cluster name is required"}

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
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "status": "CREATED",
            "message": f"EMR cluster '{cluster_name}' created successfully"
        }

    except ClientError as e:
        logger.error(f"Error creating EMR cluster: {e}")
        return {"error": f"Failed to create EMR cluster: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in create_emr_cluster: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def terminate_emr_cluster(cluster_id):
    """
    Terminate an EMR cluster.

    Args:
        cluster_id (str): ID of the EMR cluster to terminate

    Returns:
        dict: Dictionary containing termination result
    """
    try:
        client = get_emr_client()
        if not client:
            return {"error": "Failed to create EMR client"}

        if not cluster_id:
            return {"error": "Cluster ID is required"}

        # Terminate the cluster
        client.terminate_job_flows(JobFlowIds=[cluster_id])

        return {
            "cluster_id": cluster_id,
            "status": "TERMINATION_INITIATED",
            "message": f"EMR cluster {cluster_id} termination initiated"
        }

    except ClientError as e:
        logger.error(f"Error terminating EMR cluster {cluster_id}: {e}")
        return {"error": f"Failed to terminate EMR cluster: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in terminate_emr_cluster: {e}")
        return {"error": f"Unexpected error: {str(e)}"}