"""
Secrets Manager MCP Tools
Herramientas MCP para gestión de AWS Secrets Manager
"""

import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict, List, Any, Optional

class SecretsManagerMCPTools:
    """Herramientas MCP para AWS Secrets Manager"""

    def __init__(self):
        self.client = None

    def _get_client(self):
        """Obtener cliente de Secrets Manager"""
        if not self.client:
            try:
                self.client = boto3.client('secretsmanager')
            except Exception as e:
                raise ConnectionError(f"Error al conectar con Secrets Manager: {str(e)}")
        return self.client

    def list_secrets(self) -> Dict[str, Any]:
        """
        Listar todos los secretos en Secrets Manager

        Returns:
            Dict con lista de secretos y metadatos
        """
        try:
            client = self._get_client()
            response = client.list_secrets(MaxResults=100)

            secrets = []
            for secret in response.get('SecretList', []):
                secrets.append({
                    'name': secret.get('Name'),
                    'arn': secret.get('ARN'),
                    'description': secret.get('Description'),
                    'created_date': secret.get('CreatedDate').isoformat() if secret.get('CreatedDate') else None,
                    'last_changed_date': secret.get('LastChangedDate').isoformat() if secret.get('LastChangedDate') else None,
                    'status': secret.get('SecretVersionsToStages', {}),
                    'tags': secret.get('Tags', [])
                })

            return {
                'success': True,
                'secrets': secrets,
                'count': len(secrets)
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'secrets': [],
                'count': 0
            }

    def create_secret(self, name: str, secret_string: str, description: str = None,
                     kms_key_id: str = None, tags: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Crear un nuevo secreto

        Args:
            name: Nombre del secreto
            secret_string: Valor del secreto como string JSON
            description: Descripción opcional
            kms_key_id: ID de clave KMS opcional
            tags: Lista de tags opcional

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            params = {
                'Name': name,
                'SecretString': secret_string
            }

            if description:
                params['Description'] = description
            if kms_key_id:
                params['KmsKeyId'] = kms_key_id
            if tags:
                params['Tags'] = tags

            response = client.create_secret(**params)

            return {
                'success': True,
                'secret_arn': response.get('ARN'),
                'name': response.get('Name'),
                'version_id': response.get('VersionId')
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_secret_value(self, secret_name: str, version_id: str = None,
                        version_stage: str = None) -> Dict[str, Any]:
        """
        Obtener el valor de un secreto

        Args:
            secret_name: Nombre o ARN del secreto
            version_id: ID de versión específico (opcional)
            version_stage: Stage de versión (opcional)

        Returns:
            Dict con el valor del secreto
        """
        try:
            client = self._get_client()

            params = {'SecretId': secret_name}
            if version_id:
                params['VersionId'] = version_id
            if version_stage:
                params['VersionStage'] = version_stage

            response = client.get_secret_value(**params)

            # Intentar parsear como JSON
            secret_value = response.get('SecretString', '')
            try:
                parsed_value = json.loads(secret_value)
            except json.JSONDecodeError:
                parsed_value = secret_value

            return {
                'success': True,
                'secret_value': parsed_value,
                'arn': response.get('ARN'),
                'name': response.get('Name'),
                'version_id': response.get('VersionId'),
                'version_stages': response.get('VersionStages', []),
                'created_date': response.get('CreatedDate').isoformat() if response.get('CreatedDate') else None
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_secret(self, secret_name: str, secret_string: str = None,
                     description: str = None, kms_key_id: str = None) -> Dict[str, Any]:
        """
        Actualizar un secreto existente

        Args:
            secret_name: Nombre o ARN del secreto
            secret_string: Nuevo valor del secreto (opcional)
            description: Nueva descripción (opcional)
            kms_key_id: Nueva clave KMS (opcional)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            params = {'SecretId': secret_name}

            if secret_string:
                params['SecretString'] = secret_string
            if description is not None:
                params['Description'] = description
            if kms_key_id:
                params['KmsKeyId'] = kms_key_id

            if not params:
                return {
                    'success': False,
                    'error': 'Debe proporcionar al menos un campo para actualizar'
                }

            response = client.update_secret(**params)

            return {
                'success': True,
                'arn': response.get('ARN'),
                'name': response.get('Name'),
                'version_id': response.get('VersionId')
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def rotate_secret(self, secret_name: str, rotation_lambda_arn: str = None,
                     automatically_after_days: int = None) -> Dict[str, Any]:
        """
        Rotar un secreto

        Args:
            secret_name: Nombre o ARN del secreto
            rotation_lambda_arn: ARN de la función Lambda para rotación (opcional)
            automatically_after_days: Días para rotación automática (opcional)

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            params = {'SecretId': secret_name}

            if rotation_lambda_arn:
                params['RotationLambdaARN'] = rotation_lambda_arn
            if automatically_after_days:
                params['AutomaticallyAfterDays'] = automatically_after_days

            response = client.rotate_secret(**params)

            return {
                'success': True,
                'arn': response.get('ARN'),
                'name': response.get('Name'),
                'version_id': response.get('VersionId'),
                'rotation_enabled': response.get('RotationEnabled', False)
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_secret(self, secret_name: str, recovery_window: int = 7,
                     force_delete: bool = False) -> Dict[str, Any]:
        """
        Eliminar un secreto

        Args:
            secret_name: Nombre o ARN del secreto
            recovery_window: Días para recuperación (7-30, default: 7)
            force_delete: Eliminar inmediatamente sin período de recuperación

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            params = {'SecretId': secret_name}

            if force_delete:
                params['ForceDeleteWithoutRecovery'] = True
            else:
                params['RecoveryWindowInDays'] = recovery_window

            response = client.delete_secret(**params)

            return {
                'success': True,
                'arn': response.get('ARN'),
                'name': response.get('Name'),
                'deletion_date': response.get('DeletionDate').isoformat() if response.get('DeletionDate') else None
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def restore_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Restaurar un secreto eliminado

        Args:
            secret_name: Nombre o ARN del secreto

        Returns:
            Dict con resultado de la operación
        """
        try:
            client = self._get_client()

            response = client.restore_secret(SecretId=secret_name)

            return {
                'success': True,
                'arn': response.get('ARN'),
                'name': response.get('Name')
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }