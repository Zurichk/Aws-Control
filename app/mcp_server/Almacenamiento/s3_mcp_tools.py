"""
MCP Tools para Amazon S3
Herramientas para gestión de buckets, objetos, políticas, etc.
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class S3MCPTools:
    """Herramientas MCP para operaciones con Amazon S3"""

    def __init__(self):
        self.s3_client = None
        self.s3_resource = None

    def _get_client(self):
        """Obtiene el cliente S3"""
        if self.s3_client is None:
            self.s3_client = get_aws_client('s3')
        return self.s3_client

    def _get_resource(self):
        """Obtiene el recurso S3"""
        if self.s3_resource is None:
            session = boto3.Session()
            self.s3_resource = session.resource('s3', region_name='us-east-1')
        return self.s3_resource

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para S3"""
        return [
            {
                'name': 's3_list_buckets',
                'description': 'Lista todos los buckets S3 disponibles',
                'parameters': {}
            },
            {
                'name': 's3_create_bucket',
                'description': 'Crea un nuevo bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'region': {'type': 'string', 'description': 'Región AWS (opcional)', 'default': 'us-east-1'},
                        'acl': {'type': 'string', 'description': 'ACL del bucket (private, public-read, etc.)', 'default': 'private'}
                    },
                    'required': ['bucket_name']
                }
            },
            {
                'name': 's3_delete_bucket',
                'description': 'Elimina un bucket S3 (debe estar vacío)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'}
                    },
                    'required': ['bucket_name']
                }
            },
            {
                'name': 's3_list_objects',
                'description': 'Lista objetos en un bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'prefix': {'type': 'string', 'description': 'Prefijo para filtrar objetos'},
                        'max_keys': {'type': 'integer', 'description': 'Número máximo de objetos', 'default': 1000}
                    },
                    'required': ['bucket_name']
                }
            },
            {
                'name': 's3_get_object',
                'description': 'Obtiene información de un objeto específico',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'key': {'type': 'string', 'description': 'Clave del objeto'}
                    },
                    'required': ['bucket_name', 'key']
                }
            },
            {
                'name': 's3_upload_object',
                'description': 'Sube un objeto a un bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'key': {'type': 'string', 'description': 'Clave del objeto'},
                        'file_path': {'type': 'string', 'description': 'Ruta del archivo local'},
                        'content_type': {'type': 'string', 'description': 'Tipo de contenido MIME'},
                        'metadata': {'type': 'object', 'description': 'Metadatos del objeto'}
                    },
                    'required': ['bucket_name', 'key', 'file_path']
                }
            },
            {
                'name': 's3_download_object',
                'description': 'Descarga un objeto desde S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'key': {'type': 'string', 'description': 'Clave del objeto'},
                        'file_path': {'type': 'string', 'description': 'Ruta donde guardar el archivo'}
                    },
                    'required': ['bucket_name', 'key', 'file_path']
                }
            },
            {
                'name': 's3_delete_object',
                'description': 'Elimina un objeto de un bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'key': {'type': 'string', 'description': 'Clave del objeto'}
                    },
                    'required': ['bucket_name', 'key']
                }
            },
            {
                'name': 's3_copy_object',
                'description': 'Copia un objeto dentro de S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'source_bucket': {'type': 'string', 'description': 'Bucket fuente'},
                        'source_key': {'type': 'string', 'description': 'Clave fuente'},
                        'dest_bucket': {'type': 'string', 'description': 'Bucket destino'},
                        'dest_key': {'type': 'string', 'description': 'Clave destino'}
                    },
                    'required': ['source_bucket', 'source_key', 'dest_bucket', 'dest_key']
                }
            },
            {
                'name': 's3_get_bucket_policy',
                'description': 'Obtiene la política de un bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'}
                    },
                    'required': ['bucket_name']
                }
            },
            {
                'name': 's3_put_bucket_policy',
                'description': 'Establece la política de un bucket S3',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'policy': {'type': 'string', 'description': 'Política en formato JSON'}
                    },
                    'required': ['bucket_name', 'policy']
                }
            },
            {
                'name': 's3_get_bucket_versioning',
                'description': 'Obtiene la configuración de versionado de un bucket',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'}
                    },
                    'required': ['bucket_name']
                }
            },
            {
                'name': 's3_put_bucket_versioning',
                'description': 'Configura el versionado de un bucket',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'bucket_name': {'type': 'string', 'description': 'Nombre del bucket'},
                        'versioning': {'type': 'string', 'description': 'Estado del versionado (Enabled, Suspended)', 'default': 'Enabled'}
                    },
                    'required': ['bucket_name']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de S3"""
        try:
            if tool_name == 's3_list_buckets':
                return self._list_buckets()
            elif tool_name == 's3_create_bucket':
                return self._create_bucket(**parameters)
            elif tool_name == 's3_delete_bucket':
                return self._delete_bucket(**parameters)
            elif tool_name == 's3_list_objects':
                return self._list_objects(**parameters)
            elif tool_name == 's3_get_object':
                return self._get_object(**parameters)
            elif tool_name == 's3_upload_object':
                return self._upload_object(**parameters)
            elif tool_name == 's3_download_object':
                return self._download_object(**parameters)
            elif tool_name == 's3_delete_object':
                return self._delete_object(**parameters)
            elif tool_name == 's3_copy_object':
                return self._copy_object(**parameters)
            elif tool_name == 's3_get_bucket_policy':
                return self._get_bucket_policy(**parameters)
            elif tool_name == 's3_put_bucket_policy':
                return self._put_bucket_policy(**parameters)
            elif tool_name == 's3_get_bucket_versioning':
                return self._get_bucket_versioning(**parameters)
            elif tool_name == 's3_put_bucket_versioning':
                return self._put_bucket_versioning(**parameters)
            else:
                return {'error': f'Herramienta S3 no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta S3 {tool_name}: {str(e)}'}

    def _list_buckets(self) -> Dict[str, Any]:
        """Lista todos los buckets"""
        client = self._get_client()
        response = client.list_buckets()

        buckets = [{
            'name': bucket['Name'],
            'creation_date': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
        } for bucket in response['Buckets']]

        return {
            'buckets': buckets,
            'total_count': len(buckets)
        }

    def _create_bucket(self, **kwargs) -> Dict[str, Any]:
        """Crea un nuevo bucket"""
        client = self._get_client()

        bucket_config = {}
        region = kwargs.get('region', 'us-east-1')

        # Configuración especial para buckets en regiones diferentes a us-east-1
        if region != 'us-east-1':
            bucket_config['CreateBucketConfiguration'] = {
                'LocationConstraint': region
            }

        # Crear el bucket
        if region == 'us-east-1':
            response = client.create_bucket(
                Bucket=kwargs.get('bucket_name'),
                ACL=kwargs.get('acl', 'private')
            )
        else:
            response = client.create_bucket(
                Bucket=kwargs.get('bucket_name'),
                ACL=kwargs.get('acl', 'private'),
                **bucket_config
            )

        return {
            'message': f'Bucket {kwargs.get('bucket_name')} creado exitosamente',
            'bucket_name': kwargs.get('bucket_name'),
            'location': response.get('Location', f'https://{kwargs.get('bucket_name')}.s3.amazonaws.com/')
        }

    def _delete_bucket(self, **kwargs) -> Dict[str, Any]:
        """Elimina un bucket"""
        client = self._get_client()

        client.delete_bucket(Bucket=kwargs.get('bucket_name'))

        return {
            'message': f'Bucket {kwargs.get('bucket_name')} eliminado exitosamente'
        }

    def _list_objects(self, **kwargs) -> Dict[str, Any]:
        """Lista objetos en un bucket"""
        client = self._get_client()

        s3_params = {
            'Bucket': kwargs.get('bucket_name'),
            'MaxKeys': kwargs.get('max_keys', 1000)
        }

        if kwargs.get('prefix'):
            s3_kwargs.get('Prefix') = kwargs.get('prefix')

        response = client.list_objects_v2(**s3_params)

        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S'),
                    'etag': obj['ETag'],
                    'storage_class': obj.get('StorageClass', 'STANDARD')
                })

        return {
            'bucket_name': kwargs.get('bucket_name'),
            'objects': objects,
            'total_count': len(objects),
            'is_truncated': response.get('IsTruncated', False),
            'next_continuation_token': response.get('NextContinuationToken')
        }

    def _get_object(self, **kwargs) -> Dict[str, Any]:
        """Obtiene información de un objeto"""
        client = self._get_client()

        response = client.head_object(
            Bucket=kwargs.get('bucket_name'),
            Key=kwargs.get('key')
        )

        return {
            'bucket_name': kwargs.get('bucket_name'),
            'key': kwargs.get('key'),
            'size': response.get('ContentLength', 0),
            'content_type': response.get('ContentType'),
            'last_modified': response.get('LastModified').strftime('%Y-%m-%d %H:%M:%S') if response.get('LastModified') else None,
            'etag': response.get('ETag'),
            'metadata': response.get('Metadata', {}),
            'storage_class': response.get('StorageClass', 'STANDARD'),
            'server_side_encryption': response.get('ServerSideEncryption'),
            'version_id': response.get('VersionId')
        }

    def _upload_object(self, **kwargs) -> Dict[str, Any]:
        """Sube un objeto a S3"""
        client = self._get_client()

        s3_params = {
            'Bucket': kwargs.get('bucket_name'),
            'Key': kwargs.get('key')
        }

        # Leer el archivo
        try:
            with open(kwargs.get('file_path'), 'rb') as file:
                s3_kwargs.get('Body') = file.read()
        except FileNotFoundError:
            return {'error': f'Archivo no encontrado: {kwargs.get('file_path')}'}

        if kwargs.get('content_type'):
            s3_kwargs.get('ContentType') = kwargs.get('content_type')

        if kwargs.get('metadata'):
            s3_kwargs.get('Metadata') = kwargs.get('metadata')

        response = client.put_object(**s3_params)

        return {
            'message': f'Objeto {kwargs.get('key')} subido exitosamente',
            'bucket_name': kwargs.get('bucket_name'),
            'key': kwargs.get('key'),
            'etag': response.get('ETag'),
            'version_id': response.get('VersionId')
        }

    def _download_object(self, **kwargs) -> Dict[str, Any]:
        """Descarga un objeto desde S3"""
        client = self._get_client()

        response = client.get_object(
            Bucket=kwargs.get('bucket_name'),
            Key=kwargs.get('key')
        )

        # Guardar el archivo
        with open(kwargs.get('file_path'), 'wb') as file:
            file.write(response['Body'].read())

        return {
            'message': f'Objeto {kwargs.get('key')} descargado exitosamente',
            'bucket_name': kwargs.get('bucket_name'),
            'key': kwargs.get('key'),
            'file_path': kwargs.get('file_path'),
            'size': response.get('ContentLength', 0),
            'content_type': response.get('ContentType')
        }

    def _delete_object(self, **kwargs) -> Dict[str, Any]:
        """Elimina un objeto"""
        client = self._get_client()

        response = client.delete_object(
            Bucket=kwargs.get('bucket_name'),
            Key=kwargs.get('key')
        )

        return {
            'message': f'Objeto {kwargs.get('key')} eliminado exitosamente',
            'bucket_name': kwargs.get('bucket_name'),
            'key': kwargs.get('key'),
            'delete_marker': response.get('DeleteMarker', False),
            'version_id': response.get('VersionId')
        }

    def _copy_object(self, **kwargs) -> Dict[str, Any]:
        """Copia un objeto"""
        client = self._get_client()

        copy_source = {
            'Bucket': kwargs.get('source_bucket'),
            'Key': kwargs.get('source_key')
        }

        response = client.copy_object(
            CopySource=copy_source,
            Bucket=kwargs.get('dest_bucket'),
            Key=kwargs.get('dest_key')
        )

        return {
            'message': f'Objeto copiado de {kwargs.get('source_bucket')}/{kwargs.get('source_key')} a {kwargs.get('dest_bucket')}/{kwargs.get('dest_key')}',
            'source_bucket': kwargs.get('source_bucket'),
            'source_key': kwargs.get('source_key'),
            'dest_bucket': kwargs.get('dest_bucket'),
            'dest_key': kwargs.get('dest_key'),
            'etag': response.get('CopyObjectResult', {}).get('ETag'),
            'last_modified': response.get('CopyObjectResult', {}).get('LastModified').strftime('%Y-%m-%d %H:%M:%S') if response.get('CopyObjectResult', {}).get('LastModified') else None
        }

    def _get_bucket_policy(self, **kwargs) -> Dict[str, Any]:
        """Obtiene la política de un bucket"""
        client = self._get_client()

        try:
            response = client.get_bucket_policy(Bucket=kwargs.get('bucket_name'))
            return {
                'bucket_name': kwargs.get('bucket_name'),
                'policy': response['Policy']
            }
        except client.exceptions.NoSuchBucketPolicy:
            return {
                'bucket_name': kwargs.get('bucket_name'),
                'policy': None,
                'message': 'El bucket no tiene política configurada'
            }

    def _put_bucket_policy(self, **kwargs) -> Dict[str, Any]:
        """Establece la política de un bucket"""
        client = self._get_client()

        client.put_bucket_policy(
            Bucket=kwargs.get('bucket_name'),
            Policy=kwargs.get('policy')
        )

        return {
            'message': f'Política aplicada al bucket {kwargs.get('bucket_name')}',
            'bucket_name': kwargs.get('bucket_name')
        }

    def _get_bucket_versioning(self, **kwargs) -> Dict[str, Any]:
        """Obtiene la configuración de versionado"""
        client = self._get_client()

        response = client.get_bucket_versioning(Bucket=kwargs.get('bucket_name'))

        return {
            'bucket_name': kwargs.get('bucket_name'),
            'versioning': response.get('Status', 'Suspended'),
            'mfa_delete': response.get('MFADelete', 'Disabled')
        }

    def _put_bucket_versioning(self, **kwargs) -> Dict[str, Any]:
        """Configura el versionado del bucket"""
        client = self._get_client()

        versioning_config = {
            'Status': kwargs.get('versioning', 'Enabled')
        }

        client.put_bucket_versioning(
            Bucket=kwargs.get('bucket_name'),
            VersioningConfiguration=versioning_config
        )

        return {
            'message': f'Versionado {versioning_config["Status"]} para bucket {kwargs.get('bucket_name')}',
            'bucket_name': kwargs.get('bucket_name'),
            'versioning_status': versioning_config['Status']
        }