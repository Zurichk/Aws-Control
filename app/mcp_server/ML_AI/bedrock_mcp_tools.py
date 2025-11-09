from typing import Dict, Any, List
import boto3
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BedrockMCPTools:
    """Herramientas MCP para Amazon Bedrock"""

    def __init__(self):
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    def list_foundation_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista los modelos de foundation disponibles en Bedrock"""
        try:
            region = params.get('region', self.region)
            bedrock_client = boto3.client('bedrock', region_name=region)

            response = bedrock_client.list_foundation_models()

            models = []
            for model in response.get('modelSummaries', []):
                models.append({
                    'modelId': model.get('modelId', ''),
                    'modelName': model.get('modelName', ''),
                    'providerName': model.get('providerName', ''),
                    'modelLifecycle': model.get('modelLifecycle', {}),
                    'inputModalities': model.get('inputModalities', []),
                    'outputModalities': model.get('outputModalities', []),
                    'customizationsSupported': model.get('customizationsSupported', []),
                    'inferenceTypesSupported': model.get('inferenceTypesSupported', [])
                })

            return {
                'models': models,
                'total_count': len(models),
                'region': region
            }

        except Exception as e:
            logger.exception(f"Error listando modelos de foundation: {e}")
            return {
                'error': str(e),
                'models': [],
                'message': f"Error al listar modelos de foundation: {str(e)}"
            }

    def invoke_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Invoca un modelo de Bedrock para generar texto"""
        try:
            model_id = params['model_id']
            prompt = params['prompt']
            region = params.get('region', self.region)
            max_tokens = params.get('max_tokens', 256)

            bedrock_client = boto3.client('bedrock-runtime', region_name=region)

            # Configurar el body de la petición según el modelo
            if 'anthropic' in model_id.lower():
                body = json.dumps({
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": max_tokens,
                    "temperature": 0.7,
                    "top_p": 1,
                    "top_k": 250
                })
            elif 'meta' in model_id.lower():
                body = json.dumps({
                    "prompt": prompt,
                    "max_gen_len": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
            else:
                # Configuración genérica
                body = json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                })

            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )

            response_body = json.loads(response['body'].read())

            # Extraer la respuesta según el modelo
            if 'anthropic' in model_id.lower():
                generated_text = response_body.get('completion', '')
            elif 'meta' in model_id.lower():
                generated_text = response_body.get('generation', '')
            else:
                generated_text = response_body.get('results', [{}])[0].get('outputText', '')

            return {
                'model_id': model_id,
                'prompt': prompt,
                'generated_text': generated_text,
                'region': region,
                'max_tokens': max_tokens
            }

        except Exception as e:
            logger.exception(f"Error invocando modelo: {e}")
            return {
                'error': str(e),
                'message': f"Error al invocar modelo: {str(e)}"
            }

    def create_model_customization_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un trabajo de customización de modelo"""
        try:
            base_model_id = params['base_model_id']
            job_name = params['job_name']
            role_arn = params['role_arn']
            training_data_uri = params['training_data_uri']
            output_data_uri = params['output_data_uri']
            region = params.get('region', self.region)
            validation_data_uri = params.get('validation_data_uri')

            bedrock_client = boto3.client('bedrock', region_name=region)

            customization_config = {
                'trainingDataConfig': {
                    's3Uri': training_data_uri
                },
                'outputDataConfig': {
                    's3Uri': output_data_uri
                }
            }

            if validation_data_uri:
                customization_config['validationDataConfig'] = {
                    'validators': [{
                        's3Uri': validation_data_uri
                    }]
                }

            response = bedrock_client.create_model_customization_job(
                jobName=job_name,
                customModelName=f"{job_name}-custom",
                roleArn=role_arn,
                baseModelIdentifier=base_model_id,
                customizationConfig=customization_config
            )

            return {
                'job_arn': response.get('jobArn', ''),
                'job_name': job_name,
                'custom_model_name': f"{job_name}-custom",
                'base_model_id': base_model_id,
                'status': 'Submitted',
                'region': region,
                'creation_time': datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception(f"Error creando trabajo de customización: {e}")
            return {
                'error': str(e),
                'message': f"Error al crear trabajo de customización: {str(e)}"
            }

# Instancia global
bedrock_tools = BedrockMCPTools()

# Definición de herramientas MCP
BEDROCK_MCP_TOOLS = [
    {
        'name': 'list_foundation_models',
        'description': 'Lista todos los modelos de foundation disponibles en Amazon Bedrock',
        'parameters': {
            'type': 'object',
            'properties': {
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                }
            },
            'required': []
        }
    },
    {
        'name': 'invoke_model',
        'description': 'Invoca un modelo de foundation para generar texto basado en un prompt',
        'parameters': {
            'type': 'object',
            'properties': {
                'model_id': {
                    'type': 'string',
                    'description': 'ID del modelo de Bedrock (ej: anthropic.claude-v2)'
                },
                'prompt': {
                    'type': 'string',
                    'description': 'Texto del prompt para el modelo'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                },
                'max_tokens': {
                    'type': 'integer',
                    'description': 'Número máximo de tokens a generar',
                    'default': 256
                }
            },
            'required': ['model_id', 'prompt']
        }
    },
    {
        'name': 'create_model_customization_job',
        'description': 'Crea un trabajo de customización de modelo usando datos de entrenamiento',
        'parameters': {
            'type': 'object',
            'properties': {
                'base_model_id': {
                    'type': 'string',
                    'description': 'ID del modelo base para customizar'
                },
                'job_name': {
                    'type': 'string',
                    'description': 'Nombre único para el trabajo de customización'
                },
                'role_arn': {
                    'type': 'string',
                    'description': 'ARN del rol IAM con permisos para Bedrock'
                },
                'training_data_uri': {
                    'type': 'string',
                    'description': 'URI de S3 con los datos de entrenamiento'
                },
                'output_data_uri': {
                    'type': 'string',
                    'description': 'URI de S3 donde guardar el modelo customizado'
                },
                'validation_data_uri': {
                    'type': 'string',
                    'description': 'URI de S3 con datos de validación (opcional)'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                }
            },
            'required': ['base_model_id', 'job_name', 'role_arn', 'training_data_uri', 'output_data_uri']
        }
    }
]