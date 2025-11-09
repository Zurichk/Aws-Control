from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('cloudwatch', __name__)

@bp.route('/cloudwatch')
def index():
    return render_template('Gestion/cloudwatch/index.html')

@bp.route('/cloudwatch/alarms')
def alarms():
    try:
        cw = get_aws_client('cloudwatch')
        alarms = cw.describe_alarms()
        alarm_list = []
        for alarm in alarms['MetricAlarms']:
            alarm_list.append({
                'name': alarm['AlarmName'],
                'state': alarm['StateValue'],
                'description': alarm.get('AlarmDescription', 'N/A'),
                'metric': alarm['MetricName'],
                'namespace': alarm.get('Namespace', 'N/A'),
                'threshold': alarm.get('Threshold', 'N/A'),
                'comparison_operator': alarm.get('ComparisonOperator', 'N/A')
            })
        return render_template('Gestion/cloudwatch/alarms.html', alarms=alarm_list)
    except Exception as e:
        flash(f'Error obteniendo alarmas de CloudWatch: {str(e)}', 'error')
        return render_template('Gestion/cloudwatch/alarms.html', alarms=[])

@bp.route('/cloudwatch/alarms/create', methods=['GET', 'POST'])
def create_alarm():
    if request.method == 'POST':
        try:
            cw = get_aws_client('cloudwatch')
            
            alarm_name = request.form.get('alarm_name')
            metric_name = request.form.get('metric_name')
            namespace = request.form.get('namespace')
            statistic = request.form.get('statistic')
            comparison_operator = request.form.get('comparison_operator')
            threshold = float(request.form.get('threshold'))
            period = int(request.form.get('period'))
            evaluation_periods = int(request.form.get('evaluation_periods'))
            description = request.form.get('description')
            
            cw.put_metric_alarm(
                AlarmName=alarm_name,
                MetricName=metric_name,
                Namespace=namespace,
                Statistic=statistic,
                ComparisonOperator=comparison_operator,
                Threshold=threshold,
                Period=period,
                EvaluationPeriods=evaluation_periods,
                AlarmDescription=description
            )
            
            flash(f'Alarma {alarm_name} creada exitosamente', 'success')
            return redirect(url_for('cloudwatch.alarms'))
            
        except Exception as e:
            flash(f'Error creando alarma: {str(e)}', 'error')
    
    return render_template('Gestion/cloudwatch/create_alarm.html')

@bp.route('/cloudwatch/alarms/delete/<alarm_name>', methods=['POST'])
def delete_alarm(alarm_name):
    try:
        cw = get_aws_client('cloudwatch')
        cw.delete_alarms(AlarmNames=[alarm_name])
        flash(f'Alarma {alarm_name} eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando alarma: {str(e)}', 'error')
    
    return redirect(url_for('cloudwatch.alarms'))

@bp.route('/cloudwatch/metrics')
def metrics():
    try:
        cw = get_aws_client('cloudwatch')
        metrics = cw.list_metrics()
        metric_list = []
        
        for metric in metrics['Metrics'][:100]:  # Limitar a 100 métricas
            metric_list.append({
                'namespace': metric['Namespace'],
                'metric_name': metric['MetricName'],
                'dimensions': metric.get('Dimensions', [])
            })
        
        return render_template('Gestion/cloudwatch/metrics.html', metrics=metric_list)
    except Exception as e:
        flash(f'Error obteniendo métricas: {str(e)}', 'error')
        return render_template('Gestion/cloudwatch/metrics.html', metrics=[])

@bp.route('/cloudwatch/metrics/statistics', methods=['GET', 'POST'])
def metric_statistics():
    if request.method == 'POST':
        try:
            cw = get_aws_client('cloudwatch')
            
            namespace = request.form.get('namespace')
            metric_name = request.form.get('metric_name')
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            period = int(request.form.get('period'))
            statistics = request.form.getlist('statistics')
            
            response = cw.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=statistics
            )
            
            return render_template('Gestion/cloudwatch/metric_statistics.html', 
                                 statistics=response['Datapoints'],
                                 namespace=namespace,
                                 metric_name=metric_name)
            
        except Exception as e:
            flash(f'Error obteniendo estadísticas: {str(e)}', 'error')
            return render_template('Gestion/cloudwatch/metric_statistics.html', 
                                 statistics=[], namespace='', metric_name='')
    
    return render_template('Gestion/cloudwatch/metric_statistics_form.html')

@bp.route('/cloudwatch/metrics/data', methods=['GET', 'POST'])
def put_metric_data():
    if request.method == 'POST':
        try:
            cw = get_aws_client('cloudwatch')
            
            namespace = request.form.get('namespace')
            metric_name = request.form.get('metric_name')
            value = float(request.form.get('value'))
            timestamp = request.form.get('timestamp')
            unit = request.form.get('unit')
            
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }
            
            if timestamp:
                from datetime import datetime
                metric_data['Timestamp'] = datetime.fromisoformat(timestamp)
            
            cw.put_metric_data(
                Namespace=namespace,
                MetricData=[metric_data]
            )
            
            flash('Dato métrico enviado exitosamente', 'success')
            return redirect(url_for('cloudwatch.metrics'))
            
        except Exception as e:
            flash(f'Error enviando dato métrico: {str(e)}', 'error')
    
    return render_template('Gestion/cloudwatch/put_metric_data.html')