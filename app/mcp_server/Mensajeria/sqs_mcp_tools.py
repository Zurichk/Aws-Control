"""
SQS (Simple Queue Service) MCP Tools
Herramientas para gestión completa de colas SQS, mensajes y atributos
"""

import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class SQSMCPTools:
    """Herramientas MCP para gestión de SQS (Simple Queue Service)"""

    @staticmethod
    def list_sqs_queues(region: str = None, queue_name_prefix: str = None) -> Dict[str, Any]:
        """
        Lista todas las colas SQS en la región especificada

        Args:
            region: Región de AWS (opcional, usa default si no se especifica)
            queue_name_prefix: Prefijo para filtrar colas por nombre (opcional)

        Returns:
            Dict con lista de colas SQS y metadatos
        """
        try:
            sqs = get_aws_client('sqs', region)

            params = {}
            if queue_name_prefix:
                params['QueueNamePrefix'] = queue_name_prefix

            response = sqs.list_queues(**params)

            queues = []
            if 'QueueUrls' in response:
                for queue_url in response['QueueUrls']:
                    queue_name = queue_url.split('/')[-1]

                    # Obtener atributos de la cola
                    try:
                        attrs_response = sqs.get_queue_attributes(
                            QueueUrl=queue_url,
                            AttributeNames=['All']
                        )
                        attributes = attrs_response['Attributes']
                    except Exception:
                        attributes = {}

                    queues.append({
                        'QueueUrl': queue_url,
                        'QueueName': queue_name,
                        'ApproximateNumberOfMessages': attributes.get('ApproximateNumberOfMessages', '0'),
                        'ApproximateNumberOfMessagesNotVisible': attributes.get('ApproximateNumberOfMessagesNotVisible', '0'),
                        'ApproximateNumberOfMessagesDelayed': attributes.get('ApproximateNumberOfMessagesDelayed', '0'),
                        'VisibilityTimeout': attributes.get('VisibilityTimeout', '30'),
                        'MaximumMessageSize': attributes.get('MaximumMessageSize', '262144'),
                        'MessageRetentionPeriod': attributes.get('MessageRetentionPeriod', '345600'),
                        'DelaySeconds': attributes.get('DelaySeconds', '0'),
                        'ReceiveMessageWaitTimeSeconds': attributes.get('ReceiveMessageWaitTimeSeconds', '0'),
                        'FifoQueue': attributes.get('FifoQueue', 'false'),
                        'ContentBasedDeduplication': attributes.get('ContentBasedDeduplication', 'false'),
                        'CreatedTimestamp': attributes.get('CreatedTimestamp', ''),
                        'LastModifiedTimestamp': attributes.get('LastModifiedTimestamp', '')
                    })

            return {
                'success': True,
                'queues': queues,
                'count': len(queues),
                'region': region or 'default',
                'queue_name_prefix': queue_name_prefix
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queues': [],
                'count': 0
            }

    @staticmethod
    def create_sqs_queue(
        queue_name: str,
        region: str = None,
        attributes: Dict[str, str] = None,
        fifo_queue: bool = False
    ) -> Dict[str, Any]:
        """
        Crea una nueva cola SQS

        Args:
            queue_name: Nombre de la cola
            region: Región de AWS
            attributes: Atributos de la cola (opcional)
            fifo_queue: Si es una cola FIFO (opcional)

        Returns:
            Dict con información de la cola creada
        """
        try:
            sqs = get_aws_client('sqs', region)

            # Asegurar que el nombre tenga la extensión correcta para colas FIFO
            if fifo_queue and not queue_name.endswith('.fifo'):
                queue_name += '.fifo'

            params = {'QueueName': queue_name}

            # Configurar atributos
            queue_attributes = {}

            if fifo_queue:
                queue_attributes['FifoQueue'] = 'true'
                # Para colas FIFO, el ContentBasedDeduplication es recomendado
                if attributes and 'ContentBasedDeduplication' not in attributes:
                    queue_attributes['ContentBasedDeduplication'] = 'true'

            # Agregar atributos personalizados
            if attributes:
                queue_attributes.update(attributes)

            if queue_attributes:
                params['Attributes'] = queue_attributes

            response = sqs.create_queue(**params)

            return {
                'success': True,
                'queue_url': response['QueueUrl'],
                'queue_name': queue_name,
                'region': region or 'default',
                'fifo_queue': fifo_queue,
                'attributes': queue_attributes
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_name': queue_name
            }

    @staticmethod
    def delete_sqs_queue(queue_url: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina una cola SQS

        Args:
            queue_url: URL de la cola SQS
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            sqs = get_aws_client('sqs', region)

            sqs.delete_queue(QueueUrl=queue_url)

            queue_name = queue_url.split('/')[-1]

            return {
                'success': True,
                'queue_url': queue_url,
                'queue_name': queue_name,
                'message': f'Cola SQS {queue_name} eliminada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_url': queue_url
            }

    @staticmethod
    def send_message(
        queue_url: str,
        message_body: str,
        region: str = None,
        message_group_id: str = None,
        message_deduplication_id: str = None,
        delay_seconds: int = None,
        message_attributes: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Envía un mensaje a una cola SQS

        Args:
            queue_url: URL de la cola SQS
            message_body: Contenido del mensaje
            region: Región de AWS
            message_group_id: ID del grupo de mensajes (para colas FIFO)
            message_deduplication_id: ID de deduplicación (para colas FIFO)
            delay_seconds: Segundos de delay antes de que el mensaje esté disponible
            message_attributes: Atributos del mensaje (opcional)

        Returns:
            Dict con resultado del envío
        """
        try:
            sqs = get_aws_client('sqs', region)

            params = {
                'QueueUrl': queue_url,
                'MessageBody': message_body
            }

            if message_group_id:
                params['MessageGroupId'] = message_group_id

            if message_deduplication_id:
                params['MessageDeduplicationId'] = message_deduplication_id

            if delay_seconds is not None:
                params['DelaySeconds'] = delay_seconds

            if message_attributes:
                params['MessageAttributes'] = {}
                for key, value in message_attributes.items():
                    if isinstance(value, str):
                        attr_value = {'DataType': 'String', 'StringValue': value}
                    elif isinstance(value, (int, float)):
                        attr_value = {'DataType': 'Number', 'StringValue': str(value)}
                    else:
                        attr_value = {'DataType': 'String', 'StringValue': str(value)}

                    params['MessageAttributes'][key] = attr_value

            response = sqs.send_message(**params)

            return {
                'success': True,
                'message_id': response.get('MessageId', ''),
                'queue_url': queue_url,
                'message_body': message_body[:100] + '...' if len(message_body) > 100 else message_body,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_url': queue_url
            }

    @staticmethod
    def receive_message(
        queue_url: str,
        region: str = None,
        max_number_of_messages: int = 1,
        visibility_timeout: int = None,
        wait_time_seconds: int = None
    ) -> Dict[str, Any]:
        """
        Recibe mensajes de una cola SQS

        Args:
            queue_url: URL de la cola SQS
            region: Región de AWS
            max_number_of_messages: Número máximo de mensajes a recibir (1-10)
            visibility_timeout: Timeout de visibilidad en segundos
            wait_time_seconds: Tiempo de espera largo en segundos (0-20)

        Returns:
            Dict con mensajes recibidos
        """
        try:
            sqs = get_aws_client('sqs', region)

            params = {'QueueUrl': queue_url}

            if max_number_of_messages and 1 <= max_number_of_messages <= 10:
                params['MaxNumberOfMessages'] = max_number_of_messages

            if visibility_timeout is not None:
                params['VisibilityTimeout'] = visibility_timeout

            if wait_time_seconds is not None and 0 <= wait_time_seconds <= 20:
                params['WaitTimeSeconds'] = wait_time_seconds

            response = sqs.receive_message(**params)

            messages = []
            if 'Messages' in response:
                for msg in response['Messages']:
                    messages.append({
                        'MessageId': msg.get('MessageId', ''),
                        'ReceiptHandle': msg.get('ReceiptHandle', ''),
                        'Body': msg.get('Body', ''),
                        'MD5OfBody': msg.get('MD5OfBody', ''),
                        'Attributes': msg.get('Attributes', {}),
                        'MessageAttributes': msg.get('MessageAttributes', {})
                    })

            return {
                'success': True,
                'messages': messages,
                'count': len(messages),
                'queue_url': queue_url,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'messages': [],
                'count': 0,
                'queue_url': queue_url
            }

    @staticmethod
    def purge_queue(queue_url: str, region: str = None) -> Dict[str, Any]:
        """
        Purga todos los mensajes de una cola SQS

        Args:
            queue_url: URL de la cola SQS
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            sqs = get_aws_client('sqs', region)

            sqs.purge_queue(QueueUrl=queue_url)

            queue_name = queue_url.split('/')[-1]

            return {
                'success': True,
                'queue_url': queue_url,
                'queue_name': queue_name,
                'message': f'Cola SQS {queue_name} purgada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_url': queue_url
            }

    @staticmethod
    def get_queue_attributes(queue_url: str, region: str = None, attribute_names: List[str] = None) -> Dict[str, Any]:
        """
        Obtiene atributos de una cola SQS

        Args:
            queue_url: URL de la cola SQS
            region: Región de AWS
            attribute_names: Lista de nombres de atributos a obtener (opcional, obtiene todos si no se especifica)

        Returns:
            Dict con atributos de la cola
        """
        try:
            sqs = get_aws_client('sqs', region)

            params = {'QueueUrl': queue_url}

            if attribute_names:
                params['AttributeNames'] = attribute_names
            else:
                params['AttributeNames'] = ['All']

            response = sqs.get_queue_attributes(**params)

            queue_name = queue_url.split('/')[-1]

            return {
                'success': True,
                'queue_url': queue_url,
                'queue_name': queue_name,
                'attributes': response.get('Attributes', {}),
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_url': queue_url,
                'attributes': {}
            }

    @staticmethod
    def set_queue_attributes(queue_url: str, attributes: Dict[str, str], region: str = None) -> Dict[str, Any]:
        """
        Establece atributos de una cola SQS

        Args:
            queue_url: URL de la cola SQS
            attributes: Diccionario de atributos a establecer
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            sqs = get_aws_client('sqs', region)

            params = {
                'QueueUrl': queue_url,
                'Attributes': attributes
            }

            sqs.set_queue_attributes(**params)

            queue_name = queue_url.split('/')[-1]

            return {
                'success': True,
                'queue_url': queue_url,
                'queue_name': queue_name,
                'attributes_set': attributes,
                'message': f'Atributos de cola SQS {queue_name} actualizados exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'queue_url': queue_url,
                'attributes': attributes
            }