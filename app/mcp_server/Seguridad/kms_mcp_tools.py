import boto3
import os
import base64
from typing import Dict, List, Any, Optional

class KMSMCPTools:
    """Herramientas MCP para gestión de AWS Key Management Service (KMS)"""

    def __init__(self):
        self.client_name = 'kms'

    def _get_client(self):
        """Obtener cliente de KMS"""
        return boto3.client(
            self.client_name,
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )

    def list_keys(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todas las claves KMS

        Args:
            params: Parámetros opcionales
                - limit (int, opcional): Número máximo de claves a retornar (default: 100)
                - marker (str, opcional): Token de paginación

        Returns:
            Dict con lista de claves KMS
        """
        try:
            kms = self._get_client()
            kwargs = {}
            if params:
                if 'limit' in params:
                    kwargs['Limit'] = min(int(params['limit']), 1000)  # Máximo 1000
                if 'marker' in params:
                    kwargs['Marker'] = params['marker']

            response = kms.list_keys(**kwargs)

            keys = []
            for key in response.get('Keys', []):
                try:
                    # Obtener detalles adicionales de la clave
                    key_info = kms.describe_key(KeyId=key['KeyId'])
                    aliases = kms.list_aliases(KeyId=key['KeyId'])

                    keys.append({
                        'key_id': key['KeyId'],
                        'key_arn': key_info['KeyMetadata']['Arn'],
                        'description': key_info['KeyMetadata'].get('Description', ''),
                        'key_state': key_info['KeyMetadata']['KeyState'],
                        'key_usage': key_info['KeyMetadata']['KeyUsage'],
                        'key_spec': key_info['KeyMetadata']['KeySpec'],
                        'origin': key_info['KeyMetadata']['Origin'],
                        'creation_date': key_info['KeyMetadata']['CreationDate'].isoformat() if key_info['KeyMetadata']['CreationDate'] else None,
                        'enabled': key_info['KeyMetadata']['Enabled'],
                        'aliases': [alias['AliasName'] for alias in aliases.get('Aliases', []) if not alias['AliasName'].startswith('alias/aws/')]
                    })
                except Exception as e:
                    # Si hay error con una clave específica, incluir información básica
                    keys.append({
                        'key_id': key['KeyId'],
                        'error': str(e)
                    })

            return {
                'success': True,
                'keys': keys,
                'truncated': response.get('Truncated', False),
                'next_marker': response.get('NextMarker'),
                'total_count': len(keys)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva clave KMS

        Args:
            params: Parámetros de la clave
                - description (str, opcional): Descripción de la clave
                - key_usage (str, opcional): Uso de la clave ('ENCRYPT_DECRYPT' o 'SIGN_VERIFY')
                - key_spec (str, opcional): Especificación de la clave
                - origin (str, opcional): Origen de la clave ('AWS_KMS', 'EXTERNAL', 'AWS_CLOUDHSM')
                - alias (str, opcional): Alias para la clave

        Returns:
            Dict con resultado de la creación
        """
        try:
            kms = self._get_client()

            # Configurar parámetros de la clave
            key_config = {}
            if 'description' in params:
                key_config['Description'] = params['description']
            if 'key_usage' in params:
                key_config['KeyUsage'] = params['key_usage']
            if 'key_spec' in params:
                key_config['KeySpec'] = params['key_spec']
            if 'origin' in params:
                key_config['Origin'] = params['origin']

            response = kms.create_key(**key_config)

            key_id = response['KeyMetadata']['KeyId']
            key_arn = response['KeyMetadata']['Arn']

            # Crear alias si se especifica
            if 'alias' in params:
                kms.create_alias(
                    AliasName=params['alias'],
                    TargetKeyId=key_id
                )

            return {
                'success': True,
                'key_id': key_id,
                'key_arn': key_arn,
                'key_state': response['KeyMetadata']['KeyState'],
                'description': response['KeyMetadata'].get('Description', ''),
                'alias': params.get('alias')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def disable_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deshabilita una clave KMS

        Args:
            params: Parámetros de deshabilitación
                - key_id (str): ID o ARN de la clave

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()
            kms.disable_key(KeyId=params['key_id'])

            return {
                'success': True,
                'message': f'Clave {params["key_id"]} deshabilitada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def enable_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Habilita una clave KMS

        Args:
            params: Parámetros de habilitación
                - key_id (str): ID o ARN de la clave

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()
            kms.enable_key(KeyId=params['key_id'])

            return {
                'success': True,
                'message': f'Clave {params["key_id"]} habilitada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def schedule_key_deletion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Programa la eliminación de una clave KMS

        Args:
            params: Parámetros de eliminación
                - key_id (str): ID o ARN de la clave
                - pending_window_in_days (int, opcional): Días de espera antes de eliminar (7-30, default: 30)

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()

            kwargs = {'KeyId': params['key_id']}
            if 'pending_window_in_days' in params:
                window = int(params['pending_window_in_days'])
                kwargs['PendingWindowInDays'] = max(7, min(30, window))  # Entre 7 y 30 días

            response = kms.schedule_key_deletion(**kwargs)

            return {
                'success': True,
                'key_id': response['KeyId'],
                'deletion_date': response['DeletionDate'].isoformat(),
                'pending_window_in_days': kwargs.get('PendingWindowInDays', 30)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def cancel_key_deletion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancela la eliminación programada de una clave KMS

        Args:
            params: Parámetros de cancelación
                - key_id (str): ID o ARN de la clave

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()
            response = kms.cancel_key_deletion(KeyId=params['key_id'])

            return {
                'success': True,
                'key_id': response['KeyId'],
                'key_state': response['KeyState']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def enable_key_rotation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Habilita la rotación automática de una clave KMS

        Args:
            params: Parámetros de rotación
                - key_id (str): ID o ARN de la clave

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()
            kms.enable_key_rotation(KeyId=params['key_id'])

            return {
                'success': True,
                'message': f'Rotación de clave habilitada para {params["key_id"]}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def disable_key_rotation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deshabilita la rotación automática de una clave KMS

        Args:
            params: Parámetros de rotación
                - key_id (str): ID o ARN de la clave

        Returns:
            Dict con resultado de la operación
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()
            kms.disable_key_rotation(KeyId=params['key_id'])

            return {
                'success': True,
                'message': f'Rotación de clave deshabilitada para {params["key_id"]}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def encrypt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encripta datos usando una clave KMS

        Args:
            params: Parámetros de encriptación
                - key_id (str): ID o ARN de la clave
                - plaintext (str): Datos a encriptar (texto plano)
                - encryption_context (dict, opcional): Contexto de encriptación

        Returns:
            Dict con datos encriptados
        """
        try:
            required_params = ['key_id', 'plaintext']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()

            kwargs = {
                'KeyId': params['key_id'],
                'Plaintext': params['plaintext']
            }

            if 'encryption_context' in params:
                kwargs['EncryptionContext'] = params['encryption_context']

            response = kms.encrypt(**kwargs)

            return {
                'success': True,
                'key_id': response['KeyId'],
                'ciphertext_blob': base64.b64encode(response['CiphertextBlob']).decode('utf-8'),
                'encryption_algorithm': response.get('EncryptionAlgorithm', 'SYMMETRIC_DEFAULT')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def decrypt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Desencripta datos usando una clave KMS

        Args:
            params: Parámetros de desencriptación
                - ciphertext_blob (str): Datos encriptados (base64)
                - encryption_context (dict, opcional): Contexto de encriptación

        Returns:
            Dict con datos desencriptados
        """
        try:
            required_params = ['ciphertext_blob']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()

            kwargs = {
                'CiphertextBlob': base64.b64decode(params['ciphertext_blob'])
            }

            if 'encryption_context' in params:
                kwargs['EncryptionContext'] = params['encryption_context']

            response = kms.decrypt(**kwargs)

            return {
                'success': True,
                'key_id': response['KeyId'],
                'plaintext': response['Plaintext'].decode('utf-8'),
                'encryption_algorithm': response.get('EncryptionAlgorithm', 'SYMMETRIC_DEFAULT')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def generate_data_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera una clave de datos encriptada usando KMS

        Args:
            params: Parámetros de generación
                - key_id (str): ID o ARN de la clave KMS
                - key_spec (str, opcional): Especificación de la clave de datos
                - number_of_bytes (int, opcional): Número de bytes para la clave
                - encryption_context (dict, opcional): Contexto de encriptación

        Returns:
            Dict con clave de datos generada
        """
        try:
            required_params = ['key_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            kms = self._get_client()

            kwargs = {'KeyId': params['key_id']}

            if 'key_spec' in params:
                kwargs['KeySpec'] = params['key_spec']
            if 'number_of_bytes' in params:
                kwargs['NumberOfBytes'] = int(params['number_of_bytes'])
            if 'encryption_context' in params:
                kwargs['EncryptionContext'] = params['encryption_context']

            response = kms.generate_data_key(**kwargs)

            return {
                'success': True,
                'key_id': response['KeyId'],
                'plaintext': base64.b64encode(response['Plaintext']).decode('utf-8'),
                'ciphertext_blob': base64.b64encode(response['CiphertextBlob']).decode('utf-8'),
                'key_spec': response.get('KeySpec', 'AES_256')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }