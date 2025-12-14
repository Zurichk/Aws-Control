import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import json
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)


class PollyMCPTools:
    """
    MCP tools for Amazon Polly (Text-to-Speech).
    Provides comprehensive text-to-speech synthesis operations.
    """

    def __init__(self):
        self.client = boto3.client('polly')

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para Amazon Polly"""
        return [
            {
                'name': 'polly_synthesize_speech',
                'description': 'Sintetiza texto a voz usando Amazon Polly. Retorna audio en formato MP3, OGG o PCM.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'text': {
                            'type': 'string',
                            'description': 'Texto a convertir en voz (máximo 3000 caracteres para voz estándar, 6000 para neural)'
                        },
                        'voice_id': {
                            'type': 'string',
                            'description': 'ID de la voz (ej: Joanna, Matthew, Lucia, Miguel). Usa list_voices para ver opciones'
                        },
                        'output_format': {
                            'type': 'string',
                            'description': 'Formato de salida: mp3, ogg_vorbis, pcm',
                            'default': 'mp3'
                        },
                        'engine': {
                            'type': 'string',
                            'description': 'Motor de síntesis: standard o neural (neural ofrece mejor calidad)',
                            'default': 'neural'
                        },
                        'language_code': {
                            'type': 'string',
                            'description': 'Código de idioma (ej: es-ES, es-US, en-US). Opcional si la voz es específica del idioma'
                        },
                        'sample_rate': {
                            'type': 'string',
                            'description': 'Frecuencia de muestreo: 8000, 16000, 22050, 24000 Hz'
                        },
                        'text_type': {
                            'type': 'string',
                            'description': 'Tipo de texto: text o ssml (Speech Synthesis Markup Language)',
                            'default': 'text'
                        }
                    },
                    'required': ['text', 'voice_id']
                },
                'function': self.synthesize_speech
            },
            {
                'name': 'polly_list_voices',
                'description': 'Lista todas las voces disponibles en Amazon Polly, filtradas por idioma opcionalmente',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'language_code': {
                            'type': 'string',
                            'description': 'Filtrar por código de idioma (ej: es-ES, es-US, en-US, pt-BR)'
                        },
                        'engine': {
                            'type': 'string',
                            'description': 'Filtrar por motor: standard, neural, long-form, generative'
                        }
                    }
                },
                'function': self.list_voices
            },
            {
                'name': 'polly_describe_voices',
                'description': 'Obtiene información detallada sobre voces específicas de Amazon Polly',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'language_code': {
                            'type': 'string',
                            'description': 'Código de idioma para filtrar voces'
                        },
                        'voice_ids': {
                            'type': 'array',
                            'description': 'Lista de IDs de voces específicas para describir',
                            'items': {'type': 'string'}
                        }
                    }
                },
                'function': self.describe_voices
            },
            {
                'name': 'polly_start_speech_synthesis_task',
                'description': 'Inicia tarea asíncrona de síntesis de voz (para textos largos). Guarda el audio en S3.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'text': {
                            'type': 'string',
                            'description': 'Texto a sintetizar (hasta 200,000 caracteres)'
                        },
                        'voice_id': {
                            'type': 'string',
                            'description': 'ID de la voz a usar'
                        },
                        's3_bucket': {
                            'type': 'string',
                            'description': 'Nombre del bucket S3 donde guardar el audio'
                        },
                        's3_key_prefix': {
                            'type': 'string',
                            'description': 'Prefijo de la clave S3 (carpeta)'
                        },
                        'output_format': {
                            'type': 'string',
                            'description': 'Formato: mp3, ogg_vorbis, pcm',
                            'default': 'mp3'
                        },
                        'engine': {
                            'type': 'string',
                            'description': 'Motor: standard, neural, long-form',
                            'default': 'neural'
                        },
                        'text_type': {
                            'type': 'string',
                            'description': 'Tipo: text o ssml',
                            'default': 'text'
                        }
                    },
                    'required': ['text', 'voice_id', 's3_bucket']
                },
                'function': self.start_speech_synthesis_task
            },
            {
                'name': 'polly_get_speech_synthesis_task',
                'description': 'Obtiene el estado y resultado de una tarea de síntesis asíncrona',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'task_id': {
                            'type': 'string',
                            'description': 'ID de la tarea de síntesis'
                        }
                    },
                    'required': ['task_id']
                },
                'function': self.get_speech_synthesis_task
            },
            {
                'name': 'polly_list_speech_synthesis_tasks',
                'description': 'Lista todas las tareas de síntesis de voz (asíncronas)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'description': 'Filtrar por estado: scheduled, inProgress, completed, failed'
                        },
                        'max_results': {
                            'type': 'integer',
                            'description': 'Número máximo de resultados (1-100)',
                            'default': 10
                        }
                    }
                },
                'function': self.list_speech_synthesis_tasks
            },
            {
                'name': 'polly_get_lexicon',
                'description': 'Obtiene un lexicón personalizado de pronunciación',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Nombre del lexicón'
                        }
                    },
                    'required': ['name']
                },
                'function': self.get_lexicon
            },
            {
                'name': 'polly_put_lexicon',
                'description': 'Crea o actualiza un lexicón personalizado para pronunciaciones específicas',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Nombre del lexicón'
                        },
                        'content': {
                            'type': 'string',
                            'description': 'Contenido del lexicón en formato PLS (Pronunciation Lexicon Specification) XML'
                        }
                    },
                    'required': ['name', 'content']
                },
                'function': self.put_lexicon
            },
            {
                'name': 'polly_delete_lexicon',
                'description': 'Elimina un lexicón personalizado',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'Nombre del lexicón a eliminar'
                        }
                    },
                    'required': ['name']
                },
                'function': self.delete_lexicon
            },
            {
                'name': 'polly_list_lexicons',
                'description': 'Lista todos los lexicones personalizados',
                'parameters': {
                    'type': 'object',
                    'properties': {}
                },
                'function': self.list_lexicons
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica"""
        tools = {tool['name']: tool['function'] for tool in self.get_tools()}
        
        if tool_name in tools:
            return tools[tool_name](**parameters)
        
        return {
            'success': False,
            'error': f'Herramienta {tool_name} no encontrada'
        }

    def synthesize_speech(self, text: str, voice_id: str, output_format: str = 'mp3', 
                         engine: str = 'neural', language_code: Optional[str] = None,
                         sample_rate: Optional[str] = None, text_type: str = 'text',
                         **kwargs) -> Dict[str, Any]:
        """
        Sintetiza texto a voz y retorna el audio codificado en base64
        
        Args:
            text: Texto a sintetizar
            voice_id: ID de la voz
            output_format: mp3, ogg_vorbis, pcm
            engine: standard o neural
            language_code: Código de idioma (opcional)
            sample_rate: Frecuencia de muestreo
            text_type: text o ssml
        """
        try:
            params = {
                'Text': text,
                'VoiceId': voice_id,
                'OutputFormat': output_format,
                'Engine': engine,
                'TextType': text_type
            }
            
            if language_code:
                params['LanguageCode'] = language_code
            if sample_rate:
                params['SampleRate'] = sample_rate
            
            response = self.client.synthesize_speech(**params)
            
            # Leer el audio stream
            audio_stream = response['AudioStream'].read()
            
            # Codificar en base64 para retornar como JSON
            audio_base64 = base64.b64encode(audio_stream).decode('utf-8')
            
            return {
                'success': True,
                'message': f'Audio sintetizado exitosamente con voz {voice_id}',
                'audio_base64': audio_base64,
                'content_type': response.get('ContentType', f'audio/{output_format}'),
                'size_bytes': len(audio_stream),
                'request_characters': response.get('RequestCharacters', len(text)),
                'voice_id': voice_id,
                'engine': engine,
                'format': output_format
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            return {
                'success': False,
                'error': f'Error sintetizando voz: {error_msg}',
                'error_code': error_code
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }

    def list_voices(self, language_code: Optional[str] = None, engine: Optional[str] = None, 
                   **kwargs) -> Dict[str, Any]:
        """
        Lista todas las voces disponibles
        
        Args:
            language_code: Filtrar por idioma (ej: es-ES, en-US)
            engine: Filtrar por motor (standard, neural, long-form, generative)
        """
        try:
            params = {}
            if language_code:
                params['LanguageCode'] = language_code
            if engine:
                params['Engine'] = engine
            
            response = self.client.describe_voices(**params)
            
            voices = []
            for voice in response.get('Voices', []):
                voices.append({
                    'id': voice['Id'],
                    'name': voice['Name'],
                    'gender': voice['Gender'],
                    'language_name': voice['LanguageName'],
                    'language_code': voice['LanguageCode'],
                    'supported_engines': voice.get('SupportedEngines', []),
                    'additional_language_codes': voice.get('AdditionalLanguageCodes', [])
                })
            
            return {
                'success': True,
                'voices': voices,
                'total_count': len(voices),
                'filter_language': language_code,
                'filter_engine': engine
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error listando voces: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def describe_voices(self, language_code: Optional[str] = None, 
                       voice_ids: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre voces específicas
        """
        try:
            params = {}
            if language_code:
                params['LanguageCode'] = language_code
            
            response = self.client.describe_voices(**params)
            
            voices = response.get('Voices', [])
            
            # Filtrar por voice_ids si se especificaron
            if voice_ids:
                voices = [v for v in voices if v['Id'] in voice_ids]
            
            voices_details = []
            for voice in voices:
                voices_details.append({
                    'id': voice['Id'],
                    'name': voice['Name'],
                    'gender': voice['Gender'],
                    'language_name': voice['LanguageName'],
                    'language_code': voice['LanguageCode'],
                    'supported_engines': voice.get('SupportedEngines', []),
                    'additional_language_codes': voice.get('AdditionalLanguageCodes', [])
                })
            
            return {
                'success': True,
                'voices': voices_details,
                'count': len(voices_details)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error obteniendo información de voces: {str(e)}'
            }

    def start_speech_synthesis_task(self, text: str, voice_id: str, s3_bucket: str,
                                   s3_key_prefix: Optional[str] = None,
                                   output_format: str = 'mp3', engine: str = 'neural',
                                   text_type: str = 'text', **kwargs) -> Dict[str, Any]:
        """
        Inicia una tarea asíncrona de síntesis de voz (para textos largos)
        El audio se guarda automáticamente en S3
        """
        try:
            params = {
                'Text': text,
                'VoiceId': voice_id,
                'OutputFormat': output_format,
                'OutputS3BucketName': s3_bucket,
                'Engine': engine,
                'TextType': text_type
            }
            
            if s3_key_prefix:
                params['OutputS3KeyPrefix'] = s3_key_prefix
            
            response = self.client.start_speech_synthesis_task(**params)
            
            task = response.get('SynthesisTask', {})
            
            return {
                'success': True,
                'message': 'Tarea de síntesis iniciada exitosamente',
                'task_id': task.get('TaskId'),
                'task_status': task.get('TaskStatus'),
                'output_uri': task.get('OutputUri'),
                's3_bucket': s3_bucket,
                's3_key_prefix': s3_key_prefix,
                'creation_time': str(task.get('CreationTime', '')),
                'voice_id': voice_id,
                'engine': engine
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error iniciando tarea de síntesis: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def get_speech_synthesis_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """
        Obtiene el estado de una tarea de síntesis asíncrona
        """
        try:
            response = self.client.get_speech_synthesis_task(TaskId=task_id)
            
            task = response.get('SynthesisTask', {})
            
            return {
                'success': True,
                'task_id': task.get('TaskId'),
                'task_status': task.get('TaskStatus'),
                'task_status_reason': task.get('TaskStatusReason'),
                'output_uri': task.get('OutputUri'),
                'creation_time': str(task.get('CreationTime', '')),
                'request_characters': task.get('RequestCharacters'),
                'voice_id': task.get('VoiceId'),
                'engine': task.get('Engine'),
                'output_format': task.get('OutputFormat'),
                'text_type': task.get('TextType')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error obteniendo tarea: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def list_speech_synthesis_tasks(self, status: Optional[str] = None, 
                                   max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Lista todas las tareas de síntesis
        """
        try:
            params = {'MaxResults': max_results}
            if status:
                params['Status'] = status
            
            response = self.client.list_speech_synthesis_tasks(**params)
            
            tasks = []
            for task in response.get('SynthesisTasks', []):
                tasks.append({
                    'task_id': task.get('TaskId'),
                    'task_status': task.get('TaskStatus'),
                    'creation_time': str(task.get('CreationTime', '')),
                    'voice_id': task.get('VoiceId'),
                    'output_uri': task.get('OutputUri'),
                    'engine': task.get('Engine'),
                    'output_format': task.get('OutputFormat')
                })
            
            return {
                'success': True,
                'tasks': tasks,
                'total_count': len(tasks),
                'next_token': response.get('NextToken')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error listando tareas: {str(e)}'
            }

    def get_lexicon(self, name: str, **kwargs) -> Dict[str, Any]:
        """Obtiene un lexicón personalizado"""
        try:
            response = self.client.get_lexicon(Name=name)
            
            return {
                'success': True,
                'name': name,
                'content': response.get('Lexicon', {}).get('Content'),
                'attributes': response.get('LexiconAttributes', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error obteniendo lexicón: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def put_lexicon(self, name: str, content: str, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza un lexicón personalizado"""
        try:
            self.client.put_lexicon(Name=name, Content=content)
            
            return {
                'success': True,
                'message': f'Lexicón {name} creado/actualizado exitosamente',
                'name': name
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error creando/actualizando lexicón: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def delete_lexicon(self, name: str, **kwargs) -> Dict[str, Any]:
        """Elimina un lexicón"""
        try:
            self.client.delete_lexicon(Name=name)
            
            return {
                'success': True,
                'message': f'Lexicón {name} eliminado exitosamente',
                'name': name
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error eliminando lexicón: {str(e)}',
                'error_code': e.response['Error']['Code']
            }

    def list_lexicons(self, **kwargs) -> Dict[str, Any]:
        """Lista todos los lexicones"""
        try:
            response = self.client.list_lexicons()
            
            lexicons = []
            for lex in response.get('Lexicons', []):
                lexicons.append({
                    'name': lex.get('Name'),
                    'attributes': lex.get('Attributes', {})
                })
            
            return {
                'success': True,
                'lexicons': lexicons,
                'total_count': len(lexicons)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': f'Error listando lexicones: {str(e)}'
            }
