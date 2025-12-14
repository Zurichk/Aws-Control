"""
Route53 (DNS Service) MCP Tools
Herramientas para gestión completa de DNS, zonas hospedadas y registros DNS
"""

import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class Route53MCPTools:
    """Herramientas MCP para gestión de Route53 (DNS Service)"""

    @staticmethod
    def list_hosted_zones(region: str = None) -> Dict[str, Any]:
        """
        Lista todas las zonas hospedadas en Route53

        Args:
            region: Región de AWS (opcional, Route53 es global)

        Returns:
            Dict con lista de zonas hospedadas y metadatos
        """
        try:
            r53 = get_aws_client('route53', region)

            response = r53.list_hosted_zones()

            zones = []
            for zone in response['HostedZones']:
                zones.append({
                    'Id': zone['Id'],
                    'Name': zone['Name'],
                    'CallerReference': zone['CallerReference'],
                    'Config': {
                        'Comment': zone['Config'].get('Comment', ''),
                        'PrivateZone': zone['Config'].get('PrivateZone', False)
                    },
                    'ResourceRecordSetCount': zone.get('ResourceRecordSetCount', 0)
                })

            return {
                'success': True,
                'hosted_zones': zones,
                'count': len(zones),
                'marker': response.get('Marker'),
                'max_items': response.get('MaxItems'),
                'is_truncated': response.get('IsTruncated', False)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hosted_zones': [],
                'count': 0
            }

    @staticmethod
    def create_hosted_zone(
        name: str,
        caller_reference: str = None,
        comment: str = None,
        private_zone: bool = False,
        vpc_region: str = None,
        vpc_id: str = None,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva zona hospedada en Route53

        Args:
            name: Nombre del dominio (ej: example.com.)
            caller_reference: Referencia única para evitar duplicados
            comment: Comentario descriptivo
            private_zone: Si es una zona privada
            vpc_region: Región de la VPC (requerido para zonas privadas)
            vpc_id: ID de la VPC (requerido para zonas privadas)
            region: Región de AWS

        Returns:
            Dict con información de la zona creada
        """
        try:
            r53 = get_aws_client('route53', region)

            # Generar caller_reference si no se proporciona
            if not caller_reference:
                import time
                caller_reference = f"{name}-{int(time.time())}"

            params = {
                'Name': name,
                'CallerReference': caller_reference,
                'HostedZoneConfig': {
                    'Comment': comment or '',
                    'PrivateZone': private_zone
                }
            }

            # Agregar configuración de VPC para zonas privadas
            if private_zone and vpc_id and vpc_region:
                params['VPCs'] = [{
                    'VPCRegion': vpc_region,
                    'VPCId': vpc_id
                }]

            response = r53.create_hosted_zone(**params)

            return {
                'success': True,
                'hosted_zone': {
                    'Id': response['HostedZone']['Id'],
                    'Name': response['HostedZone']['Name'],
                    'CallerReference': response['HostedZone']['CallerReference'],
                    'Config': response['HostedZone']['Config']
                },
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat()
                },
                'delegation_set': response.get('DelegationSet', {}),
                'name_servers': response.get('DelegationSet', {}).get('NameServers', [])
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_hosted_zone(hosted_zone_id: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina una zona hospedada de Route53

        Args:
            hosted_zone_id: ID de la zona hospedada
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            r53 = get_aws_client('route53', region)

            response = r53.delete_hosted_zone(Id=hosted_zone_id)

            return {
                'success': True,
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat()
                },
                'hosted_zone_id': hosted_zone_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hosted_zone_id': hosted_zone_id
            }

    @staticmethod
    def list_resource_record_sets(
        hosted_zone_id: str,
        start_record_name: str = None,
        start_record_type: str = None,
        max_items: int = None,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Lista los registros de recursos de una zona hospedada

        Args:
            hosted_zone_id: ID de la zona hospedada
            start_record_name: Nombre del registro para empezar la lista
            start_record_type: Tipo de registro para empezar la lista
            max_items: Número máximo de registros a devolver
            region: Región de AWS

        Returns:
            Dict con lista de registros DNS
        """
        try:
            r53 = get_aws_client('route53', region)

            params = {'HostedZoneId': hosted_zone_id}

            if start_record_name:
                params['StartRecordName'] = start_record_name
            if start_record_type:
                params['StartRecordType'] = start_record_type
            if max_items:
                params['MaxItems'] = str(max_items)

            response = r53.list_resource_record_sets(**params)

            records = []
            for record in response.get('ResourceRecordSets', []):
                record_data = {
                    'Name': record['Name'],
                    'Type': record['Type'],
                    'TTL': record.get('TTL'),
                    'ResourceRecords': record.get('ResourceRecords', []),
                    'AliasTarget': record.get('AliasTarget'),
                    'HealthCheckId': record.get('HealthCheckId'),
                    'SetIdentifier': record.get('SetIdentifier'),
                    'Weight': record.get('Weight'),
                    'Region': record.get('Region'),
                    'GeoLocation': record.get('GeoLocation'),
                    'Failover': record.get('Failover'),
                    'MultiValue': record.get('MultiValue'),
                    'TrafficPolicyInstanceId': record.get('TrafficPolicyInstanceId')
                }
                records.append(record_data)

            return {
                'success': True,
                'resource_record_sets': records,
                'count': len(records),
                'hosted_zone_id': hosted_zone_id,
                'is_truncated': response.get('IsTruncated', False),
                'next_record_name': response.get('NextRecordName'),
                'next_record_type': response.get('NextRecordType'),
                'max_items': response.get('MaxItems')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'resource_record_sets': [],
                'count': 0,
                'hosted_zone_id': hosted_zone_id
            }

    @staticmethod
    def create_record(
        hosted_zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int = 300,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo registro DNS en una zona hospedada

        Args:
            hosted_zone_id: ID de la zona hospedada
            name: Nombre del registro (ej: www.example.com)
            record_type: Tipo de registro (A, AAAA, CNAME, MX, TXT, etc.)
            value: Valor del registro
            ttl: Time To Live en segundos
            region: Región de AWS

        Returns:
            Dict con resultado de la creación del registro
        """
        try:
            r53 = get_aws_client('route53', region)

            change_batch = {
                'Changes': [{
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [{'Value': value}]
                    }
                }]
            }

            response = r53.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch
            )

            return {
                'success': True,
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat()
                },
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'value': value,
                    'ttl': ttl
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'value': value,
                    'ttl': ttl
                }
            }

    @staticmethod
    def delete_record(
        hosted_zone_id: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int = 300,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Elimina un registro DNS de una zona hospedada

        Args:
            hosted_zone_id: ID de la zona hospedada
            name: Nombre del registro
            record_type: Tipo de registro
            value: Valor del registro
            ttl: Time To Live en segundos
            region: Región de AWS

        Returns:
            Dict con resultado de la eliminación del registro
        """
        try:
            r53 = get_aws_client('route53', region)

            change_batch = {
                'Changes': [{
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [{'Value': value}]
                    }
                }]
            }

            response = r53.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch
            )

            return {
                'success': True,
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat()
                },
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'value': value,
                    'ttl': ttl
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'value': value,
                    'ttl': ttl
                }
            }

    @staticmethod
    def update_record(
        hosted_zone_id: str,
        name: str,
        record_type: str,
        old_value: str,
        new_value: str,
        old_ttl: int = 300,
        new_ttl: int = 300,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Actualiza un registro DNS existente (DELETE + CREATE)

        Args:
            hosted_zone_id: ID de la zona hospedada
            name: Nombre del registro
            record_type: Tipo de registro
            old_value: Valor actual del registro
            new_value: Nuevo valor del registro
            old_ttl: TTL actual
            new_ttl: Nuevo TTL
            region: Región de AWS

        Returns:
            Dict con resultado de la actualización del registro
        """
        try:
            r53 = get_aws_client('route53', region)

            change_batch = {
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': record_type,
                            'TTL': old_ttl,
                            'ResourceRecords': [{'Value': old_value}]
                        }
                    },
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': record_type,
                            'TTL': new_ttl,
                            'ResourceRecords': [{'Value': new_value}]
                        }
                    }
                ]
            }

            response = r53.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch=change_batch
            )

            return {
                'success': True,
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat()
                },
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'old_value': old_value,
                    'new_value': new_value,
                    'old_ttl': old_ttl,
                    'new_ttl': new_ttl
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hosted_zone_id': hosted_zone_id,
                'record': {
                    'name': name,
                    'type': record_type,
                    'old_value': old_value,
                    'new_value': new_value
                }
            }

    @staticmethod
    def get_change(change_id: str, region: str = None) -> Dict[str, Any]:
        """
        Obtiene el estado de un cambio en Route53

        Args:
            change_id: ID del cambio (sin el prefijo /change/)
            region: Región de AWS

        Returns:
            Dict con información del cambio
        """
        try:
            r53 = get_aws_client('route53', region)

            # Agregar prefijo /change/ si no está presente
            if not change_id.startswith('/change/'):
                change_id = f'/change/{change_id}'

            response = r53.get_change(Id=change_id)

            return {
                'success': True,
                'change_info': {
                    'Id': response['ChangeInfo']['Id'],
                    'Status': response['ChangeInfo']['Status'],
                    'SubmittedAt': response['ChangeInfo']['SubmittedAt'].isoformat(),
                    'Comment': response['ChangeInfo'].get('Comment')
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'change_id': change_id
            }