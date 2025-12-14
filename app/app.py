from flask import Flask, render_template, jsonify, request
from app.routes import (ec2, s3, iam, lambda_bp, rds, vpc, cloudformation, cloudwatch, 
                       route53, elbv2, dynamodb, sns, sqs, cloudfront, kms, kinesis, 
                       apigateway, ecs, ecr, eks, sagemaker, config, elasticache, neptune, documentdb,
                       autoscaling, ebs, efs, fsx, security_groups, secretsmanager, batch, acm_bp, cost_explorer,
                       bedrock, rekognition, polly_bp, athena, glue, emr, chat, eventbridge, systems_manager, cloudtrail, 
                       setup, configuracion)
import os
import logging
from dotenv import load_dotenv
from app.mcp_server.Contenedores.ecs_mcp_tools import ECS_MCP_TOOLS
from app.mcp_server.Seguridad.secretsmanager_mcp_tools import SecretsManagerMCPTools
from app.mcp_server.Seguridad.acm_mcp_tools import AcmMCPTools
from app.mcp_server.Gestion.cloudwatch_mcp_tools import CLOUDWATCH_MCP_TOOLS
from app.mcp_server.AWSConfig.config_mcp_tools import CONFIG_MCP_TOOLS
from app.mcp_server.Gestion.cost_explorer_mcp_tools import COST_EXPLORER_MCP_TOOLS
from app.mcp_server.ML_AI.bedrock_mcp_tools import BedrockMCPTools
from app.mcp_server.ML_AI.rekognition_mcp_tools import RekognitionMCPTools
from app.mcp_server.Mensajeria.kinesis_mcp_tools import KinesisMCPTools
from app.mcp_server.Analytics.athena_mcp_tools import AthenaMCPTools
from app.mcp_server.Analytics.glue_mcp_tools import GlueMCPTools
from app.mcp_server.AI_Assistant.ai_assistant_mcp_tools import AIAssistantMCPTools

# Initialize MCP tool instances
secretsmanager_tools = SecretsManagerMCPTools()
acm_tools = AcmMCPTools()
bedrock_tools = BedrockMCPTools()
rekognition_tools = RekognitionMCPTools()
kinesis_tools = KinesisMCPTools()
athena_tools = AthenaMCPTools()
glue_tools = GlueMCPTools()
ai_assistant_tools = AIAssistantMCPTools()

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler() 
        ]
    )

    # Register blueprints
    app.register_blueprint(ec2)
    app.register_blueprint(s3)
    app.register_blueprint(iam)
    app.register_blueprint(lambda_bp, url_prefix='/lambda_service')
    app.register_blueprint(autoscaling, url_prefix='/autoscaling')
    app.register_blueprint(rds)
    app.register_blueprint(vpc)
    app.register_blueprint(cloudformation, url_prefix='/cloudformation')
    app.register_blueprint(cloudwatch)
    app.register_blueprint(route53, url_prefix='/route53')
    app.register_blueprint(elbv2, url_prefix='/elbv2')
    app.register_blueprint(dynamodb, url_prefix='/dynamodb')
    app.register_blueprint(sns, url_prefix='/sns')
    app.register_blueprint(sqs, url_prefix='/sqs')
    app.register_blueprint(eventbridge, url_prefix='/eventbridge')
    app.register_blueprint(cloudfront, url_prefix='/cloudfront')
    app.register_blueprint(kms, url_prefix='/kms')
    app.register_blueprint(kinesis, url_prefix='/kinesis')
    app.register_blueprint(apigateway, url_prefix='/apigateway')
    app.register_blueprint(ecs, url_prefix='/ecs')
    app.register_blueprint(ecr, url_prefix='/ecr')
    app.register_blueprint(eks, url_prefix='/eks')
    app.register_blueprint(sagemaker, url_prefix='/sagemaker')
    app.register_blueprint(chat, url_prefix='/chat')
    app.register_blueprint(config, url_prefix='/config')
    app.register_blueprint(setup, url_prefix='/setup')
    app.register_blueprint(configuracion)  # Ya tiene el prefijo /configuracion en el blueprint
    app.register_blueprint(cost_explorer, url_prefix='/cost_explorer')
    app.register_blueprint(elasticache, url_prefix='/elasticache')
    app.register_blueprint(neptune, url_prefix='/neptune')
    app.register_blueprint(documentdb, url_prefix='/documentdb')
    app.register_blueprint(ebs, url_prefix='/ebs')
    app.register_blueprint(efs)
    app.register_blueprint(fsx)
    app.register_blueprint(security_groups)
    app.register_blueprint(secretsmanager, url_prefix='/secretsmanager')
    app.register_blueprint(batch, url_prefix='/batch')
    app.register_blueprint(acm_bp, url_prefix='/acm')
    app.register_blueprint(bedrock, url_prefix='/bedrock')
    app.register_blueprint(rekognition, url_prefix='/rekognition')
    app.register_blueprint(polly_bp, url_prefix='/ml-ai/polly')
    app.register_blueprint(athena, url_prefix='/athena')
    app.register_blueprint(glue, url_prefix='/glue')
    app.register_blueprint(emr, url_prefix='/emr')
    app.register_blueprint(systems_manager, url_prefix='/systems-manager')
    app.register_blueprint(cloudtrail, url_prefix='/cloudtrail')

    @app.route('/')
    def index():
        return render_template('index.html')

    # MCP Server routes
    @app.route('/mcp/tools')
    def get_mcp_tools():
        """Get available MCP tools"""
        tools = {}
        
        # ECS tools
        for tool_name, tool_info in ECS_MCP_TOOLS.items():
            tools[tool_name] = {
                'description': tool_info['description'],
                'parameters': tool_info['parameters']
            }
        
        # Secrets Manager tools
        secrets_tools = {
            'secretsmanager_list_secrets': {
                'description': 'Listar todos los secretos en AWS Secrets Manager',
                'parameters': {},
                'function': secretsmanager_tools.list_secrets
            },
            'secretsmanager_create_secret': {
                'description': 'Crear un nuevo secreto en AWS Secrets Manager',
                'parameters': {
                    'name': {'type': 'string', 'description': 'Nombre del secreto', 'required': True},
                    'secret_string': {'type': 'string', 'description': 'Valor del secreto como JSON string', 'required': True},
                    'description': {'type': 'string', 'description': 'Descripción opcional del secreto', 'required': False},
                    'kms_key_id': {'type': 'string', 'description': 'ID de clave KMS opcional', 'required': False},
                    'tags': {'type': 'array', 'description': 'Lista de tags opcional', 'required': False}
                },
                'function': secretsmanager_tools.create_secret
            },
            'secretsmanager_get_secret_value': {
                'description': 'Obtener el valor de un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'version_id': {'type': 'string', 'description': 'ID de versión específico (opcional)', 'required': False},
                    'version_stage': {'type': 'string', 'description': 'Stage de versión (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.get_secret_value
            },
            'secretsmanager_update_secret': {
                'description': 'Actualizar un secreto existente',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'secret_string': {'type': 'string', 'description': 'Nuevo valor del secreto (opcional)', 'required': False},
                    'description': {'type': 'string', 'description': 'Nueva descripción (opcional)', 'required': False},
                    'kms_key_id': {'type': 'string', 'description': 'Nueva clave KMS (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.update_secret
            },
            'secretsmanager_rotate_secret': {
                'description': 'Rotar un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'rotation_lambda_arn': {'type': 'string', 'description': 'ARN de función Lambda para rotación (opcional)', 'required': False},
                    'automatically_after_days': {'type': 'integer', 'description': 'Días para rotación automática (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.rotate_secret
            },
            'secretsmanager_delete_secret': {
                'description': 'Eliminar un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'recovery_window': {'type': 'integer', 'description': 'Días para recuperación (7-30, default: 7)', 'required': False},
                    'force_delete': {'type': 'boolean', 'description': 'Eliminar inmediatamente sin recuperación', 'required': False}
                },
                'function': secretsmanager_tools.delete_secret
            },
            'secretsmanager_restore_secret': {
                'description': 'Restaurar un secreto eliminado',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True}
                },
                'function': secretsmanager_tools.restore_secret
            }
        }
        
        # ACM tools
        acm_tools_dict = {
            'acm_list_certificates': {
                'description': 'Listar todos los certificados en AWS Certificate Manager',
                'parameters': {
                    'max_items': {'type': 'integer', 'description': 'Número máximo de certificados (default: 100)', 'required': False}
                },
                'function': acm_tools.list_certificates
            },
            'acm_request_certificate': {
                'description': 'Solicitar un nuevo certificado SSL/TLS',
                'parameters': {
                    'domain_name': {'type': 'string', 'description': 'Nombre de dominio principal', 'required': True},
                    'validation_method': {'type': 'string', 'description': 'Método de validación (DNS o EMAIL, default: DNS)', 'required': False},
                    'subject_alternative_names': {'type': 'array', 'description': 'Lista de nombres alternativos del sujeto', 'required': False},
                    'key_algorithm': {'type': 'string', 'description': 'Algoritmo de clave (default: RSA_2048)', 'required': False}
                },
                'function': acm_tools.request_certificate
            },
            'acm_describe_certificate': {
                'description': 'Obtener detalles completos de un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado', 'required': True}
                },
                'function': acm_tools.describe_certificate
            },
            'acm_delete_certificate': {
                'description': 'Eliminar un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado a eliminar', 'required': True}
                },
                'function': acm_tools.delete_certificate
            },
            'acm_get_certificate_validation_status': {
                'description': 'Obtener el estado de validación de un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado', 'required': True}
                },
                'function': acm_tools.get_certificate_validation_status
            }
        }
        
        # Combine all tools
        all_tools = {**ECS_MCP_TOOLS, **secrets_tools, **acm_tools_dict, **CLOUDWATCH_MCP_TOOLS, **CONFIG_MCP_TOOLS, **COST_EXPLORER_MCP_TOOLS}
        
        for tool_name, tool_info in all_tools.items():
            tools[tool_name] = {
                'description': tool_info['description'],
                'parameters': tool_info['parameters']
            }
        
        return jsonify(tools)

    @app.route('/mcp/call/<tool_name>', methods=['POST'])
    def call_mcp_tool(tool_name):
        """Call an MCP tool"""
        # Combine all available tools
        secrets_tools = {
            'secretsmanager_list_secrets': {
                'description': 'Listar todos los secretos en AWS Secrets Manager',
                'parameters': {},
                'function': secretsmanager_tools.list_secrets
            },
            'secretsmanager_create_secret': {
                'description': 'Crear un nuevo secreto en AWS Secrets Manager',
                'parameters': {
                    'name': {'type': 'string', 'description': 'Nombre del secreto', 'required': True},
                    'secret_string': {'type': 'string', 'description': 'Valor del secreto como JSON string', 'required': True},
                    'description': {'type': 'string', 'description': 'Descripción opcional del secreto', 'required': False},
                    'kms_key_id': {'type': 'string', 'description': 'ID de clave KMS opcional', 'required': False},
                    'tags': {'type': 'array', 'description': 'Lista de tags opcional', 'required': False}
                },
                'function': secretsmanager_tools.create_secret
            },
            'secretsmanager_get_secret_value': {
                'description': 'Obtener el valor de un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'version_id': {'type': 'string', 'description': 'ID de versión específico (opcional)', 'required': False},
                    'version_stage': {'type': 'string', 'description': 'Stage de versión (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.get_secret_value
            },
            'secretsmanager_update_secret': {
                'description': 'Actualizar un secreto existente',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'secret_string': {'type': 'string', 'description': 'Nuevo valor del secreto (opcional)', 'required': False},
                    'description': {'type': 'string', 'description': 'Nueva descripción (opcional)', 'required': False},
                    'kms_key_id': {'type': 'string', 'description': 'Nueva clave KMS (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.update_secret
            },
            'secretsmanager_rotate_secret': {
                'description': 'Rotar un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'rotation_lambda_arn': {'type': 'string', 'description': 'ARN de función Lambda para rotación (opcional)', 'required': False},
                    'automatically_after_days': {'type': 'integer', 'description': 'Días para rotación automática (opcional)', 'required': False}
                },
                'function': secretsmanager_tools.rotate_secret
            },
            'secretsmanager_delete_secret': {
                'description': 'Eliminar un secreto',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True},
                    'recovery_window': {'type': 'integer', 'description': 'Días para recuperación (7-30, default: 7)', 'required': False},
                    'force_delete': {'type': 'boolean', 'description': 'Eliminar inmediatamente sin recuperación', 'required': False}
                },
                'function': secretsmanager_tools.delete_secret
            },
            'secretsmanager_restore_secret': {
                'description': 'Restaurar un secreto eliminado',
                'parameters': {
                    'secret_name': {'type': 'string', 'description': 'Nombre o ARN del secreto', 'required': True}
                },
                'function': secretsmanager_tools.restore_secret
            }
        }
        
        acm_tools_dict = {
            'acm_list_certificates': {
                'description': 'Listar todos los certificados en AWS Certificate Manager',
                'parameters': {
                    'max_items': {'type': 'integer', 'description': 'Número máximo de certificados (default: 100)', 'required': False}
                },
                'function': acm_tools.list_certificates
            },
            'acm_request_certificate': {
                'description': 'Solicitar un nuevo certificado SSL/TLS',
                'parameters': {
                    'domain_name': {'type': 'string', 'description': 'Nombre de dominio principal', 'required': True},
                    'validation_method': {'type': 'string', 'description': 'Método de validación (DNS o EMAIL, default: DNS)', 'required': False},
                    'subject_alternative_names': {'type': 'array', 'description': 'Lista de nombres alternativos del sujeto', 'required': False},
                    'key_algorithm': {'type': 'string', 'description': 'Algoritmo de clave (default: RSA_2048)', 'required': False}
                },
                'function': acm_tools.request_certificate
            },
            'acm_describe_certificate': {
                'description': 'Obtener detalles completos de un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado', 'required': True}
                },
                'function': acm_tools.describe_certificate
            },
            'acm_delete_certificate': {
                'description': 'Eliminar un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado a eliminar', 'required': True}
                },
                'function': acm_tools.delete_certificate
            },
            'acm_get_certificate_validation_status': {
                'description': 'Obtener el estado de validación de un certificado',
                'parameters': {
                    'certificate_arn': {'type': 'string', 'description': 'ARN del certificado', 'required': True}
                },
                'function': acm_tools.get_certificate_validation_status
            }
        }
        
        # CloudWatch tools
        from app.mcp_server.cloudwatch_mcp_tools import (put_metric_alarm, delete_alarm, put_metric_data, get_metric_statistics, list_metrics)
        
        cloudwatch_tools = {
            'put_metric_alarm': {
                'description': 'Crear una nueva alarma métrica en CloudWatch',
                'parameters': CLOUDWATCH_MCP_TOOLS['put_metric_alarm']['parameters'],
                'function': put_metric_alarm
            },
            'delete_alarm': {
                'description': 'Eliminar una alarma de CloudWatch',
                'parameters': CLOUDWATCH_MCP_TOOLS['delete_alarm']['parameters'],
                'function': delete_alarm
            },
            'put_metric_data': {
                'description': 'Enviar datos métricos personalizados a CloudWatch',
                'parameters': CLOUDWATCH_MCP_TOOLS['put_metric_data']['parameters'],
                'function': put_metric_data
            },
            'get_metric_statistics': {
                'description': 'Obtener estadísticas de una métrica específica',
                'parameters': CLOUDWATCH_MCP_TOOLS['get_metric_statistics']['parameters'],
                'function': get_metric_statistics
            },
            'list_metrics': {
                'description': 'Listar métricas disponibles en CloudWatch',
                'parameters': CLOUDWATCH_MCP_TOOLS['list_metrics']['parameters'],
                'function': list_metrics
            }
        }
        
        # Config tools
        from app.mcp_server.config_mcp_tools import (
            list_config_rules, put_config_rule, delete_config_rule, get_compliance_details
        )
        
        # Cost Explorer tools
        from app.mcp_server.cost_explorer_mcp_tools import cost_explorer_tools as ce_tools_instance
        from app.mcp_server.cost_explorer_mcp_tools import (
            CostExplorerMCPTools
        )
        
        ce_tools = CostExplorerMCPTools()
        
        # Bedrock tools
        bedrock_tools_dict = {
            'bedrock_list_foundation_models': {
                'description': 'Listar modelos foundation disponibles en Amazon Bedrock',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True}
                },
                'function': bedrock_tools.list_foundation_models
            },
            'bedrock_invoke_model': {
                'description': 'Invocar un modelo de IA en Amazon Bedrock',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'model_id': {'type': 'string', 'description': 'ID del modelo', 'required': True},
                    'prompt': {'type': 'string', 'description': 'Prompt para el modelo', 'required': True},
                    'max_tokens': {'type': 'integer', 'description': 'Máximo de tokens', 'required': False},
                    'temperature': {'type': 'number', 'description': 'Temperatura', 'required': False},
                    'top_p': {'type': 'number', 'description': 'Top P', 'required': False}
                },
                'function': bedrock_tools.invoke_model
            },
            'bedrock_create_model_customization_job': {
                'description': 'Crear un trabajo de customización de modelo en Amazon Bedrock',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'job_name': {'type': 'string', 'description': 'Nombre del trabajo', 'required': True},
                    'base_model_id': {'type': 'string', 'description': 'ID del modelo base', 'required': True},
                    'customization_type': {'type': 'string', 'description': 'Tipo de customización', 'required': True},
                    'training_data_s3_uri': {'type': 'string', 'description': 'URI S3 de datos de entrenamiento', 'required': True},
                    'validation_data_s3_uri': {'type': 'string', 'description': 'URI S3 de datos de validación', 'required': False},
                    'output_data_s3_uri': {'type': 'string', 'description': 'URI S3 de salida', 'required': True},
                    'role_arn': {'type': 'string', 'description': 'ARN del rol IAM', 'required': True}
                },
                'function': bedrock_tools.create_model_customization_job
            }
        }
        
        # Rekognition tools
        rekognition_tools_dict = {
            'rekognition_detect_labels': {
                'description': 'Detectar etiquetas (objetos, escenas) en una imagen usando Amazon Rekognition',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'image_bytes': {'type': 'string', 'description': 'Bytes de la imagen en base64', 'required': True},
                    'max_labels': {'type': 'integer', 'description': 'Máximo número de etiquetas', 'required': False},
                    'min_confidence': {'type': 'number', 'description': 'Confianza mínima', 'required': False}
                },
                'function': rekognition_tools.detect_labels
            },
            'rekognition_detect_faces': {
                'description': 'Detectar rostros en una imagen usando Amazon Rekognition',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'image_bytes': {'type': 'string', 'description': 'Bytes de la imagen en base64', 'required': True},
                    'attributes': {'type': 'array', 'description': 'Atributos a detectar', 'required': False}
                },
                'function': rekognition_tools.detect_faces
            },
            'rekognition_compare_faces': {
                'description': 'Comparar dos rostros para verificar similitud usando Amazon Rekognition',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'source_image_bytes': {'type': 'string', 'description': 'Bytes de la imagen fuente en base64', 'required': True},
                    'target_image_bytes': {'type': 'string', 'description': 'Bytes de la imagen objetivo en base64', 'required': True},
                    'similarity_threshold': {'type': 'number', 'description': 'Umbral de similitud', 'required': False}
                },
                'function': rekognition_tools.compare_faces
            },
            'rekognition_detect_text': {
                'description': 'Detectar texto en una imagen usando Amazon Rekognition',
                'parameters': {
                    'region': {'type': 'string', 'description': 'Región de AWS', 'required': True},
                    'image_bytes': {'type': 'string', 'description': 'Bytes de la imagen en base64', 'required': True}
                },
                'function': rekognition_tools.detect_text
            }
        }
        
        # Kinesis tools
        kinesis_tools_dict = {
            'kinesis_create_stream': {
                'description': 'Crear un nuevo stream de Kinesis',
                'parameters': {
                    'stream_name': {'type': 'string', 'description': 'Nombre del stream', 'required': True},
                    'shard_count': {'type': 'integer', 'description': 'Número de shards (default: 1)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': kinesis_tools.create_stream
            },
            'kinesis_delete_stream': {
                'description': 'Eliminar un stream de Kinesis',
                'parameters': {
                    'stream_name': {'type': 'string', 'description': 'Nombre del stream a eliminar', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': kinesis_tools.delete_stream
            },
            'kinesis_put_record': {
                'description': 'Enviar un registro a un stream de Kinesis',
                'parameters': {
                    'stream_name': {'type': 'string', 'description': 'Nombre del stream', 'required': True},
                    'data': {'type': 'string', 'description': 'Datos del registro', 'required': True},
                    'partition_key': {'type': 'string', 'description': 'Clave de partición', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': kinesis_tools.put_record
            },
            'kinesis_get_records': {
                'description': 'Obtener registros de un shard específico en un stream de Kinesis',
                'parameters': {
                    'stream_name': {'type': 'string', 'description': 'Nombre del stream', 'required': True},
                    'shard_id': {'type': 'string', 'description': 'ID del shard', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': kinesis_tools.get_records
            }
        }
        
        # Athena tools
        athena_tools_dict = {
            'athena_list_query_executions': {
                'description': 'Listar ejecuciones de consultas recientes en Athena',
                'parameters': {
                    'max_results': {'type': 'integer', 'description': 'Número máximo de resultados (default: 50)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': athena_tools.list_query_executions
            },
            'athena_start_query_execution': {
                'description': 'Iniciar la ejecución de una consulta SQL en Athena',
                'parameters': {
                    'query': {'type': 'string', 'description': 'Consulta SQL a ejecutar', 'required': True},
                    'database': {'type': 'string', 'description': 'Base de datos/catalog (default: default)', 'required': False},
                    'workgroup': {'type': 'string', 'description': 'Workgroup de Athena (default: primary)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': athena_tools.start_query_execution
            },
            'athena_stop_query_execution': {
                'description': 'Detener una consulta en ejecución en Athena',
                'parameters': {
                    'execution_id': {'type': 'string', 'description': 'ID de la ejecución de consulta', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': athena_tools.stop_query_execution
            },
            'athena_get_query_results': {
                'description': 'Obtener resultados de una consulta ejecutada en Athena',
                'parameters': {
                    'execution_id': {'type': 'string', 'description': 'ID de la ejecución de consulta', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': athena_tools.get_query_results
            }
        }
        
        # Glue tools
        glue_tools_dict = {
            'glue_list_crawlers': {
                'description': 'Listar crawlers de AWS Glue',
                'parameters': {
                    'max_results': {'type': 'integer', 'description': 'Número máximo de resultados (default: 50)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.list_crawlers
            },
            'glue_create_crawler': {
                'description': 'Crear un nuevo crawler en AWS Glue',
                'parameters': {
                    'crawler_name': {'type': 'string', 'description': 'Nombre del crawler', 'required': True},
                    'role': {'type': 'string', 'description': 'ARN del rol IAM', 'required': True},
                    'database_name': {'type': 'string', 'description': 'Nombre de la base de datos', 'required': True},
                    's3_targets': {'type': 'array', 'description': 'Lista de rutas S3', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.create_crawler
            },
            'glue_start_crawler': {
                'description': 'Iniciar un crawler en AWS Glue',
                'parameters': {
                    'crawler_name': {'type': 'string', 'description': 'Nombre del crawler', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.start_crawler
            },
            'glue_list_jobs': {
                'description': 'Listar jobs ETL de AWS Glue',
                'parameters': {
                    'max_results': {'type': 'integer', 'description': 'Número máximo de resultados (default: 50)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.list_jobs
            },
            'glue_create_job': {
                'description': 'Crear un nuevo job ETL en AWS Glue',
                'parameters': {
                    'job_name': {'type': 'string', 'description': 'Nombre del job', 'required': True},
                    'role': {'type': 'string', 'description': 'ARN del rol IAM', 'required': True},
                    'script_location': {'type': 'string', 'description': 'Ubicación del script en S3', 'required': True},
                    'max_capacity': {'type': 'number', 'description': 'Capacidad máxima (default: 2.0)', 'required': False},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.create_job
            },
            'glue_start_job_run': {
                'description': 'Ejecutar un job ETL en AWS Glue',
                'parameters': {
                    'job_name': {'type': 'string', 'description': 'Nombre del job', 'required': True},
                    'region': {'type': 'string', 'description': 'Región de AWS (default: us-east-1)', 'required': False}
                },
                'function': glue_tools.start_job_run
            }
        }
        
        # EMR tools
        emr_tools_dict = {
            'emr_list_clusters': {
                'description': 'Listar clusters de Amazon EMR',
                'parameters': {},
                'function': list_emr_clusters
            },
            'emr_create_cluster': {
                'description': 'Crear un nuevo cluster en Amazon EMR',
                'parameters': {
                    'cluster_name': {'type': 'string', 'description': 'Nombre del cluster', 'required': True},
                    'instance_count': {'type': 'integer', 'description': 'Número de instancias (default: 3)', 'required': False},
                    'instance_type': {'type': 'string', 'description': 'Tipo de instancia (default: m5.xlarge)', 'required': False},
                    'release_label': {'type': 'string', 'description': 'Versión de EMR (default: emr-6.4.0)', 'required': False}
                },
                'function': create_emr_cluster
            },
            'emr_terminate_cluster': {
                'description': 'Terminar un cluster de Amazon EMR',
                'parameters': {
                    'cluster_id': {'type': 'string', 'description': 'ID del cluster a terminar', 'required': True}
                },
                'function': terminate_emr_cluster
            }
        }
        
        config_tools = {
            'list_config_rules': {
                'description': 'Listar todas las reglas de AWS Config',
                'parameters': CONFIG_MCP_TOOLS['list_config_rules']['parameters'],
                'function': list_config_rules
            },
            'put_config_rule': {
                'description': 'Crear o actualizar una regla de AWS Config',
                'parameters': CONFIG_MCP_TOOLS['put_config_rule']['parameters'],
                'function': put_config_rule
            },
            'delete_config_rule': {
                'description': 'Eliminar una regla de AWS Config',
                'parameters': CONFIG_MCP_TOOLS['delete_config_rules']['parameters'],
                'function': delete_config_rule
            },
            'get_compliance_details': {
                'description': 'Obtener detalles de cumplimiento para una regla específica',
                'parameters': CONFIG_MCP_TOOLS['get_compliance_details']['parameters'],
                'function': get_compliance_details
            }
        }
        
        # Cost Explorer tools
        cost_explorer_tools = {
            'get_cost_forecast': {
                'description': 'Obtener pronóstico de costos de AWS para un período futuro',
                'parameters': COST_EXPLORER_MCP_TOOLS[0]['parameters'] if COST_EXPLORER_MCP_TOOLS else {},
                'function': ce_tools.get_cost_forecast
            },
            'get_cost_categories': {
                'description': 'Obtener desglose de costos por categoría/servicio',
                'parameters': COST_EXPLORER_MCP_TOOLS[1]['parameters'] if len(COST_EXPLORER_MCP_TOOLS) > 1 else {},
                'function': ce_tools.get_cost_categories
            },
            'get_savings_plans_utilization': {
                'description': 'Obtener información de utilización de Savings Plans',
                'parameters': COST_EXPLORER_MCP_TOOLS[2]['parameters'] if len(COST_EXPLORER_MCP_TOOLS) > 2 else {},
                'function': ce_tools.get_savings_plans_utilization
            }
        }
        
        all_tools = {**ECS_MCP_TOOLS, **secrets_tools, **acm_tools_dict, **cloudwatch_tools, **config_tools, **cost_explorer_tools, **bedrock_tools_dict, **rekognition_tools_dict, **kinesis_tools_dict, **athena_tools_dict, **glue_tools_dict, **emr_tools_dict}
        
        if tool_name not in all_tools:
            return jsonify({'error': f'Tool {tool_name} not found'}), 404

        tool_info = all_tools[tool_name]
        data = request.get_json() or {}

        # Validate required parameters
        required_params = [param for param, info in tool_info['parameters'].items() if info.get('required', True)]
        missing_params = [param for param in required_params if param not in data]

        if missing_params:
            return jsonify({'error': f'Missing required parameters: {missing_params}'}), 400

        try:
            # Call the tool function with parameters
            result = tool_info['function'](**data)
            return jsonify({'result': result})
        except Exception as e:
            return jsonify({'error': f'Tool execution failed: {str(e)}'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')