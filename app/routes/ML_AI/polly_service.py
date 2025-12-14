from flask import Blueprint, render_template, request, jsonify, send_file
from app.utils.aws_client import get_aws_client
from botocore.exceptions import ClientError, BotoCoreError
import base64
import io
import logging

logger = logging.getLogger(__name__)

polly_bp = Blueprint('polly', __name__, url_prefix='/ml-ai/polly')


@polly_bp.route('/')
def index():
    """Página principal de Amazon Polly"""
    return render_template('ML_AI/polly/index.html')


@polly_bp.route('/synthesize', methods=['POST'])
def synthesize_speech():
    """Sintetiza texto a voz"""
    try:
        data = request.json
        text = data.get('text')
        voice_id = data.get('voice_id', 'Joanna')
        engine = data.get('engine', 'neural')
        output_format = data.get('output_format', 'mp3')
        
        if not text:
            return jsonify({'error': 'El texto es requerido'}), 400
        
        polly = get_aws_client('polly')
        
        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            OutputFormat=output_format,
            Engine=engine
        )
        
        # Leer el audio
        audio_stream = response['AudioStream'].read()
        audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'content_type': response.get('ContentType'),
            'size': len(audio_stream),
            'characters': len(text)
        })
        
    except ClientError as e:
        logger.error(f"Error en Polly synthesize: {str(e)}")
        return jsonify({
            'error': f'Error de AWS: {str(e)}',
            'error_code': e.response['Error']['Code']
        }), 500
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return jsonify({'error': str(e)}), 500


@polly_bp.route('/voices', methods=['GET'])
def list_voices():
    """Lista todas las voces disponibles"""
    try:
        language_code = request.args.get('language_code')
        engine = request.args.get('engine')
        
        polly = get_aws_client('polly')
        
        params = {}
        if language_code:
            params['LanguageCode'] = language_code
        if engine:
            params['Engine'] = engine
        
        response = polly.describe_voices(**params)
        
        voices = []
        for voice in response.get('Voices', []):
            voices.append({
                'id': voice['Id'],
                'name': voice['Name'],
                'gender': voice['Gender'],
                'language_name': voice['LanguageName'],
                'language_code': voice['LanguageCode'],
                'supported_engines': voice.get('SupportedEngines', [])
            })
        
        return jsonify({
            'success': True,
            'voices': voices,
            'total': len(voices)
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error listando voces: {str(e)}'
        }), 500


@polly_bp.route('/tasks/start', methods=['POST'])
def start_synthesis_task():
    """Inicia tarea asíncrona de síntesis (para textos largos)"""
    try:
        data = request.json
        text = data.get('text')
        voice_id = data.get('voice_id', 'Joanna')
        s3_bucket = data.get('s3_bucket')
        s3_key_prefix = data.get('s3_key_prefix', 'polly-output/')
        engine = data.get('engine', 'neural')
        output_format = data.get('output_format', 'mp3')
        
        if not text or not s3_bucket:
            return jsonify({'error': 'Texto y bucket S3 son requeridos'}), 400
        
        polly = get_aws_client('polly')
        
        params = {
            'Text': text,
            'VoiceId': voice_id,
            'OutputFormat': output_format,
            'OutputS3BucketName': s3_bucket,
            'Engine': engine
        }
        
        if s3_key_prefix:
            params['OutputS3KeyPrefix'] = s3_key_prefix
        
        response = polly.start_speech_synthesis_task(**params)
        
        task = response.get('SynthesisTask', {})
        
        return jsonify({
            'success': True,
            'task_id': task.get('TaskId'),
            'status': task.get('TaskStatus'),
            'output_uri': task.get('OutputUri')
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error iniciando tarea: {str(e)}'
        }), 500


@polly_bp.route('/tasks/<task_id>', methods=['GET'])
def get_synthesis_task(task_id):
    """Obtiene el estado de una tarea"""
    try:
        polly = get_aws_client('polly')
        
        response = polly.get_speech_synthesis_task(TaskId=task_id)
        task = response.get('SynthesisTask', {})
        
        return jsonify({
            'success': True,
            'task_id': task.get('TaskId'),
            'status': task.get('TaskStatus'),
            'output_uri': task.get('OutputUri'),
            'creation_time': str(task.get('CreationTime', '')),
            'voice_id': task.get('VoiceId')
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error obteniendo tarea: {str(e)}'
        }), 500


@polly_bp.route('/tasks', methods=['GET'])
def list_synthesis_tasks():
    """Lista todas las tareas de síntesis"""
    try:
        status = request.args.get('status')
        max_results = request.args.get('max_results', 10, type=int)
        
        polly = get_aws_client('polly')
        
        params = {'MaxResults': max_results}
        if status:
            params['Status'] = status
        
        response = polly.list_speech_synthesis_tasks(**params)
        
        tasks = []
        for task in response.get('SynthesisTasks', []):
            tasks.append({
                'task_id': task.get('TaskId'),
                'status': task.get('TaskStatus'),
                'creation_time': str(task.get('CreationTime', '')),
                'voice_id': task.get('VoiceId'),
                'output_uri': task.get('OutputUri')
            })
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'total': len(tasks)
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error listando tareas: {str(e)}'
        }), 500


@polly_bp.route('/lexicons', methods=['GET'])
def list_lexicons():
    """Lista lexicones personalizados"""
    try:
        polly = get_aws_client('polly')
        response = polly.list_lexicons()
        
        lexicons = []
        for lex in response.get('Lexicons', []):
            lexicons.append({
                'name': lex.get('Name'),
                'attributes': lex.get('Attributes', {})
            })
        
        return jsonify({
            'success': True,
            'lexicons': lexicons
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error listando lexicones: {str(e)}'
        }), 500


@polly_bp.route('/lexicons', methods=['POST'])
def create_lexicon():
    """Crea un lexicón personalizado"""
    try:
        data = request.json
        name = data.get('name')
        content = data.get('content')
        
        if not name or not content:
            return jsonify({'error': 'Nombre y contenido son requeridos'}), 400
        
        polly = get_aws_client('polly')
        polly.put_lexicon(Name=name, Content=content)
        
        return jsonify({
            'success': True,
            'message': f'Lexicón {name} creado exitosamente'
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error creando lexicón: {str(e)}'
        }), 500


@polly_bp.route('/lexicons/<name>', methods=['DELETE'])
def delete_lexicon(name):
    """Elimina un lexicón"""
    try:
        polly = get_aws_client('polly')
        polly.delete_lexicon(Name=name)
        
        return jsonify({
            'success': True,
            'message': f'Lexicón {name} eliminado'
        })
        
    except ClientError as e:
        return jsonify({
            'error': f'Error eliminando lexicón: {str(e)}'
        }), 500
