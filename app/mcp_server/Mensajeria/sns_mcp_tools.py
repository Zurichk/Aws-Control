"""
SNS (Simple Notification Service) MCP Tools
Herramientas para gestión completa de tópicos SNS, suscripciones y mensajes
"""

import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class SNSMCPTools:
    """Herramientas MCP para gestión de SNS (Simple Notification Service)"""

    @staticmethod
    def list_sns_topics(region: str = None) -> Dict[str, Any]:
        """
        Lista todos los tópicos SNS en la región especificada

        Args:
            region: Región de AWS (opcional, usa default si no se especifica)

        Returns:
            Dict con lista de tópicos SNS y metadatos
        """
        try:
            sns = get_aws_client('sns', region)

            response = sns.list_topics()

            topics = []
            for topic in response['Topics']:
                topic_arn = topic['TopicArn']
                topic_name = topic_arn.split(':')[-1]

                # Obtener atributos del tópico
                try:
                    attrs_response = sns.get_topic_attributes(TopicArn=topic_arn)
                    attributes = attrs_response['Attributes']
                except Exception:
                    attributes = {}

                topics.append({
                    'TopicArn': topic_arn,
                    'TopicName': topic_name,
                    'DisplayName': attributes.get('DisplayName', ''),
                    'DeliveryPolicy': attributes.get('DeliveryPolicy', ''),
                    'EffectiveDeliveryPolicy': attributes.get('EffectiveDeliveryPolicy', ''),
                    'Owner': attributes.get('Owner', ''),
                    'SubscriptionsConfirmed': attributes.get('SubscriptionsConfirmed', '0'),
                    'SubscriptionsDeleted': attributes.get('SubscriptionsDeleted', '0'),
                    'SubscriptionsPending': attributes.get('SubscriptionsPending', '0')
                })

            return {
                'success': True,
                'topics': topics,
                'count': len(topics),
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topics': [],
                'count': 0
            }

    @staticmethod
    def create_sns_topic(
        name: str,
        region: str = None,
        attributes: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo tópico SNS

        Args:
            name: Nombre del tópico
            region: Región de AWS
            attributes: Atributos adicionales del tópico (opcional)

        Returns:
            Dict con información del tópico creado
        """
        try:
            sns = get_aws_client('sns', region)

            params = {'Name': name}

            response = sns.create_topic(**params)

            topic_arn = response['TopicArn']

            # Establecer atributos adicionales si se proporcionaron
            if attributes:
                attr_updates = []
                for key, value in attributes.items():
                    attr_updates.append({
                        'AttributeName': key,
                        'AttributeValue': value
                    })

                for attr_update in attr_updates:
                    sns.set_topic_attributes(
                        TopicArn=topic_arn,
                        AttributeName=attr_update['AttributeName'],
                        AttributeValue=attr_update['AttributeValue']
                    )

            return {
                'success': True,
                'topic_arn': topic_arn,
                'topic_name': name,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topic_name': name
            }

    @staticmethod
    def delete_sns_topic(topic_arn: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina un tópico SNS

        Args:
            topic_arn: ARN del tópico SNS
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            sns = get_aws_client('sns', region)

            sns.delete_topic(TopicArn=topic_arn)

            return {
                'success': True,
                'topic_arn': topic_arn,
                'message': f'Tópico SNS {topic_arn} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topic_arn': topic_arn
            }

    @staticmethod
    def list_subscriptions(region: str = None, topic_arn: str = None) -> Dict[str, Any]:
        """
        Lista suscripciones SNS

        Args:
            region: Región de AWS
            topic_arn: Filtrar por ARN de tópico específico (opcional)

        Returns:
            Dict con lista de suscripciones
        """
        try:
            sns = get_aws_client('sns', region)

            subscriptions = []

            if topic_arn:
                # Listar suscripciones de un tópico específico
                response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
                subscriptions = response['Subscriptions']
            else:
                # Listar todas las suscripciones
                response = sns.list_subscriptions()
                subscriptions = response['Subscriptions']

            formatted_subscriptions = []
            for sub in subscriptions:
                formatted_subscriptions.append({
                    'SubscriptionArn': sub.get('SubscriptionArn', ''),
                    'TopicArn': sub.get('TopicArn', ''),
                    'Protocol': sub.get('Protocol', ''),
                    'Endpoint': sub.get('Endpoint', ''),
                    'Owner': sub.get('Owner', ''),
                    'SubscriptionPrincipal': sub.get('SubscriptionPrincipal', '')
                })

            return {
                'success': True,
                'subscriptions': formatted_subscriptions,
                'count': len(formatted_subscriptions),
                'region': region or 'default',
                'topic_filter': topic_arn
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'subscriptions': [],
                'count': 0
            }

    @staticmethod
    def create_subscription(
        topic_arn: str,
        protocol: str,
        endpoint: str,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Crea una suscripción a un tópico SNS

        Args:
            topic_arn: ARN del tópico SNS
            protocol: Protocolo de entrega (http, https, email, sms, sqs, lambda, etc.)
            endpoint: Endpoint para la entrega (URL, email, ARN de cola, etc.)
            region: Región de AWS

        Returns:
            Dict con información de la suscripción creada
        """
        try:
            sns = get_aws_client('sns', region)

            response = sns.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )

            return {
                'success': True,
                'subscription_arn': response.get('SubscriptionArn', ''),
                'topic_arn': topic_arn,
                'protocol': protocol,
                'endpoint': endpoint,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topic_arn': topic_arn,
                'protocol': protocol,
                'endpoint': endpoint
            }

    @staticmethod
    def delete_subscription(subscription_arn: str, region: str = None) -> Dict[str, Any]:
        """
        Elimina una suscripción SNS

        Args:
            subscription_arn: ARN de la suscripción
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            sns = get_aws_client('sns', region)

            sns.unsubscribe(SubscriptionArn=subscription_arn)

            return {
                'success': True,
                'subscription_arn': subscription_arn,
                'message': f'Suscripción SNS {subscription_arn} eliminada exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'subscription_arn': subscription_arn
            }

    @staticmethod
    def publish_message(
        topic_arn: str,
        message: str,
        subject: str = None,
        message_attributes: Dict[str, Any] = None,
        region: str = None
    ) -> Dict[str, Any]:
        """
        Publica un mensaje en un tópico SNS

        Args:
            topic_arn: ARN del tópico SNS
            message: Contenido del mensaje
            subject: Asunto del mensaje (opcional, para email)
            message_attributes: Atributos del mensaje (opcional)
            region: Región de AWS

        Returns:
            Dict con resultado de la publicación
        """
        try:
            sns = get_aws_client('sns', region)

            params = {
                'TopicArn': topic_arn,
                'Message': message
            }

            if subject:
                params['Subject'] = subject

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

            response = sns.publish(**params)

            return {
                'success': True,
                'message_id': response.get('MessageId', ''),
                'topic_arn': topic_arn,
                'message': message[:100] + '...' if len(message) > 100 else message,
                'region': region or 'default'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'topic_arn': topic_arn
            }