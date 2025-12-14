import boto3
from flask import current_app, session
import os

def get_aws_client(service_name, region=None):
    """Get AWS client with credentials from session or environment variables"""
    if region is None:
        # Primero intentar obtener de sesión, luego de variables de entorno
        region = session.get('aws_default_region') or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Configuración base - intentar obtener de sesión primero, luego de variables de entorno
    access_key = session.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = session.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY')
    session_token = session.get('aws_session_token') or os.environ.get('AWS_SESSION_TOKEN')

    config = {
        'service_name': service_name,
        'region_name': region
    }

    # Agregar credenciales si existen
    if access_key:
        config['aws_access_key_id'] = access_key
    if secret_key:
        config['aws_secret_access_key'] = secret_key
    if session_token:
        config['aws_session_token'] = session_token

    return boto3.client(**config)

def get_aws_resource(service_name, region=None):
    """Get AWS resource with credentials from session or environment variables"""
    if region is None:
        # Primero intentar obtener de sesión, luego de variables de entorno
        region = session.get('aws_default_region') or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    # Configuración base - intentar obtener de sesión primero, luego de variables de entorno
    access_key = session.get('aws_access_key_id') or os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = session.get('aws_secret_access_key') or os.environ.get('AWS_SECRET_ACCESS_KEY')
    session_token = session.get('aws_session_token') or os.environ.get('AWS_SESSION_TOKEN')

    config = {
        'service_name': service_name,
        'region_name': region
    }

    # Agregar credenciales si existen
    if access_key:
        config['aws_access_key_id'] = access_key
    if secret_key:
        config['aws_secret_access_key'] = secret_key
    if session_token:
        config['aws_session_token'] = session_token

    return boto3.resource(**config)