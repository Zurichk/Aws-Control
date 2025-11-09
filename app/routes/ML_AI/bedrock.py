from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
import os
import json
from datetime import datetime

bedrock = Blueprint('bedrock', __name__)

@bedrock.route('/bedrock')
def bedrock_dashboard():
    """Dashboard principal de Amazon Bedrock"""
    return render_template('ML_AI/bedrock/index.html')

@bedrock.route('/bedrock/models', methods=['GET', 'POST'])
def list_foundation_models():
    """Listar modelos de foundation disponibles en Bedrock"""
    if request.method == 'POST':
        try:
            region = request.form.get('region', 'us-east-1')

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

            return render_template('ML_AI/bedrock/models.html',
                                 models=models,
                                 region=region)

        except Exception as e:
            flash(f'Error listando modelos de foundation: {str(e)}', 'error')
            return redirect(url_for('bedrock.list_foundation_models'))

    # GET request - mostrar formulario
    return render_template('ML_AI/bedrock/models.html', models=None, region='us-east-1')

@bedrock.route('/bedrock/invoke', methods=['GET', 'POST'])
def invoke_model():
    """Invocar un modelo de Bedrock"""
    if request.method == 'POST':
        try:
            model_id = request.form.get('model_id')
            prompt = request.form.get('prompt')
            region = request.form.get('region', 'us-east-1')
            max_tokens = int(request.form.get('max_tokens', 256))

            if not model_id or not prompt:
                flash('El ID del modelo y el prompt son requeridos', 'error')
                return redirect(url_for('bedrock.invoke_model'))

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

            return render_template('ML_AI/bedrock/invoke.html',
                                 model_id=model_id,
                                 prompt=prompt,
                                 response=generated_text,
                                 region=region,
                                 max_tokens=max_tokens)

        except Exception as e:
            flash(f'Error invocando modelo: {str(e)}', 'error')
            return redirect(url_for('bedrock.invoke_model'))

    # GET request - mostrar formulario
    return render_template('ML_AI/bedrock/invoke.html',
                         model_id=None,
                         prompt=None,
                         response=None,
                         region='us-east-1',
                         max_tokens=256)

@bedrock.route('/bedrock/customization', methods=['GET', 'POST'])
def create_model_customization_job():
    """Crear un trabajo de customización de modelo"""
    if request.method == 'POST':
        try:
            base_model_id = request.form.get('base_model_id')
            job_name = request.form.get('job_name')
            role_arn = request.form.get('role_arn')
            training_data_uri = request.form.get('training_data_uri')
            validation_data_uri = request.form.get('validation_data_uri')
            output_data_uri = request.form.get('output_data_uri')
            region = request.form.get('region', 'us-east-1')

            if not all([base_model_id, job_name, role_arn, training_data_uri, output_data_uri]):
                flash('Los campos requeridos son: modelo base, nombre del job, rol ARN, datos de entrenamiento y output URI', 'error')
                return redirect(url_for('bedrock.create_model_customization_job'))

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

            job_details = {
                'jobArn': response.get('jobArn', ''),
                'jobName': job_name,
                'status': 'Submitted',
                'creationTime': datetime.now().isoformat(),
                'baseModelId': base_model_id,
                'customModelName': f"{job_name}-custom"
            }

            return render_template('ML_AI/bedrock/customization.html',
                                 job_details=job_details,
                                 region=region)

        except Exception as e:
            flash(f'Error creando trabajo de customización: {str(e)}', 'error')
            return redirect(url_for('bedrock.create_model_customization_job'))

    # GET request - mostrar formulario
    return render_template('ML_AI/bedrock/customization.html',
                         job_details=None,
                         region='us-east-1')