from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('cloudfront', __name__)

@bp.route('/')
def index():
    return render_template('Redes/cloudfront/index.html')

@bp.route('/distributions')
def distributions():
    try:
        cf = get_aws_client('cloudfront')
        distributions = cf.list_distributions()
        dist_list = []
        if 'DistributionList' in distributions and 'Items' in distributions['DistributionList']:
            for dist in distributions['DistributionList']['Items']:
                dist_list.append({
                    'id': dist['Id'],
                    'domain': dist['DomainName'],
                    'status': dist['Status'],
                    'enabled': dist['Enabled'],
                    'origins': len(dist.get('Origins', {}).get('Items', []))
                })
        return render_template('Redes/cloudfront/distributions.html', distributions=dist_list)
    except Exception as e:
        flash(f'Error obteniendo distribuciones CloudFront: {str(e)}', 'error')
        return render_template('Redes/cloudfront/distributions.html', distributions=[])

@bp.route('/create_distribution', methods=['GET', 'POST'])
def create_distribution():
    if request.method == 'POST':
        try:
            cf = get_aws_client('cloudfront')
            s3 = get_aws_client('s3')

            # Obtener datos del formulario
            origin_domain = request.form.get('origin_domain')
            comment = request.form.get('comment', '')
            enabled = request.form.get('enabled') == 'on'
            price_class = request.form.get('price_class', 'PriceClass_All')

            # Verificar si el origen es un bucket S3
            if origin_domain.endswith('.s3.amazonaws.com') or '.s3.' in origin_domain:
                bucket_name = origin_domain.split('.')[0]
                try:
                    s3.head_bucket(Bucket=bucket_name)
                except Exception as e:
                    flash(f'Error: No se puede acceder al bucket S3 {bucket_name}: {str(e)}', 'error')
                    return redirect(url_for('cloudfront.create_distribution'))

            # Crear configuración de distribución
            distribution_config = {
                'CallerReference': f'cf-{int(__import__("time").time())}',
                'Comment': comment,
                'Enabled': enabled,
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'origin1',
                            'DomainName': origin_domain,
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'https-only',
                                'OriginSSLProtocols': {
                                    'Quantity': 1,
                                    'Items': ['TLSv1.2']
                                }
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'origin1',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {
                            'Forward': 'none'
                        }
                    },
                    'MinTTL': 0
                },
                'PriceClass': price_class
            }

            # Crear distribución
            response = cf.create_distribution(DistributionConfig=distribution_config)
            distribution_id = response['Distribution']['Id']

            flash(f'Distribución CloudFront creada exitosamente. ID: {distribution_id}', 'success')
            return redirect(url_for('cloudfront.distributions'))

        except Exception as e:
            flash(f'Error creando distribución CloudFront: {str(e)}', 'error')
            return redirect(url_for('cloudfront.create_distribution'))

    return render_template('Redes/cloudfront/create_distribution.html')

@bp.route('/delete_distribution/<distribution_id>', methods=['POST'])
def delete_distribution(distribution_id):
    try:
        cf = get_aws_client('cloudfront')

        # Obtener configuración actual de la distribución
        dist_config = cf.get_distribution_config(Id=distribution_id)
        etag = dist_config['ETag']

        # Deshabilitar la distribución primero si está habilitada
        if dist_config['Distribution']['DistributionConfig']['Enabled']:
            dist_config['Distribution']['DistributionConfig']['Enabled'] = False
            cf.update_distribution(
                Id=distribution_id,
                DistributionConfig=dist_config['Distribution']['DistributionConfig'],
                IfMatch=etag
            )
            flash('Distribución deshabilitada. Esperando propagación...', 'info')
            return redirect(url_for('cloudfront.distributions'))

        # Una vez deshabilitada, eliminar la distribución
        cf.delete_distribution(Id=distribution_id, IfMatch=etag)
        flash(f'Distribución {distribution_id} eliminada exitosamente', 'success')

    except Exception as e:
        flash(f'Error eliminando distribución: {str(e)}', 'error')

    return redirect(url_for('cloudfront.distributions'))

@bp.route('/update_distribution/<distribution_id>', methods=['GET', 'POST'])
def update_distribution(distribution_id):
    try:
        cf = get_aws_client('cloudfront')

        if request.method == 'POST':
            # Obtener configuración actual
            dist_config = cf.get_distribution_config(Id=distribution_id)
            etag = dist_config['ETag']
            config = dist_config['Distribution']['DistributionConfig']

            # Actualizar campos
            config['Comment'] = request.form.get('comment', config.get('Comment', ''))
            config['Enabled'] = request.form.get('enabled') == 'on'

            # Actualizar distribución
            cf.update_distribution(
                Id=distribution_id,
                DistributionConfig=config,
                IfMatch=etag
            )

            flash(f'Distribución {distribution_id} actualizada exitosamente', 'success')
            return redirect(url_for('cloudfront.distributions'))

        # GET: Mostrar formulario con datos actuales
        dist_config = cf.get_distribution_config(Id=distribution_id)
        config = dist_config['Distribution']['DistributionConfig']

        return render_template('Redes/cloudfront/update_distribution.html',
                             distribution_id=distribution_id,
                             config=config)

    except Exception as e:
        flash(f'Error actualizando distribución: {str(e)}', 'error')
        return redirect(url_for('cloudfront.distributions'))

@bp.route('/create_invalidation/<distribution_id>', methods=['GET', 'POST'])
def create_invalidation(distribution_id):
    if request.method == 'POST':
        try:
            cf = get_aws_client('cloudfront')

            # Obtener paths a invalidar
            paths = request.form.get('paths', '').strip()
            if not paths:
                flash('Debe especificar al menos una ruta para invalidar', 'error')
                return redirect(url_for('cloudfront.create_invalidation', distribution_id=distribution_id))

            # Convertir paths a lista
            path_list = [path.strip() for path in paths.split('\n') if path.strip()]

            # Crear invalidación
            invalidation_config = {
                'CallerReference': f'invalidation-{int(__import__("time").time())}',
                'Paths': {
                    'Quantity': len(path_list),
                    'Items': path_list
                }
            }

            response = cf.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch=invalidation_config
            )

            invalidation_id = response['Invalidation']['Id']
            flash(f'Invalidación creada exitosamente. ID: {invalidation_id}', 'success')
            return redirect(url_for('cloudfront.distributions'))

        except Exception as e:
            flash(f'Error creando invalidación: {str(e)}', 'error')
            return redirect(url_for('cloudfront.create_invalidation', distribution_id=distribution_id))

    return render_template('Redes/cloudfront/create_invalidation.html', distribution_id=distribution_id)