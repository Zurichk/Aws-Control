"""
ACM MCP Tools
Herramientas MCP para gestión de AWS Certificate Manager
"""

import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional

class AcmMCPTools:
    """Herramientas MCP para AWS Certificate Manager"""

    def __init__(self):
        self.client = None

    def _get_client(self):
        """Obtener cliente de ACM"""
        if not self.client:
            try:
                self.client = boto3.client('acm')
            except Exception as e:
                raise ConnectionError(f"Error al conectar con ACM: {str(e)}")
        return self.client

    def list_certificates(self, max_items: int = 100) -> Dict[str, Any]:
        """
        Listar todos los certificados en ACM

        Args:
            max_items: Número máximo de certificados a retornar (default: 100)

        Returns:
            Dict con lista de certificados
        """
        try:
            client = self._get_client()
            response = client.list_certificates(MaxItems=max_items)

            certificates = []
            for cert_summary in response.get('CertificateSummaryList', []):
                # Obtener detalles completos del certificado
                try:
                    cert_details = client.describe_certificate(
                        CertificateArn=cert_summary['CertificateArn']
                    )
                    cert = cert_details['Certificate']
                    cert.update(cert_summary)
                    certificates.append({
                        'certificate_arn': cert.get('CertificateArn'),
                        'domain_name': cert.get('DomainName'),
                        'subject_alternative_names': cert.get('SubjectAlternativeNames', []),
                        'status': cert.get('Status'),
                        'type': cert.get('Type'),
                        'key_algorithm': cert.get('KeyAlgorithm'),
                        'issuer': cert.get('Issuer'),
                        'not_before': cert.get('NotBefore').isoformat() if cert.get('NotBefore') else None,
                        'not_after': cert.get('NotAfter').isoformat() if cert.get('NotAfter') else None,
                        'created_at': cert.get('CreatedAt').isoformat() if cert.get('CreatedAt') else None,
                        'failure_reason': cert.get('FailureReason'),
                        'validation_method': cert.get('ValidationMethod')
                    })
                except ClientError:
                    # Si no podemos obtener detalles, usar el resumen
                    certificates.append({
                        'certificate_arn': cert_summary.get('CertificateArn'),
                        'domain_name': cert_summary.get('DomainName'),
                        'status': cert_summary.get('Status')
                    })

            return {
                'success': True,
                'certificates': certificates,
                'count': len(certificates)
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e),
                'certificates': [],
                'count': 0
            }

    def request_certificate(self, domain_name: str, validation_method: str = 'DNS',
                          subject_alternative_names: List[str] = None,
                          key_algorithm: str = 'RSA_2048') -> Dict[str, Any]:
        """
        Solicitar un nuevo certificado SSL/TLS

        Args:
            domain_name: Nombre de dominio principal
            validation_method: Método de validación ('DNS' o 'EMAIL')
            subject_alternative_names: Lista de nombres alternativos del sujeto
            key_algorithm: Algoritmo de clave ('RSA_2048', 'RSA_3072', 'RSA_4096', 'EC_prime256v1', etc.)

        Returns:
            Dict con resultado de la solicitud
        """
        try:
            client = self._get_client()

            params = {
                'DomainName': domain_name,
                'ValidationMethod': validation_method,
                'KeyAlgorithm': key_algorithm
            }

            if subject_alternative_names:
                params['SubjectAlternativeNames'] = subject_alternative_names

            response = client.request_certificate(**params)

            return {
                'success': True,
                'certificate_arn': response.get('CertificateArn'),
                'domain_name': domain_name,
                'validation_method': validation_method
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def describe_certificate(self, certificate_arn: str) -> Dict[str, Any]:
        """
        Obtener detalles completos de un certificado

        Args:
            certificate_arn: ARN del certificado

        Returns:
            Dict con detalles del certificado
        """
        try:
            client = self._get_client()
            response = client.describe_certificate(CertificateArn=certificate_arn)

            certificate = response['Certificate']

            # Formatear la respuesta
            cert_details = {
                'certificate_arn': certificate.get('CertificateArn'),
                'domain_name': certificate.get('DomainName'),
                'subject_alternative_names': certificate.get('SubjectAlternativeNames', []),
                'status': certificate.get('Status'),
                'type': certificate.get('Type'),
                'key_algorithm': certificate.get('KeyAlgorithm'),
                'issuer': certificate.get('Issuer'),
                'not_before': certificate.get('NotBefore').isoformat() if certificate.get('NotBefore') else None,
                'not_after': certificate.get('NotAfter').isoformat() if certificate.get('NotAfter') else None,
                'created_at': certificate.get('CreatedAt').isoformat() if certificate.get('CreatedAt') else None,
                'failure_reason': certificate.get('FailureReason'),
                'validation_method': certificate.get('ValidationMethod'),
                'renewal_eligibility': certificate.get('RenewalEligibility'),
                'domain_validation_options': []
            }

            # Agregar opciones de validación de dominio
            if certificate.get('DomainValidationOptions'):
                for option in certificate['DomainValidationOptions']:
                    cert_details['domain_validation_options'].append({
                        'domain_name': option.get('DomainName'),
                        'validation_domain': option.get('ValidationDomain'),
                        'validation_status': option.get('ValidationStatus'),
                        'validation_method': option.get('ValidationMethod'),
                        'validation_emails': option.get('ValidationEmails', []),
                        'resource_record': {
                            'name': option.get('ResourceRecord', {}).get('Name'),
                            'type': option.get('ResourceRecord', {}).get('Type'),
                            'value': option.get('ResourceRecord', {}).get('Value')
                        } if option.get('ResourceRecord') else None
                    })

            return {
                'success': True,
                'certificate': cert_details
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_certificate(self, certificate_arn: str) -> Dict[str, Any]:
        """
        Eliminar un certificado

        Args:
            certificate_arn: ARN del certificado a eliminar

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            client = self._get_client()
            client.delete_certificate(CertificateArn=certificate_arn)

            return {
                'success': True,
                'certificate_arn': certificate_arn,
                'message': 'Certificado eliminado exitosamente'
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_certificate_validation_status(self, certificate_arn: str) -> Dict[str, Any]:
        """
        Obtener el estado de validación de un certificado

        Args:
            certificate_arn: ARN del certificado

        Returns:
            Dict con estado de validación
        """
        try:
            client = self._get_client()
            response = client.describe_certificate(CertificateArn=certificate_arn)

            certificate = response['Certificate']

            validation_status = {
                'certificate_arn': certificate.get('CertificateArn'),
                'domain_name': certificate.get('DomainName'),
                'status': certificate.get('Status'),
                'validation_method': certificate.get('ValidationMethod'),
                'domain_validation_options': []
            }

            # Agregar opciones de validación
            if certificate.get('DomainValidationOptions'):
                for option in certificate['DomainValidationOptions']:
                    validation_status['domain_validation_options'].append({
                        'domain_name': option.get('DomainName'),
                        'validation_status': option.get('ValidationStatus'),
                        'validation_method': option.get('ValidationMethod'),
                        'resource_record': {
                            'name': option.get('ResourceRecord', {}).get('Name'),
                            'type': option.get('ResourceRecord', {}).get('Type'),
                            'value': option.get('ResourceRecord', {}).get('Value')
                        } if option.get('ResourceRecord') else None,
                        'validation_emails': option.get('ValidationEmails', [])
                    })

            return {
                'success': True,
                'validation_status': validation_status
            }

        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }