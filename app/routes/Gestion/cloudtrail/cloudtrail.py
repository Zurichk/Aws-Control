"""
Rutas web para AWS CloudTrail
Auditoría y monitoreo de actividad en AWS
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
from app.utils.aws_client import get_aws_client

cloudtrail_bp = Blueprint('cloudtrail', __name__, url_prefix='/cloudtrail')


@cloudtrail_bp.route('/')
def index():
    """Página principal de CloudTrail"""
    return render_template('Gestion/cloudtrail/index.html')


@cloudtrail_bp.route('/trails')
def trails():
    """Lista todos los trails de CloudTrail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')
        response = cloudtrail.describe_trails()

        trails = []
        for trail in response.get('trailList', []):
            trail_info = {
                'name': trail.get('Name'),
                's3_bucket_name': trail.get('S3BucketName'),
                's3_key_prefix': trail.get('S3KeyPrefix', ''),
                'sns_topic_name': trail.get('SnsTopicName', ''),
                'include_global_service_events': trail.get('IncludeGlobalServiceEvents', False),
                'is_multi_region_trail': trail.get('IsMultiRegionTrail', False),
                'trail_arn': trail.get('TrailARN'),
                'log_file_validation_enabled': trail.get('LogFileValidationEnabled', False),
                'is_organization_trail': trail.get('IsOrganizationTrail', False),
                'kms_key_id': trail.get('KmsKeyId', ''),
                'has_custom_event_selectors': len(trail.get('EventSelectors', [])) > 0,
                'has_insight_selectors': len(trail.get('InsightSelectors', [])) > 0
            }
            trails.append(trail_info)

        return render_template('Gestion/cloudtrail/trails.html', trails=trails)
    except Exception as e:
        flash(f'Error obteniendo trails: {str(e)}', 'error')
        return render_template('Gestion/cloudtrail/trails.html', trails=[])


@cloudtrail_bp.route('/create-trail', methods=['GET', 'POST'])
def create_trail():
    """Crea un nuevo trail de CloudTrail"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            s3_bucket_name = request.form.get('s3_bucket_name')
            s3_key_prefix = request.form.get('s3_key_prefix')
            sns_topic_name = request.form.get('sns_topic_name')
            include_global_service_events = request.form.get('include_global_service_events') == 'on'
            is_multi_region_trail = request.form.get('is_multi_region_trail') == 'on'
            enable_log_file_validation = request.form.get('enable_log_file_validation') == 'on'
            kms_key_id = request.form.get('kms_key_id')
            is_organization_trail = request.form.get('is_organization_trail') == 'on'

            if not name or not s3_bucket_name:
                flash('Nombre del trail y bucket S3 son requeridos', 'error')
                return redirect(request.url)

            cloudtrail = get_aws_client('cloudtrail')

            params = {
                'Name': name,
                'S3BucketName': s3_bucket_name,
                'IncludeGlobalServiceEvents': include_global_service_events,
                'IsMultiRegionTrail': is_multi_region_trail,
                'EnableLogFileValidation': enable_log_file_validation,
                'IsOrganizationTrail': is_organization_trail
            }

            if s3_key_prefix:
                params['S3KeyPrefix'] = s3_key_prefix

            if sns_topic_name:
                params['SnsTopicName'] = sns_topic_name

            if kms_key_id:
                params['KmsKeyId'] = kms_key_id

            response = cloudtrail.create_trail(**params)

            flash(f'Trail {name} creado exitosamente. ARN: {response.get("TrailARN", "N/A")}', 'success')
            return redirect(url_for('cloudtrail.trails'))

        except Exception as e:
            flash(f'Error creando trail: {str(e)}', 'error')
            return redirect(request.url)

    # GET request - obtener buckets S3 disponibles
    try:
        s3 = get_aws_client('s3')
        buckets_response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in buckets_response.get('Buckets', [])]

        # Obtener topics SNS disponibles
        sns = get_aws_client('sns')
        topics_response = sns.list_topics()
        topics = [topic['TopicArn'].split(':')[-1] for topic in topics_response.get('Topics', [])]

        # Obtener claves KMS disponibles
        kms = get_aws_client('kms')
        keys_response = kms.list_keys()
        keys = [key['KeyId'] for key in keys_response.get('Keys', [])]

        return render_template('Gestion/cloudtrail/create_trail.html',
                             buckets=buckets, topics=topics, keys=keys)
    except Exception as e:
        flash(f'Error obteniendo recursos disponibles: {str(e)}', 'error')
        return render_template('Gestion/cloudtrail/create_trail.html',
                             buckets=[], topics=[], keys=[])


@cloudtrail_bp.route('/trail/<trail_name>')
def trail_detail(trail_name):
    """Obtiene detalles de un trail específico"""
    try:
        cloudtrail = get_aws_client('cloudtrail')

        # Obtener información del trail
        trail_response = cloudtrail.describe_trails(trailNameList=[trail_name])
        if not trail_response.get('trailList'):
            flash('Trail no encontrado', 'error')
            return redirect(url_for('cloudtrail.trails'))

        trail = trail_response['trailList'][0]

        # Obtener status del trail
        status_response = cloudtrail.get_trail_status(Name=trail_name)
        status = status_response

        # Obtener event selectors
        try:
            selectors_response = cloudtrail.get_event_selectors(TrailName=trail_name)
            event_selectors = selectors_response.get('EventSelectors', [])
        except:
            event_selectors = []

        # Obtener insight selectors
        try:
            insights_response = cloudtrail.get_insight_selectors(TrailName=trail_name)
            insight_selectors = insights_response.get('InsightSelectors', [])
        except:
            insight_selectors = []

        trail_detail = {
            'name': trail.get('Name'),
            's3_bucket_name': trail.get('S3BucketName'),
            's3_key_prefix': trail.get('S3KeyPrefix', ''),
            'sns_topic_name': trail.get('SnsTopicName', ''),
            'include_global_service_events': trail.get('IncludeGlobalServiceEvents', False),
            'is_multi_region_trail': trail.get('IsMultiRegionTrail', False),
            'trail_arn': trail.get('TrailARN'),
            'log_file_validation_enabled': trail.get('LogFileValidationEnabled', False),
            'is_organization_trail': trail.get('IsOrganizationTrail', False),
            'kms_key_id': trail.get('KmsKeyId', ''),
            'status': status,
            'event_selectors': event_selectors,
            'insight_selectors': insight_selectors
        }

        return render_template('Gestion/cloudtrail/trail_detail.html', trail=trail_detail)
    except Exception as e:
        flash(f'Error obteniendo detalles del trail: {str(e)}', 'error')
        return redirect(url_for('cloudtrail.trails'))


@cloudtrail_bp.route('/events')
def events():
    """Lista eventos recientes de CloudTrail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')

        # Parámetros de búsqueda
        lookup_attributes = []
        max_results = int(request.args.get('max_results', 50))
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        params = {
            'MaxResults': min(max_results, 50)
        }

        if start_time:
            params['StartTime'] = start_time
        if end_time:
            params['EndTime'] = end_time

        # Agregar filtros si se especifican
        user_name = request.args.get('user_name')
        event_name = request.args.get('event_name')
        resource_type = request.args.get('resource_type')

        if user_name:
            lookup_attributes.append({
                'AttributeKey': 'Username',
                'AttributeValue': user_name
            })

        if event_name:
            lookup_attributes.append({
                'AttributeKey': 'EventName',
                'AttributeValue': event_name
            })

        if resource_type:
            lookup_attributes.append({
                'AttributeKey': 'ResourceType',
                'AttributeValue': resource_type
            })

        if lookup_attributes:
            params['LookupAttributes'] = lookup_attributes

        response = cloudtrail.lookup_events(**params)

        events = []
        for event in response.get('Events', []):
            event_info = {
                'event_id': event.get('EventId'),
                'event_name': event.get('EventName'),
                'event_time': event.get('EventTime'),
                'event_source': event.get('EventSource'),
                'username': event.get('Username', 'N/A'),
                'resources': event.get('Resources', []),
                'cloud_trail_event': event.get('CloudTrailEvent', '{}')
            }
            events.append(event_info)

        return render_template('Gestion/cloudtrail/events.html',
                             events=events,
                             filters={
                                 'user_name': user_name,
                                 'event_name': event_name,
                                 'resource_type': resource_type,
                                 'max_results': max_results
                             })
    except Exception as e:
        flash(f'Error obteniendo eventos: {str(e)}', 'error')
        return render_template('Gestion/cloudtrail/events.html', events=[], filters={})


@cloudtrail_bp.route('/insights')
def insights():
    """Lista insights de CloudTrail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')

        # Obtener métricas de insights
        response = cloudtrail.get_insight_selectors()

        insights_data = []
        for selector in response.get('InsightSelectors', []):
            insight_info = {
                'insight_type': selector.get('InsightType'),
                'event_name': 'N/A',  # CloudTrail no proporciona nombres de eventos en insights básicos
                'event_source': 'N/A',
                'insight_duration': 'N/A',
                'baseline_duration': 'N/A',
                'baseline_events': 'N/A',
                'insight_events': 'N/A'
            }
            insights_data.append(insight_info)

        # Si no hay insights configurados, mostrar mensaje informativo
        if not insights_data:
            insights_data = [{
                'insight_type': 'No configurado',
                'event_name': 'Configure insights en sus trails para ver métricas',
                'event_source': 'N/A',
                'insight_duration': 'N/A',
                'baseline_duration': 'N/A',
                'baseline_events': 'N/A',
                'insight_events': 'N/A'
            }]

        return render_template('Gestion/cloudtrail/insights.html', insights=insights_data)
    except Exception as e:
        flash(f'Error obteniendo insights: {str(e)}', 'error')
        return render_template('Gestion/cloudtrail/insights.html', insights=[])


@cloudtrail_bp.route('/trail/<trail_name>/delete', methods=['POST'])
def delete_trail(trail_name):
    """Elimina un trail de CloudTrail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')
        cloudtrail.delete_trail(Name=trail_name)

        flash(f'Trail {trail_name} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando trail: {str(e)}', 'error')

    return redirect(url_for('cloudtrail.trails'))


@cloudtrail_bp.route('/trail/<trail_name>/start-logging', methods=['POST'])
def start_logging(trail_name):
    """Inicia el registro de logs para un trail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')
        cloudtrail.start_logging(Name=trail_name)

        flash(f'Registro de logs iniciado para trail {trail_name}', 'success')
    except Exception as e:
        flash(f'Error iniciando registro: {str(e)}', 'error')

    return redirect(url_for('cloudtrail.trail_detail', trail_name=trail_name))


@cloudtrail_bp.route('/trail/<trail_name>/stop-logging', methods=['POST'])
def stop_logging(trail_name):
    """Detiene el registro de logs para un trail"""
    try:
        cloudtrail = get_aws_client('cloudtrail')
        cloudtrail.stop_logging(Name=trail_name)

        flash(f'Registro de logs detenido para trail {trail_name}', 'success')
    except Exception as e:
        flash(f'Error deteniendo registro: {str(e)}', 'error')

    return redirect(url_for('cloudtrail.trail_detail', trail_name=trail_name))