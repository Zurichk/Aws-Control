"""
Herramientas MCP para Amazon Kinesis
Gestión de streams de datos en tiempo real
"""
import boto3
import json
from typing import Dict, Any, List
from ...utils.aws_client import get_aws_client


class KinesisMCPTools:
    """Herramientas MCP para operaciones con Amazon Kinesis"""

    def create_stream(self, stream_name: str, shard_count: int = 1, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Crea un nuevo stream de Kinesis

        Args:
            stream_name: Nombre del stream
            shard_count: Número de shards (default: 1)
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            kinesis = get_aws_client('kinesis', region)
            kinesis.create_stream(
                StreamName=stream_name,
                ShardCount=shard_count
            )

            return {
                'success': True,
                'message': f'Stream "{stream_name}" creado exitosamente con {shard_count} shard(s)',
                'stream_name': stream_name,
                'shard_count': shard_count,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creando stream: {str(e)}',
                'stream_name': stream_name,
                'region': region
            }

    def delete_stream(self, stream_name: str, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Elimina un stream de Kinesis

        Args:
            stream_name: Nombre del stream a eliminar
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            kinesis = get_aws_client('kinesis', region)
            kinesis.delete_stream(StreamName=stream_name)

            return {
                'success': True,
                'message': f'Stream "{stream_name}" eliminado exitosamente',
                'stream_name': stream_name,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error eliminando stream: {str(e)}',
                'stream_name': stream_name,
                'region': region
            }

    def put_record(self, stream_name: str, data: str, partition_key: str, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Envía un registro a un stream de Kinesis

        Args:
            stream_name: Nombre del stream
            data: Datos del registro (string)
            partition_key: Clave de partición
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            kinesis = get_aws_client('kinesis', region)

            # Convertir datos a bytes
            data_bytes = data.encode('utf-8')

            response = kinesis.put_record(
                StreamName=stream_name,
                Data=data_bytes,
                PartitionKey=partition_key
            )

            return {
                'success': True,
                'message': 'Registro enviado exitosamente',
                'stream_name': stream_name,
                'shard_id': response['ShardId'],
                'sequence_number': response['SequenceNumber'],
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error enviando registro: {str(e)}',
                'stream_name': stream_name,
                'region': region
            }

    def get_records(self, stream_name: str, shard_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Obtiene registros de un shard específico en un stream de Kinesis

        Args:
            stream_name: Nombre del stream
            shard_id: ID del shard
            region: Región de AWS

        Returns:
            Dict con los registros obtenidos
        """
        try:
            kinesis = get_aws_client('kinesis', region)

            # Obtener iterador de shard
            iterator_response = kinesis.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType='TRIM_HORIZON'
            )

            shard_iterator = iterator_response['ShardIterator']

            # Obtener registros
            records_response = kinesis.get_records(ShardIterator=shard_iterator)

            records = []
            for record in records_response.get('Records', []):
                records.append({
                    'sequence_number': record['SequenceNumber'],
                    'partition_key': record['PartitionKey'],
                    'data': record['Data'].decode('utf-8') if isinstance(record['Data'], bytes) else str(record['Data']),
                    'approximate_arrival_timestamp': record.get('ApproximateArrivalTimestamp', '').isoformat() if record.get('ApproximateArrivalTimestamp') else ''
                })

            return {
                'success': True,
                'message': f'Encontrados {len(records)} registro(s)',
                'stream_name': stream_name,
                'shard_id': shard_id,
                'records': records,
                'record_count': len(records),
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error obteniendo registros: {str(e)}',
                'stream_name': stream_name,
                'shard_id': shard_id,
                'region': region
            }