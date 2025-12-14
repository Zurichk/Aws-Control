import boto3
import os
from typing import Dict, List, Any, Optional

class CloudFrontMCPTools:
    """Herramientas MCP para gestión de CloudFront Distributions"""

    def __init__(self):
        self.client_name = 'cloudfront'

    def _get_client(self):
        """Obtener cliente de CloudFront"""
        return boto3.client(
            self.client_name,
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )

    def list_distributions(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todas las distribuciones de CloudFront

        Args:
            params: Parámetros opcionales (no requeridos para este método)

        Returns:
            Dict con lista de distribuciones
        """
        try:
            cf = self._get_client()
            response = cf.list_distributions()

            distributions = []
            if 'DistributionList' in response and 'Items' in response['DistributionList']:
                for dist in response['DistributionList']['Items']:
                    distributions.append({
                        'id': dist['Id'],
                        'domain_name': dist['DomainName'],
                        'status': dist['Status'],
                        'enabled': dist['Enabled'],
                        'comment': dist.get('Comment', ''),
                        'origins_count': len(dist.get('Origins', {}).get('Items', [])),
                        'last_modified_time': dist.get('LastModifiedTime', '').isoformat() if dist.get('LastModifiedTime') else None
                    })

            return {
                'success': True,
                'distributions': distributions,
                'total_count': len(distributions)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva distribución de CloudFront

        Args:
            params: Parámetros de la distribución
                - origin_domain (str): Dominio de origen
                - comment (str, opcional): Comentario
                - enabled (bool, opcional): Si está habilitada (default: True)
                - price_class (str, opcional): Clase de precio (PriceClass_All, PriceClass_200, PriceClass_100)

        Returns:
            Dict con resultado de la creación
        """
        try:
            required_params = ['origin_domain']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            cf = self._get_client()

            # Configurar distribución básica
            distribution_config = {
                'CallerReference': str(params['origin_domain']) + str(os.urandom(16).hex()),
                'Comment': params.get('comment', ''),
                'Enabled': params.get('enabled', True),
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': 'origin1',
                        'DomainName': params['origin_domain'],
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'https-only'
                        }
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'origin1',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 0,
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {
                            'Forward': 'none'
                        }
                    }
                },
                'Comment': params.get('comment', ''),
                'PriceClass': params.get('price_class', 'PriceClass_All')
            }

            response = cf.create_distribution(DistributionConfig=distribution_config)

            return {
                'success': True,
                'distribution_id': response['Distribution']['Id'],
                'domain_name': response['Distribution']['DomainName'],
                'status': response['Distribution']['Status']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza una distribución de CloudFront

        Args:
            params: Parámetros de actualización
                - distribution_id (str): ID de la distribución
                - comment (str, opcional): Nuevo comentario
                - enabled (bool, opcional): Nuevo estado habilitado
                - price_class (str, opcional): Nueva clase de precio

        Returns:
            Dict con resultado de la actualización
        """
        try:
            required_params = ['distribution_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            cf = self._get_client()

            # Obtener configuración actual
            dist_config = cf.get_distribution_config(Id=params['distribution_id'])
            config = dist_config['DistributionConfig']

            # Actualizar campos si se proporcionan
            if 'comment' in params:
                config['Comment'] = params['comment']
            if 'enabled' in params:
                config['Enabled'] = params['enabled']
            if 'price_class' in params:
                config['PriceClass'] = params['price_class']

            # Actualizar distribución
            response = cf.update_distribution(
                Id=params['distribution_id'],
                DistributionConfig=config,
                IfMatch=dist_config['ETag']
            )

            return {
                'success': True,
                'distribution_id': response['Distribution']['Id'],
                'domain_name': response['Distribution']['DomainName'],
                'status': response['Distribution']['Status']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_distribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina una distribución de CloudFront

        Args:
            params: Parámetros de eliminación
                - distribution_id (str): ID de la distribución a eliminar

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            required_params = ['distribution_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            cf = self._get_client()

            # Obtener ETag para la eliminación
            dist_config = cf.get_distribution_config(Id=params['distribution_id'])

            # Deshabilitar distribución primero si está habilitada
            if dist_config['DistributionConfig']['Enabled']:
                config = dist_config['DistributionConfig']
                config['Enabled'] = False

                cf.update_distribution(
                    Id=params['distribution_id'],
                    DistributionConfig=config,
                    IfMatch=dist_config['ETag']
                )

                # Esperar a que se deshabilite (esto es simplificado)
                import time
                time.sleep(5)

                # Obtener nuevo ETag
                dist_config = cf.get_distribution_config(Id=params['distribution_id'])

            # Eliminar distribución
            cf.delete_distribution(
                Id=params['distribution_id'],
                IfMatch=dist_config['ETag']
            )

            return {
                'success': True,
                'message': f'Distribución {params["distribution_id"]} eliminada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_invalidation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una invalidación para una distribución de CloudFront

        Args:
            params: Parámetros de invalidación
                - distribution_id (str): ID de la distribución
                - paths (list): Lista de rutas a invalidar (ej: ['/*', '/index.html'])

        Returns:
            Dict con resultado de la invalidación
        """
        try:
            required_params = ['distribution_id', 'paths']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            cf = self._get_client()

            # Crear invalidación
            invalidation_response = cf.create_invalidation(
                DistributionId=params['distribution_id'],
                InvalidationBatch={
                    'CallerReference': str(os.urandom(16).hex()),
                    'Paths': {
                        'Quantity': len(params['paths']),
                        'Items': params['paths']
                    }
                }
            )

            return {
                'success': True,
                'invalidation_id': invalidation_response['Invalidation']['Id'],
                'distribution_id': params['distribution_id'],
                'status': invalidation_response['Invalidation']['Status'],
                'paths_invalidated': params['paths']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
