import boto3
from flask import current_app
import os

def get_aws_client(service_name, region=None):
    """Get AWS client with credentials from environment variables"""
    if region is None:
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Configuración base
    config = {
        'service_name': service_name,
        'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'region_name': region
    }
    
    # Agregar session token si existe (necesario para laboratorios AWS)
    session_token = os.environ.get('AWS_SESSION_TOKEN')
    if session_token:
        config['aws_session_token'] = session_token
    
    return boto3.client(**config)

def get_aws_resource(service_name, region=None):
    """Get AWS resource with credentials from environment variables"""
    if region is None:
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Configuración base
    config = {
        'service_name': service_name,
        'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'region_name': region
    }
    
    # Agregar session token si existe (necesario para laboratorios AWS)
    session_token = os.environ.get('AWS_SESSION_TOKEN')
    if session_token:
        config['aws_session_token'] = session_token
    
    return boto3.resource(**config)