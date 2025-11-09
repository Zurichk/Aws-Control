from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime

acm_bp = Blueprint('acm', __name__, url_prefix='/acm')

def get_acm_client():
    """Obtener cliente de ACM"""
    try:
        return boto3.client('acm')
    except Exception as e:
        flash(f'Error al conectar con ACM: {str(e)}', 'danger')
        return None

@acm_bp.route('/')
def index():
    """Listar todos los certificados"""
    acm_client = get_acm_client()
    if not acm_client:
        return redirect(url_for('index'))

    try:
        # Obtener certificados
        response = acm_client.list_certificates(
            MaxItems=100
        )

        certificates = []
        for cert_summary in response.get('CertificateSummaryList', []):
            # Obtener detalles completos del certificado
            try:
                cert_details = acm_client.describe_certificate(
                    CertificateArn=cert_summary['CertificateArn']
                )
                cert = cert_details['Certificate']
                cert.update(cert_summary)
                certificates.append(cert)
            except ClientError as e:
                # Si no podemos obtener detalles, usar el resumen
                certificates.append(cert_summary)

        return render_template('Seguridad/acm/index.html', certificates=certificates)

    except ClientError as e:
        flash(f'Error al listar certificados: {str(e)}', 'danger')
        return render_template('Seguridad/acm/index.html', certificates=[])

@acm_bp.route('/request', methods=['GET', 'POST'])
def request_certificate():
    """Solicitar un nuevo certificado"""
    if request.method == 'POST':
        domain_name = request.form.get('domain_name')
        validation_method = request.form.get('validation_method', 'DNS')
        subject_alternative_names = request.form.getlist('subject_alternative_names[]')
        key_algorithm = request.form.get('key_algorithm', 'RSA_2048')

        # Filtrar nombres alternativos vacíos
        subject_alternative_names = [name for name in subject_alternative_names if name.strip()]

        acm_client = get_acm_client()
        if not acm_client:
            return redirect(url_for('acm.index'))

        try:
            # Solicitar certificado
            params = {
                'DomainName': domain_name,
                'ValidationMethod': validation_method,
                'KeyAlgorithm': key_algorithm
            }

            if subject_alternative_names:
                params['SubjectAlternativeNames'] = subject_alternative_names

            response = acm_client.request_certificate(**params)

            certificate_arn = response['CertificateArn']
            flash(f'Certificado solicitado exitosamente. ARN: {certificate_arn}', 'success')

            return redirect(url_for('acm.describe_certificate', certificate_arn=certificate_arn))

        except ClientError as e:
            flash(f'Error al solicitar certificado: {str(e)}', 'danger')
            return render_template('Seguridad/acm/request_certificate.html')

    return render_template('Seguridad/acm/request_certificate.html')

@acm_bp.route('/delete/<path:certificate_arn>', methods=['POST'])
def delete_certificate(certificate_arn):
    """Eliminar un certificado"""
    acm_client = get_acm_client()
    if not acm_client:
        return redirect(url_for('acm.index'))

    try:
        acm_client.delete_certificate(CertificateArn=certificate_arn)
        flash('Certificado eliminado exitosamente', 'success')
    except ClientError as e:
        flash(f'Error al eliminar certificado: {str(e)}', 'danger')

    return redirect(url_for('acm.index'))

@acm_bp.route('/describe/<path:certificate_arn>')
def describe_certificate(certificate_arn):
    """Describir detalles de un certificado"""
    acm_client = get_acm_client()
    if not acm_client:
        return redirect(url_for('acm.index'))

    try:
        response = acm_client.describe_certificate(CertificateArn=certificate_arn)
        certificate = response['Certificate']

        return render_template('Seguridad/acm/describe_certificate.html', certificate=certificate)

    except ClientError as e:
        flash(f'Error al obtener detalles del certificado: {str(e)}', 'danger')
        return redirect(url_for('acm.index'))

# API Routes para AJAX
@acm_bp.route('/api/certificates')
def api_certificates():
    """API para obtener certificados en formato JSON"""
    acm_client = get_acm_client()
    if not acm_client:
        return jsonify({'error': 'No se pudo conectar con ACM'}), 500

    try:
        response = acm_client.list_certificates(MaxItems=100)
        return jsonify(response.get('CertificateSummaryList', []))
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

@acm_bp.route('/api/certificate/<path:certificate_arn>')
def api_certificate_details(certificate_arn):
    """API para obtener detalles de un certificado específico"""
    acm_client = get_acm_client()
    if not acm_client:
        return jsonify({'error': 'No se pudo conectar con ACM'}), 500

    try:
        response = acm_client.describe_certificate(CertificateArn=certificate_arn)
        return jsonify(response['Certificate'])
    except ClientError as e:
        return jsonify({'error': str(e)}), 500