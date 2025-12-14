import boto3
import os
from typing import Dict, List, Any, Optional

class ECRMCPTools:
    """Herramientas MCP para gestión de Amazon Elastic Container Registry (ECR)"""

    def __init__(self):
        self.client_name = 'ecr'

    def _get_client(self):
        """Obtener cliente de ECR"""
        return boto3.client(
            self.client_name,
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )

    def describe_repositories(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todos los repositorios ECR

        Args:
            params: Parámetros opcionales
                - repository_names: Lista específica de nombres de repositorios
                - max_results: Número máximo de resultados (default: 100)

        Returns:
            Dict con lista de repositorios
        """
        try:
            ecr = self._get_client()
            kwargs = {}

            if params:
                if 'repository_names' in params:
                    kwargs['repositoryNames'] = params['repository_names']
                if 'max_results' in params:
                    kwargs['maxResults'] = min(int(params['max_results']), 1000)  # Máximo 1000

            response = ecr.describe_repositories(**kwargs)

            repositories = []
            for repo in response['repositories']:
                # Obtener información adicional de imágenes
                try:
                    images_response = ecr.list_images(repositoryName=repo['repositoryName'])
                    image_count = len(images_response.get('imageIds', []))
                except Exception:
                    image_count = 0

                repositories.append({
                    'repository_name': repo['repositoryName'],
                    'repository_arn': repo['repositoryArn'],
                    'repository_uri': repo['repositoryUri'],
                    'created_at': repo['createdAt'].isoformat() if repo.get('createdAt') else None,
                    'image_count': image_count,
                    'scan_on_push': repo.get('imageScanningConfiguration', {}).get('scanOnPush', False),
                    'encryption_configuration': repo.get('encryptionConfiguration', {}),
                    'image_tag_mutability': repo.get('imageTagMutability', 'MUTABLE')
                })

            return {
                'success': True,
                'repositories': repositories,
                'total_count': len(repositories)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_repository(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo repositorio ECR

        Args:
            params: Parámetros del repositorio
                - repository_name (str): Nombre del repositorio
                - image_tag_mutability (str, opcional): 'MUTABLE' o 'IMMUTABLE' (default: MUTABLE)
                - scan_on_push (bool, opcional): Habilitar escaneo al hacer push (default: False)
                - encryption_type (str, opcional): Tipo de encriptación ('AES256' o 'KMS')
                - kms_key (str, opcional): ARN de la clave KMS para encriptación

        Returns:
            Dict con resultado de la creación
        """
        try:
            required_params = ['repository_name']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            # Configurar repositorio
            repo_config = {
                'repositoryName': params['repository_name'],
                'imageTagMutability': params.get('image_tag_mutability', 'MUTABLE'),
                'imageScanningConfiguration': {
                    'scanOnPush': params.get('scan_on_push', False)
                }
            }

            # Configurar encriptación si se especifica
            if 'encryption_type' in params:
                encryption_config = {
                    'encryptionType': params['encryption_type']
                }
                if params.get('kms_key'):
                    encryption_config['kmsKey'] = params['kms_key']
                repo_config['encryptionConfiguration'] = encryption_config

            response = ecr.create_repository(**repo_config)

            return {
                'success': True,
                'repository_name': response['repository']['repositoryName'],
                'repository_arn': response['repository']['repositoryArn'],
                'repository_uri': response['repository']['repositoryUri'],
                'created_at': response['repository']['createdAt'].isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_repository(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina un repositorio ECR

        Args:
            params: Parámetros de eliminación
                - repository_name (str): Nombre del repositorio
                - force (bool, opcional): Forzar eliminación incluso con imágenes (default: False)

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            required_params = ['repository_name']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            kwargs = {'repositoryName': params['repository_name']}
            if params.get('force', False):
                kwargs['force'] = True

            response = ecr.delete_repository(**kwargs)

            return {
                'success': True,
                'repository_arn': response['repository']['repositoryArn'],
                'message': f'Repositorio {params["repository_name"]} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lista las imágenes en un repositorio ECR

        Args:
            params: Parámetros de consulta
                - repository_name (str): Nombre del repositorio
                - max_results (int, opcional): Número máximo de resultados (default: 100)

        Returns:
            Dict con lista de imágenes
        """
        try:
            required_params = ['repository_name']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            kwargs = {'repositoryName': params['repository_name']}
            if 'max_results' in params:
                kwargs['maxResults'] = min(int(params['max_results']), 1000)

            response = ecr.list_images(**kwargs)

            images = []
            for image_id in response.get('imageIds', []):
                images.append({
                    'image_digest': image_id.get('imageDigest'),
                    'image_tag': image_id.get('imageTag'),
                    'pushed_at': image_id.get('imagePushedAt').isoformat() if image_id.get('imagePushedAt') else None
                })

            return {
                'success': True,
                'repository_name': params['repository_name'],
                'images': images,
                'total_count': len(images)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina una imagen de un repositorio ECR

        Args:
            params: Parámetros de eliminación
                - repository_name (str): Nombre del repositorio
                - image_ids (list): Lista de IDs de imágenes a eliminar
                  Cada ID puede tener 'imageDigest' o 'imageTag'

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            required_params = ['repository_name', 'image_ids']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            response = ecr.batch_delete_image(
                repositoryName=params['repository_name'],
                imageIds=params['image_ids']
            )

            deleted_images = []
            failed_deletions = []

            for result in response.get('imageIds', []):
                deleted_images.append({
                    'image_digest': result.get('imageDigest'),
                    'image_tag': result.get('imageTag')
                })

            for failure in response.get('failures', []):
                failed_deletions.append({
                    'image_id': failure.get('imageId', {}),
                    'failure_code': failure.get('failureCode'),
                    'failure_reason': failure.get('failureReason')
                })

            return {
                'success': True,
                'repository_name': params['repository_name'],
                'deleted_images': deleted_images,
                'failed_deletions': failed_deletions,
                'deleted_count': len(deleted_images),
                'failed_count': len(failed_deletions)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_repository_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene la política de un repositorio ECR

        Args:
            params: Parámetros de consulta
                - repository_name (str): Nombre del repositorio

        Returns:
            Dict con la política del repositorio
        """
        try:
            required_params = ['repository_name']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            response = ecr.get_repository_policy(repositoryName=params['repository_name'])

            return {
                'success': True,
                'repository_name': params['repository_name'],
                'policy_text': response['policyText'],
                'registry_id': response['registryId']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def set_repository_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Establece la política de un repositorio ECR

        Args:
            params: Parámetros de configuración
                - repository_name (str): Nombre del repositorio
                - policy_text (str): Política en formato JSON

        Returns:
            Dict con resultado de la configuración
        """
        try:
            required_params = ['repository_name', 'policy_text']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            ecr = self._get_client()

            response = ecr.set_repository_policy(
                repositoryName=params['repository_name'],
                policyText=params['policy_text']
            )

            return {
                'success': True,
                'repository_name': params['repository_name'],
                'registry_id': response['registryId'],
                'message': 'Política del repositorio actualizada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }