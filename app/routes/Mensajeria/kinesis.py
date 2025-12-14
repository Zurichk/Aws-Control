from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('kinesis', __name__)

@bp.route('/')
def index():
    return render_template('Mensajeria/kinesis/index.html')

@bp.route('/streams')
def streams():
    try:
        kinesis = get_aws_client('kinesis')
        streams = kinesis.list_streams()
        stream_list = []
        for stream_name in streams['StreamNames']:
            stream_info = kinesis.describe_stream(StreamName=stream_name)
            stream_data = stream_info['StreamDescription']
            stream_list.append({
                'name': stream_name,
                'status': stream_data['StreamStatus'],
                'shards': len(stream_data.get('Shards', [])),
                'retention_hours': stream_data.get('RetentionPeriodHours', 24)
            })
        return render_template('Mensajeria/kinesis/streams.html', streams=stream_list)
    except Exception as e:
        flash(f'Error obteniendo streams de Kinesis: {str(e)}', 'error')
        return render_template('Mensajeria/kinesis/streams.html', streams=[])

@bp.route('/create-stream', methods=['GET', 'POST'])
def create_stream():
    if request.method == 'POST':
        try:
            stream_name = request.form.get('stream_name')
            shard_count = int(request.form.get('shard_count', 1))
            region = request.form.get('region', 'us-east-1')
            
            kinesis = get_aws_client('kinesis', region)
            kinesis.create_stream(
                StreamName=stream_name,
                ShardCount=shard_count
            )
            
            flash(f'Stream "{stream_name}" creado exitosamente con {shard_count} shard(s)', 'success')
            return redirect(url_for('kinesis.streams'))
        except Exception as e:
            flash(f'Error creando stream: {str(e)}', 'error')
    
    return render_template('kinesis/create_stream.html')

@bp.route('/delete-stream/<stream_name>', methods=['POST'])
def delete_stream(stream_name):
    try:
        region = request.form.get('region', 'us-east-1')
        kinesis = get_aws_client('kinesis', region)
        
        kinesis.delete_stream(StreamName=stream_name)
        flash(f'Stream "{stream_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando stream: {str(e)}', 'error')
    
    return redirect(url_for('kinesis.streams'))

@bp.route('/put-record', methods=['GET', 'POST'])
def put_record():
    if request.method == 'POST':
        try:
            stream_name = request.form.get('stream_name')
            data = request.form.get('data')
            partition_key = request.form.get('partition_key')
            region = request.form.get('region', 'us-east-1')
            
            kinesis = get_aws_client('kinesis', region)
            
            # Convertir datos a bytes
            data_bytes = data.encode('utf-8')
            
            response = kinesis.put_record(
                StreamName=stream_name,
                Data=data_bytes,
                PartitionKey=partition_key
            )
            
            flash(f'Registro enviado exitosamente. Shard ID: {response["ShardId"]}, Sequence Number: {response["SequenceNumber"]}', 'success')
            return redirect(url_for('kinesis.put_record'))
        except Exception as e:
            flash(f'Error enviando registro: {str(e)}', 'error')
    
    return render_template('kinesis/put_record.html')

@bp.route('/get-records', methods=['GET', 'POST'])
def get_records():
    records = []
    if request.method == 'POST':
        try:
            stream_name = request.form.get('stream_name')
            shard_id = request.form.get('shard_id')
            region = request.form.get('region', 'us-east-1')
            
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
            
            for record in records_response.get('Records', []):
                records.append({
                    'sequence_number': record['SequenceNumber'],
                    'partition_key': record['PartitionKey'],
                    'data': record['Data'].decode('utf-8') if isinstance(record['Data'], bytes) else str(record['Data']),
                    'approximate_arrival_timestamp': record.get('ApproximateArrivalTimestamp', '').isoformat() if record.get('ApproximateArrivalTimestamp') else ''
                })
            
            if not records:
                flash('No se encontraron registros en el shard especificado', 'info')
        except Exception as e:
            flash(f'Error obteniendo registros: {str(e)}', 'error')
    
    return render_template('kinesis/get_records.html', records=records)