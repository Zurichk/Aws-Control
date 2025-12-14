"""
EBS (Elastic Block Store) MCP Tools
Herramientas para gestión completa de volúmenes EBS, snapshots y attachments
"""

import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class EBSMCPTools:
    """Herramientas MCP para gestión de EBS (Elastic Block Store)"""

    @staticmethod
    def list_ebs_volumes(region: str = None, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista todos los volúmenes EBS en la región especificada

        Args:
            region: Región de AWS (opcional, usa default si no se especifica)
            filters: Filtros adicionales para la consulta (opcional)

        Returns:
            Dict con lista de volúmenes EBS y metadatos
        """
        try:
            ec2 = get_aws_client('ec2', region)

            params = {}
            if filters:
                params['Filters'] = [{'Name': k, 'Values': v if isinstance(v, list) else [v]} for k, v in filters.items()]

            response = ec2.describe_volumes(**params)

            volumes = []
            for volume in response['Volumes']:
                volumes.append({
                    'VolumeId': volume['VolumeId'],
                    'Size': volume['Size'],
                    'VolumeType': volume['VolumeType'],
                    'State': volume['State'],
                    'AvailabilityZone': volume['AvailabilityZone'],
                    'CreateTime': volume['CreateTime'].isoformat() if volume.get('CreateTime') else None,
                    'Iops': volume.get('Iops'),
                    'Throughput': volume.get('Throughput'),
                    'Encrypted': volume.get('Encrypted', False),
                    'KmsKeyId': volume.get('KmsKeyId'),
                    'Attachments': [{
                        'InstanceId': att.get('InstanceId'),
                        'Device': att.get('Device'),
                        'State': att.get('State'),
                        'AttachTime': att.get('AttachTime').isoformat() if att.get('AttachTime') else None
                    } for att in volume.get('Attachments', [])],
                    'Tags': {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                })

            return {
                'success': True,
                'volumes': volumes,
                'count': len(volumes),
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volumes': [],
                'count': 0
            }

    @staticmethod
    def create_ebs_volume(
        availability_zone: str,
        size: int,
        volume_type: str = 'gp3',
        region: str = None,
        iops: int = None,
        throughput: int = None,
        encrypted: bool = False,
        kms_key_id: str = None,
        tags: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo volumen EBS

        Args:
            availability_zone: Zona de disponibilidad (ej: us-east-1a)
            size: Tamaño en GB
            volume_type: Tipo de volumen (gp2, gp3, io1, io2, st1, sc1)
            region: Región de AWS
            iops: IOPS para volúmenes io1/io2/gp3
            throughput: Throughput para volúmenes gp3
            encrypted: Si el volumen debe estar encriptado
            kms_key_id: ID de la clave KMS para encriptación
            tags: Tags para el volumen

        Returns:
            Dict con información del volumen creado
        """
        try:
            ec2 = get_aws_client('ec2', region)

            params = {
                'AvailabilityZone': availability_zone,
                'Size': size,
                'VolumeType': volume_type
            }

            if iops and volume_type in ['io1', 'io2', 'gp3']:
                params['Iops'] = iops

            if throughput and volume_type == 'gp3':
                params['Throughput'] = throughput

            if encrypted:
                params['Encrypted'] = True
                if kms_key_id:
                    params['KmsKeyId'] = kms_key_id

            response = ec2.create_volume(**params)

            volume_id = response['VolumeId']

            # Agregar tags si se especificaron
            if tags:
                tag_specifications = [{
                    'ResourceType': 'volume',
                    'Tags': [{'Key': k, 'Value': v} for k, v in tags.items()]
                }]
                ec2.create_tags(Resources=[volume_id], Tags=tag_specifications['Tags'])

            return {
                'success': True,
                'volume_id': volume_id,
                'state': response['State'],
                'size': response['Size'],
                'volume_type': response['VolumeType'],
                'availability_zone': response['AvailabilityZone'],
                'create_time': response['CreateTime'].isoformat(),
                'encrypted': response.get('Encrypted', False)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_ebs_volume(volume_id: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina un volumen EBS

        Args:
            volume_id: ID del volumen EBS
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            ec2 = get_aws_client('ec2', region)

            response = ec2.delete_volume(VolumeId=volume_id)

            return {
                'success': True,
                'volume_id': volume_id,
                'message': f'Volumen EBS {volume_id} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volume_id': volume_id
            }

    @staticmethod
    def attach_ebs_volume(
        volume_id: str,
        instance_id: str,
        device: str,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Adjunta un volumen EBS a una instancia EC2

        Args:
            volume_id: ID del volumen EBS
            instance_id: ID de la instancia EC2
            device: Dispositivo (ej: /dev/sdf, /dev/xvdf)
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            ec2 = get_aws_client('ec2', region)

            response = ec2.attach_volume(
                VolumeId=volume_id,
                InstanceId=instance_id,
                Device=device
            )

            return {
                'success': True,
                'volume_id': volume_id,
                'instance_id': instance_id,
                'device': device,
                'state': response.get('State', 'attaching'),
                'attach_time': response.get('AttachTime').isoformat() if response.get('AttachTime') else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volume_id': volume_id,
                'instance_id': instance_id
            }

    @staticmethod
    def detach_ebs_volume(volume_id: str, region: str = None, force: bool = False) -> Dict[str, Any]:
        """
        Desadjunta un volumen EBS de una instancia EC2

        Args:
            volume_id: ID del volumen EBS
            region: Región de AWS
            force: Forzar desadjuntamiento (útil si la instancia no responde)

        Returns:
            Dict con resultado de la operación
        """
        try:
            ec2 = get_aws_client('ec2', region)

            params = {'VolumeId': volume_id}
            if force:
                params['Force'] = True

            response = ec2.detach_volume(**params)

            return {
                'success': True,
                'volume_id': volume_id,
                'state': response.get('State', 'detaching'),
                'detach_time': response.get('DetachTime').isoformat() if response.get('DetachTime') else None,
                'device': response.get('Device')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volume_id': volume_id
            }

    @staticmethod
    def list_ebs_snapshots(region: str = None, owner: str = 'self', volume_id: str = None) -> Dict[str, Any]:
        """
        Lista snapshots EBS

        Args:
            region: Región de AWS
            owner: Propietario ('self', 'amazon', o ID de cuenta)
            volume_id: Filtrar por ID de volumen específico

        Returns:
            Dict con lista de snapshots
        """
        try:
            ec2 = get_aws_client('ec2', region)

            params = {'OwnerIds': [owner]}

            if volume_id:
                params['Filters'] = [{'Name': 'volume-id', 'Values': [volume_id]}]

            response = ec2.describe_snapshots(**params)

            snapshots = []
            for snapshot in response['Snapshots']:
                snapshots.append({
                    'SnapshotId': snapshot['SnapshotId'],
                    'VolumeId': snapshot['VolumeId'],
                    'VolumeSize': snapshot['VolumeSize'],
                    'State': snapshot['State'],
                    'StartTime': snapshot['StartTime'].isoformat(),
                    'Progress': snapshot.get('Progress'),
                    'Description': snapshot.get('Description', ''),
                    'Encrypted': snapshot.get('Encrypted', False),
                    'KmsKeyId': snapshot.get('KmsKeyId'),
                    'OwnerId': snapshot.get('OwnerId'),
                    'Tags': {tag['Key']: tag['Value'] for tag in snapshot.get('Tags', [])}
                })

            return {
                'success': True,
                'snapshots': snapshots,
                'count': len(snapshots),
                'owner': owner,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'snapshots': [],
                'count': 0
            }

    @staticmethod
    def create_ebs_snapshot(
        volume_id: str,
        description: str = None,
        region: str = None,
        tags: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Crea un snapshot de un volumen EBS

        Args:
            volume_id: ID del volumen EBS
            description: Descripción del snapshot
            region: Región de AWS
            tags: Tags para el snapshot

        Returns:
            Dict con información del snapshot creado
        """
        try:
            ec2 = get_aws_client('ec2', region)

            params = {'VolumeId': volume_id}
            if description:
                params['Description'] = description

            response = ec2.create_snapshot(**params)

            snapshot_id = response['SnapshotId']

            # Agregar tags si se especificaron
            if tags:
                tag_specifications = [{
                    'ResourceType': 'snapshot',
                    'Tags': [{'Key': k, 'Value': v} for k, v in tags.items()]
                }]
                ec2.create_tags(Resources=[snapshot_id], Tags=tag_specifications['Tags'])

            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'volume_id': volume_id,
                'state': response['State'],
                'start_time': response['StartTime'].isoformat(),
                'progress': response.get('Progress'),
                'description': response.get('Description', ''),
                'volume_size': response.get('VolumeSize')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'volume_id': volume_id
            }

    @staticmethod
    def delete_ebs_snapshot(snapshot_id: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina un snapshot EBS

        Args:
            snapshot_id: ID del snapshot EBS
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            ec2 = get_aws_client('ec2', region)

            response = ec2.delete_snapshot(SnapshotId=snapshot_id)

            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'message': f'Snapshot EBS {snapshot_id} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'snapshot_id': snapshot_id
            }