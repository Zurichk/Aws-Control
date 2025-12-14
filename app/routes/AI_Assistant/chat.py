import os
import json
import uuid
import logging
import google.generativeai as genai
from openai import OpenAI
from flask import Blueprint, render_template, request, jsonify, session
from app.utils.aws_client import get_aws_client
from app.mcp_server import get_mcp_server

bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

def make_serializable(obj):
    """Convierte objetos no serializables a JSON (protobuf, RepeatedComposite, etc.)"""
    # Tipos básicos que ya son serializables
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # Listas y tuplas (incluyendo RepeatedComposite de protobuf)
    if isinstance(obj, (list, tuple)) or hasattr(obj, '__iter__') and not isinstance(obj, (str, dict)):
        try:
            return [make_serializable(item) for item in obj]
        except:
            return str(obj)
    
    # Diccionarios
    if isinstance(obj, dict):
        try:
            return {str(key): make_serializable(value) for key, value in obj.items()}
        except:
            return str(obj)
    
    # Objetos protobuf y otros con __dict__
    if hasattr(obj, '__dict__'):
        try:
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Ignorar atributos privados
                    result[key] = make_serializable(value)
            return result
        except:
            return str(obj)
    
    # Para cualquier otro tipo, convertir a string
    try:
        return str(obj)
    except:
        return repr(obj)

# Configure AI providers
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini').lower()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info(f"Gemini API Key configurada: {GEMINI_API_KEY[:10]}...")
else:
    logger.warning("No se encontró GEMINI_API_KEY en las variables de entorno")

# Configure DeepSeek
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    logger.info(f"DeepSeek API Key configurada: {DEEPSEEK_API_KEY[:10]}...")
else:
    logger.warning("No se encontró DEEPSEEK_API_KEY en las variables de entorno")
    deepseek_client = None

logger.info(f"Proveedor de IA activo: {AI_PROVIDER.upper()}")

# Almacenar historiales de chat en memoria (para producción usar Redis o base de datos)
chat_sessions = {}

# # System prompt with AWS services information
# SYSTEM_PROMPT = """
# Eres un asistente experto en AWS que ayuda a los usuarios a aprender y usar servicios de AWS a través de un panel de control web.

# INFORMACIÓN DE SERVICIOS DISPONIBLES EN EL PANEL:

# SERVICIOS DE COMPUTO:
# - EC2: Instancias de servidor virtual en la nube
# - Lambda: Computación serverless, ejecuta código sin servidores
# - ECS: Servicio de contenedores elásticos para Docker

# SERVICIOS DE ALMACENAMIENTO:
# - S3: Almacenamiento de objetos escalable y duradero

# SERVICIOS DE BASE DE DATOS:
# - RDS: Bases de datos relacionales administradas (MySQL, PostgreSQL, etc.)
# - DynamoDB: Base de datos NoSQL completamente administrada

# SERVICIOS DE MENSAJERÍA:
# - SNS: Servicio de notificaciones simples (pub/sub)
# - SQS: Servicio de colas de mensajes

# SERVICIOS DE REDES:
# - VPC: Redes virtuales privadas
# - Route 53: Servicio de DNS
# - ELB: Load Balancers para distribución de tráfico
# - CloudFront: CDN para distribución de contenido
# - API Gateway: Creación y gestión de APIs REST/HTTP/WebSocket

# SERVICIOS DE SEGURIDAD:
# - IAM: Gestión de identidades y accesos
# - KMS: Servicio de administración de claves de encriptación

# SERVICIOS DE ANALYTICS:
# - Kinesis: Procesamiento de datos en streaming en tiempo real

# SERVICIOS DE CONTENEDORES:
# - ECS: Orquestación de contenedores Docker

# SERVICIOS DE MACHINE LEARNING:
# - SageMaker: Plataforma completa para ML (notebooks, training, deployment)

# SERVICIOS DE GESTIÓN:
# - CloudFormation: Infraestructura como código
# - CloudWatch: Monitoreo y logging

# ESTRUCTURA DEL PANEL WEB:
# - Navegación organizada por categorías (Computo, Almacenamiento, Base de Datos, etc.)
# - Cada servicio tiene su propia página con:
#   * Descripción detallada del servicio
#   * Lista de recursos actuales
#   * Botones para crear nuevos recursos
#   * Información educativa sobre el servicio

# TU FUNCIÓN:
# 1. Guiar a los usuarios paso a paso para completar tareas específicas
# 2. Explicar conceptos de AWS de manera clara y educativa
# 3. Recomendar qué servicios usar para diferentes casos de uso
# 4. Ayudar a entender la interfaz del panel web
# 5. Dar consejos sobre mejores prácticas de AWS
# 6. Responder preguntas sobre arquitectura y diseño de soluciones
# 7. **PUEDES EJECUTAR ACCIONES REALES EN AWS** usando las herramientas disponibles

# HERRAMIENTAS DISPONIBLES:

# BÚSQUEDA Y CONSULTA (11):
# - search_amis: Buscar AMIs disponibles con filtros
# - list_ec2_instances: Listar instancias EC2
# - list_vpcs: Listar VPCs
# - describe_vpc: Detalles completos de una VPC
# - list_s3_buckets: Listar buckets S3
# - list_security_groups: Listar security groups
# - list_subnets: Listar subnets
# - list_load_balancers: Listar ALB/NLB
# - list_target_groups: Listar target groups
# - list_autoscaling_groups: Listar ASG
# - list_rds_instances: Listar instancias RDS
# - list_dynamodb_tables: Listar tablas DynamoDB

# CREACIÓN DE RECURSOS (9):
# - create_ec2_instance: Crear instancias EC2
# - create_secure_vpc: Crear VPCs seguras
# - create_security_group: Crear security groups
# - create_s3_bucket: Crear buckets S3
# - create_ami_from_instance: Crear AMI desde una instancia
# - create_target_group: Crear target group para ELB
# - create_launch_template: Crear Launch Template
# - create_autoscaling_group: Crear Auto Scaling Group

# GESTIÓN DE INSTANCIAS (4):
# - stop_ec2_instance: Detener instancias
# - start_ec2_instance: Iniciar instancias detenidas
# - modify_instance_security_groups: Modificar security groups de una instancia
# - terminate_ec2_instance: Terminar instancias

# COSTOS (1):
# - get_aws_costs: Consultar costos

# FLUJO COMPLETO PARA AUTO SCALING:
# 1. Usar search_amis para encontrar o create_ami_from_instance para crear AMI personalizada
# 2. Crear Launch Template con create_launch_template
# 3. Crear Target Group con create_target_group (si se usa con load balancer)
# 4. Crear Auto Scaling Group con create_autoscaling_group
# 5. Opcionalmente listar con list_autoscaling_groups para verificar

# FLUJO PARA LOAD BALANCING:
# 1. Crear Target Group con create_target_group
# 2. Los load balancers se pueden listar con list_load_balancers
# 3. Los target groups se listan con list_target_groups

# GESTIÓN DE SECURITY GROUPS EN INSTANCIAS:
# - Si el usuario pide "asignar un security group a una instancia", usa modify_instance_security_groups
# - Esta herramienta REEMPLAZA todos los security groups actuales con los nuevos
# - No requiere detener la instancia, funciona con instancias running o stopped
# - Después de modificar, la instancia mantiene su estado (running/stopped)
# - Ejemplo: modify_instance_security_groups(instance_id="i-xxx", security_group_ids=["sg-xxx", "sg-yyy"])

# CONTROL DE ESTADO DE INSTANCIAS:
# - start_ec2_instance: Inicia una instancia que está stopped
# - stop_ec2_instance: Detiene una instancia que está running
# - terminate_ec2_instance: Elimina permanentemente una instancia

# IMPORTANTE SOBRE AMIs:
# - Antes de crear una instancia EC2, puedes buscar AMIs disponibles usando search_amis
# - Si el usuario pide "Ubuntu", "Amazon Linux", "Windows Server", etc., BUSCA la AMI primero
# - Si el usuario no especifica AMI, usa búsqueda para encontrar la más apropiada
# - Las AMIs tienen formato ami-XXXXXXXX
# - Las AMIs de Amazon (owner=amazon) son las más comunes y confiables
# - Para Linux usa platform=linux, para Windows usa platform=windows

# INSTRUCCIONES DE RESPUESTA:
# - Sé educativo pero conciso
# - Usa ejemplos prácticos cuando sea posible
# - **IMPORTANTE: Si el usuario pide crear/modificar/listar recursos, EJECUTA LA HERRAMIENTA INMEDIATAMENTE sin anunciar que lo vas a hacer**
# - Primero ejecuta, luego explica qué se creó
# - Si mencionan servicios específicos, explica cómo usarlos en el panel
# - Mantén un tono amigable y profesional
# - Si no sabes algo específico, admítelo y sugiere alternativas

# EJEMPLO DE USO CORRECTO:
# Usuario: "Créame un bucket S3 llamado mi-bucket"
# Tú: [EJECUTAS create_s3_bucket inmediatamente]
# Tú: "✅ He creado el bucket S3 'mi-bucket' en us-east-1 con:
# - Versionado habilitado
# - Encriptación AES256
# - Acceso público bloqueado"

# EJEMPLO INCORRECTO (NO HAGAS ESTO):
# Usuario: "Créame un bucket S3"
# Tú: "¡Claro! Voy a crear un bucket S3..." ❌ NO ANUNCIES, EJECUTA DIRECTAMENTE
# [Usas la herramienta create_ec2_instance]
# Tú: "✅ He creado exitosamente: [detalles de la instancia]"

# Usuario: "Asigna el security group sg-xxx a la instancia i-yyy"
# Tú: "¡Perfecto! Voy a asignar ese security group a la instancia..."
# [Usas modify_instance_security_groups]
# Tú: "✅ Security group asignado. La instancia mantiene su estado actual."

# Recuerda: Tu objetivo es ayudar a los usuarios a aprender AWS mientras usan este panel de control educativo, Y PUEDES EJECUTAR ACCIONES REALES.
# """
# System prompt MINIMALISTA para evitar sobrecarga de tokens con 252 herramientas
SYSTEM_PROMPT = """Eres un asistente AWS que ejecuta acciones reales. Cuando el usuario pida listar/crear/modificar recursos AWS, ejecuta la herramienta correspondiente inmediatamente y luego explica brevemente qué hiciste."""



@bp.route('/')
def index():
    # Generar o recuperar session_id
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    return render_template('AI_Assistant/chat/index.html', session_id=session['chat_session_id'])

@bp.route('/get_ai_provider', methods=['GET'])
def get_ai_provider():
    """Obtener el proveedor de IA actual"""
    try:
        current_provider = session.get('ai_provider', AI_PROVIDER)
        return jsonify({
            'status': 'success',
            'provider': current_provider,
            'available_providers': ['gemini', 'deepseek']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@bp.route('/clear_history', methods=['POST'])
def clear_history():
    """Limpiar el historial de chat"""
    try:
        session_id = session.get('chat_session_id')
        if session_id and session_id in chat_sessions:
            del chat_sessions[session_id]
        # Generar nuevo session_id
        session['chat_session_id'] = str(uuid.uuid4())
        return jsonify({'status': 'success', 'message': 'Historial limpiado'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@bp.route('/get_tools', methods=['GET'])
def get_tools():
    """Obtener listado de todas las herramientas disponibles organizadas por categoría"""
    try:
        mcp_server = get_mcp_server()
        all_tools = mcp_server.get_all_tools()
        
        # Organizar herramientas por categoría
        tools_by_category = {}
        
        for tool in all_tools:
            tool_name = tool.get('name', '')
            description = tool.get('description', 'Sin descripción')
            
            # Determinar categoría basándose en el prefijo del nombre
            if tool_name.startswith('ec2_'):
                category = 'EC2 (Compute)'
            elif tool_name.startswith('lambda_'):
                category = 'Lambda (Serverless)'
            elif tool_name.startswith('s3_'):
                category = 'S3 (Storage)'
            elif tool_name.startswith('rds_'):
                category = 'RDS (Database)'
            elif tool_name.startswith('dynamodb_'):
                category = 'DynamoDB (NoSQL)'
            elif tool_name.startswith('sns_'):
                category = 'SNS (Messaging)'
            elif tool_name.startswith('sqs_'):
                category = 'SQS (Queuing)'
            elif tool_name.startswith('vpc_'):
                category = 'VPC (Networking)'
            elif tool_name.startswith('iam_'):
                category = 'IAM (Security)'
            elif tool_name.startswith('kinesis_'):
                category = 'Kinesis (Analytics)'
            elif tool_name.startswith('ecs_'):
                category = 'ECS (Containers)'
            elif tool_name.startswith('sagemaker_'):
                category = 'SageMaker (ML/AI)'
            elif tool_name.startswith('cloudformation_'):
                category = 'CloudFormation (IaC)'
            elif tool_name.startswith('cloudwatch_'):
                category = 'CloudWatch (Monitoring)'
            else:
                category = 'Otros'
            
            if category not in tools_by_category:
                tools_by_category[category] = []
            
            tools_by_category[category].append({
                'name': tool_name,
                'description': description
            })
        
        # Ordenar categorías y herramientas
        sorted_categories = {}
        for category in sorted(tools_by_category.keys()):
            sorted_categories[category] = sorted(tools_by_category[category], key=lambda x: x['name'])
        
        return jsonify({
            'status': 'success',
            'tools_by_category': sorted_categories,
            'total_tools': len(all_tools)
        })
    except Exception as e:
        logger.error(f"Error obteniendo herramientas: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


def process_with_deepseek(user_message, session_id, tools_definition, mcp_server):
    """Procesa un mensaje usando DeepSeek API"""
    try:
        if not deepseek_client:
            return {
                'error': 'DeepSeek no está configurado. Por favor configura DEEPSEEK_API_KEY.',
                'response': '',
                'tool_results': [],
                'status': 'error'
            }
        
        # Convertir herramientas a formato OpenAI
        tools_for_deepseek = []
        for tool in tools_definition:
            tool_schema = {
                'type': 'function',
                'function': {
                    'name': tool['name'],
                    'description': tool['description'],
                    'parameters': {
                        'type': 'object',
                        'properties': {},
                        'required': []
                    }
                }
            }
            
            # Agregar parámetros si existen
            if 'parameters' in tool and 'properties' in tool['parameters']:
                tool_schema['function']['parameters']['properties'] = tool['parameters']['properties']
                if 'required' in tool['parameters']:
                    tool_schema['function']['parameters']['required'] = tool['parameters']['required']
            
            tools_for_deepseek.append(tool_schema)
        
        # Recuperar o crear historial
        if session_id not in chat_sessions:
            chat_sessions[session_id] = [
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT
                }
            ]
        
        # Limitar historial
        MAX_HISTORY_MESSAGES = 10
        history = chat_sessions[session_id]
        if len(history) > MAX_HISTORY_MESSAGES + 1:  # +1 por el system message
            history = [history[0]] + history[-(MAX_HISTORY_MESSAGES):]
            chat_sessions[session_id] = history
        
        # Agregar mensaje del usuario
        messages = history + [{'role': 'user', 'content': user_message}]
        
        # Llamar a DeepSeek
        response = deepseek_client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools_for_deepseek if tools_for_deepseek else None,
            tool_choice='auto' if tools_for_deepseek else None,
            temperature=0.7,
            max_tokens=4000
        )
        
        # Procesar respuesta
        final_response = ""
        tool_results = []
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            message = response.choices[0].message
            
            # Si hay texto en la respuesta
            if message.content:
                final_response += message.content
            
            # Si hay tool calls
            if message.tool_calls:
                # Agregar el mensaje del asistente al historial
                messages.append({
                    'role': 'assistant',
                    'content': message.content,
                    'tool_calls': [
                        {
                            'id': tc.id,
                            'type': 'function',
                            'function': {
                                'name': tc.function.name,
                                'arguments': tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })
                
                # Ejecutar cada tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"DeepSeek function call: {function_name} with args: {function_args}")
                    
                    # Ejecutar la herramienta
                    result = mcp_server.execute_tool(function_name, function_args)
                    serializable_result = make_serializable(result)
                    
                    # Guardar resultado
                    tool_results.append({
                        'tool': function_name,
                        'args': function_args,
                        'result': serializable_result
                    })
                    
                    # Agregar resultado al historial
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': json.dumps(serializable_result)
                    })
                
                # Llamar de nuevo con los resultados
                response = deepseek_client.chat.completions.create(
                    model='deepseek-chat',
                    messages=messages,
                    tools=tools_for_deepseek if tools_for_deepseek else None,
                    tool_choice='auto' if tools_for_deepseek else None,
                    temperature=0.7,
                    max_tokens=4000
                )
            else:
                # No hay más tool calls, terminar
                messages.append({
                    'role': 'assistant',
                    'content': message.content
                })
                break
        
        # Actualizar historial (solo últimos mensajes sin tool calls para simplificar)
        simplified_history = [msg for msg in messages if msg['role'] in ['system', 'user', 'assistant'] and 'tool_calls' not in msg]
        chat_sessions[session_id] = simplified_history
        
        return {
            'response': final_response,
            'tool_results': tool_results,
            'status': 'success'
        }
        
    except Exception as e:
        logger.error(f"Error en DeepSeek: {str(e)}")
        import traceback
        return {
            'error': f'Error con DeepSeek: {str(e)}',
            'traceback': traceback.format_exc(),
            'status': 'error'
        }


@bp.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Obtener o crear session_id
        session_id = session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chat_session_id'] = session_id

        # Obtener MCP server
        mcp_server = get_mcp_server()
        all_tools = mcp_server.get_tools()
        
        # FILTRAR HERRAMIENTAS PRINCIPALES para reducir consumo de tokens
        # Solo pasamos las herramientas más comunes/importantes (30-40 en lugar de 252)
        priority_tools = [
            # EC2
            'ec2_list_instances', 'ec2_create_instance', 'ec2_terminate_instance',
            'ec2_start_instance', 'ec2_stop_instance', 'ec2_list_amis',
            # VPC
            'vpc_describe_vpcs', 'vpc_create_vpc', 'vpc_describe_subnets',
            'vpc_create_subnet', 'vpc_describe_security_groups', 'vpc_create_security_group',
            'vpc_authorize_security_group_ingress',
            # S3
            's3_list_buckets', 's3_create_bucket', 's3_delete_bucket',
            # Lambda
            'lambda_list_functions', 'lambda_create_function', 'lambda_invoke_function',
            # IAM
            'iam_list_users', 'iam_create_user', 'iam_list_roles',
            # RDS
            'rds_list_instances', 'rds_create_instance',
            # DynamoDB
            'dynamodb_list_tables', 'dynamodb_create_table',
            # Key Pairs
            'ec2_list_key_pairs', 'ec2_create_key_pair'
        ]
        
        tools_definition = [tool for tool in all_tools if tool['name'] in priority_tools]
        logger.info(f"Herramientas filtradas: {len(tools_definition)} de {len(all_tools)} totales")
        logger.info(f"Herramientas disponibles: {[t['name'] for t in tools_definition]}")
        
        # Determinar qué proveedor usar (permitir override desde sesión)
        current_provider = session.get('ai_provider', AI_PROVIDER)
        logger.info(f"Usando proveedor de IA: {current_provider.upper()}")
        
        # Si se selecciona DeepSeek, usar la función auxiliar
        if current_provider == 'deepseek':
            result = process_with_deepseek(user_message, session_id, tools_definition, mcp_server)
            if result['status'] == 'error':
                return jsonify(result), 500
            return jsonify(result)
        
        # Si se llega aquí, usar Gemini (comportamiento por defecto)
        # Convertir herramientas a formato simple para Gemini
        tools_for_gemini = []
        for tool in tools_definition:
            try:
                # Verificar si la herramienta tiene parámetros en formato schema
                if 'parameters' in tool and isinstance(tool['parameters'], dict):
                    if 'properties' in tool['parameters']:
                        # Formato completo con schema JSON
                        properties = {}
                        for prop_name, prop_def in tool['parameters']['properties'].items():
                            if isinstance(prop_def, dict):
                                prop_type = prop_def.get('type', 'string').upper()
                                
                                # Convertir a formato simple
                                simple_prop = {'type_': prop_type}
                                
                                if 'description' in prop_def:
                                    simple_prop['description'] = prop_def['description']
                                    
                                # Manejar enums
                                if 'enum' in prop_def:
                                    simple_prop['enum'] = prop_def['enum']
                                
                                # Manejar arrays (con recursión para arrays anidados)
                                if prop_type == 'ARRAY':
                                    if 'items' in prop_def:
                                        items_def = prop_def['items']
                                        items_type = items_def.get('type', 'string').upper()
                                        
                                        # Si el item es un objeto, procesar sus propiedades recursivamente
                                        if items_type == 'OBJECT' and 'properties' in items_def:
                                            item_properties = {}
                                            for item_prop_name, item_prop_def in items_def['properties'].items():
                                                if isinstance(item_prop_def, dict):
                                                    item_prop_type = item_prop_def.get('type', 'string').upper()
                                                    item_simple_prop = {'type_': item_prop_type}
                                                    if 'description' in item_prop_def:
                                                        item_simple_prop['description'] = item_prop_def['description']
                                                    
                                                    # Si esta propiedad también es un array, procesarlo
                                                    if item_prop_type == 'ARRAY' and 'items' in item_prop_def:
                                                        nested_items_def = item_prop_def['items']
                                                        nested_items_type = nested_items_def.get('type', 'string').upper()
                                                        
                                                        # Si el item anidado es objeto con propiedades
                                                        if nested_items_type == 'OBJECT' and 'properties' in nested_items_def:
                                                            nested_props = {}
                                                            for nested_prop_name, nested_prop_def in nested_items_def['properties'].items():
                                                                if isinstance(nested_prop_def, dict):
                                                                    nested_prop_type = nested_prop_def.get('type', 'string').upper()
                                                                    nested_simple_prop = {'type_': nested_prop_type}
                                                                    if 'description' in nested_prop_def:
                                                                        nested_simple_prop['description'] = nested_prop_def['description']
                                                                    nested_props[nested_prop_name] = genai.protos.Schema(**nested_simple_prop)
                                                            
                                                            item_simple_prop['items'] = genai.protos.Schema(
                                                                type_=nested_items_type,
                                                                properties=nested_props
                                                            )
                                                        else:
                                                            item_simple_prop['items'] = genai.protos.Schema(type_=nested_items_type)
                                                    
                                                    item_properties[item_prop_name] = genai.protos.Schema(**item_simple_prop)
                                            
                                            simple_prop['items'] = genai.protos.Schema(
                                                type_=items_type,
                                                properties=item_properties
                                            )
                                        else:
                                            simple_prop['items'] = genai.protos.Schema(type_=items_type)
                                    else:
                                        simple_prop['items'] = genai.protos.Schema(type_='STRING')
                                    
                                    # IMPORTANTE: Los enums no están permitidos en arrays en Gemini
                                    # Si un array tiene enum, lo removemos para evitar el error
                                    if 'enum' in simple_prop:
                                        del simple_prop['enum']
                                
                                # Manejar objetos (con soporte para arrays dentro)
                                if prop_type == 'OBJECT':
                                    if 'properties' in prop_def:
                                        obj_properties = {}
                                        for obj_prop_name, obj_prop_def in prop_def['properties'].items():
                                            if isinstance(obj_prop_def, dict):
                                                obj_prop_type = obj_prop_def.get('type', 'string').upper()
                                                obj_simple_prop = {'type_': obj_prop_type}
                                                if 'description' in obj_prop_def:
                                                    obj_simple_prop['description'] = obj_prop_def['description']
                                                
                                                # Si la propiedad del objeto es un array, procesar sus items
                                                if obj_prop_type == 'ARRAY' and 'items' in obj_prop_def:
                                                    obj_items_def = obj_prop_def['items']
                                                    obj_items_type = obj_items_def.get('type', 'string').upper()
                                                    obj_simple_prop['items'] = genai.protos.Schema(type_=obj_items_type)
                                                
                                                obj_properties[obj_prop_name] = genai.protos.Schema(**obj_simple_prop)
                                        simple_prop['properties'] = obj_properties
                                    else:
                                        simple_prop['properties'] = {}
                                
                                properties[prop_name] = genai.protos.Schema(**simple_prop)
                        
                        function_declaration = genai.protos.FunctionDeclaration(
                            name=tool['name'],
                            description=tool['description'],
                            parameters=genai.protos.Schema(
                                type_=genai.protos.Type.OBJECT,
                                properties=properties,
                                required=tool['parameters'].get('required', [])
                            )
                        )
                    else:
                        # Formato simple: parameters es un dict de parámetros directos
                        properties = {}
                        required = []
                        
                        for param_name, param_def in tool['parameters'].items():
                            if isinstance(param_def, dict):
                                param_type = param_def.get('type', 'string').upper()
                                simple_prop = {'type_': param_type}
                                
                                if 'description' in param_def:
                                    simple_prop['description'] = param_def['description']
                                
                                if param_def.get('required', False):
                                    required.append(param_name)
                                    
                                properties[param_name] = genai.protos.Schema(**simple_prop)
                        
                        function_declaration = genai.protos.FunctionDeclaration(
                            name=tool['name'],
                            description=tool['description'],
                            parameters=genai.protos.Schema(
                                type_=genai.protos.Type.OBJECT,
                                properties=properties,
                                required=required
                            )
                        )
                else:
                    # Herramienta sin parámetros
                    function_declaration = genai.protos.FunctionDeclaration(
                        name=tool['name'],
                        description=tool['description'],
                        parameters=genai.protos.Schema(
                            type_=genai.protos.Type.OBJECT,
                            properties={}
                        )
                    )
                
                tools_for_gemini.append(function_declaration)
                
            except Exception as tool_error:
                logger.warning(f"Error procesando herramienta {tool.get('name', 'unknown')}: {tool_error}")
                continue

        logger.info(f"Herramientas convertidas para Gemini: {len(tools_for_gemini)}")
        
        # Crear el modelo con herramientas
        model = genai.GenerativeModel('gemini-2.0-flash',tools=tools_for_gemini)

        # Recuperar o crear historial de chat
        if session_id not in chat_sessions:
            # Inicializar con system prompt usando estructura simple
            chat_sessions[session_id] = [
                {'role': 'user', 'parts': [SYSTEM_PROMPT]},
                {'role': 'model', 'parts': ['¡Entendido! Estoy listo para ayudarte con AWS. Puedo ejecutar acciones reales usando las herramientas disponibles. ¿Qué necesitas?']}
            ]
        
        # IMPORTANTE: Limitar historial a últimos 10 mensajes (5 pares pregunta-respuesta)
        # Con 252 herramientas, el historial largo sobrecarga a Gemini
        MAX_HISTORY_MESSAGES = 10
        history = chat_sessions[session_id]
        if len(history) > MAX_HISTORY_MESSAGES:
            # Mantener siempre el system prompt (primeros 2 mensajes) + últimos mensajes
            history = history[:2] + history[-(MAX_HISTORY_MESSAGES-2):]
            chat_sessions[session_id] = history
        
        # Convertir historial almacenado a formato compatible con Gemini
        try:
            # Crear el chat con historial existente
            chat = model.start_chat(history=chat_sessions[session_id])
        except Exception as history_error:
            logger.error(f"Error cargando historial: {history_error}. Iniciando nuevo chat.")
            # Si hay error con el historial, iniciar uno nuevo
            chat_sessions[session_id] = [
                {'role': 'user', 'parts': [SYSTEM_PROMPT]},
                {'role': 'model', 'parts': ['¡Entendido! Estoy listo para ayudarte con AWS. Puedo ejecutar acciones reales usando las herramientas disponibles. ¿Qué necesitas?']}
            ]
            chat = model.start_chat(history=chat_sessions[session_id])

        # Enviar mensaje del usuario
        try:
            response = chat.send_message(user_message)
        except Exception as send_error:
            logger.error(f"Error al enviar mensaje a Gemini: {send_error}")
            return jsonify({
                'error': f'Error comunicando con Gemini: {str(send_error)}',
                'response': '',
                'tool_results': [],
                'status': 'error'
            }), 500
        
        # Procesar function calls si existen
        final_response = ""
        tool_results = []
        max_iterations = 5  # Prevenir loops infinitos
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Verificar si hay partes en la respuesta
            if not response.candidates or not response.candidates[0].content.parts:
                break
                
            # Procesar cada parte y recolectar TODAS las function calls
            has_function_call = False
            function_responses = []
            
            for part in response.candidates[0].content.parts:
                # Si hay texto, agregarlo
                if part.text:
                    final_response += part.text
                
                # Si hay function call, ejecutarla
                if part.function_call:
                    has_function_call = True
                    function_call = part.function_call
                    function_name = function_call.name
                    
                    # Log detallado de lo que envía Gemini
                    logger.info(f"=== FUNCTION CALL DEBUG ===")
                    logger.info(f"Function name: {function_name}")
                    logger.info(f"Raw args type: {type(function_call.args)}")
                    logger.info(f"Raw args: {function_call.args}")
                    
                    # Convertir argumentos a formato serializable para evitar problemas con RepeatedComposite
                    function_args = make_serializable(dict(function_call.args))
                    
                    logger.info(f"Converted args: {function_args}")
                    logger.info(f"=== END DEBUG ===")
                    
                    # Ejecutar la herramienta
                    result = mcp_server.execute_tool(function_name, function_args)
                    
                    # Convertir resultado a formato serializable
                    serializable_result = make_serializable(result)
                    
                    # Guardar resultado para mostrar al usuario (con args serializables)
                    tool_results.append({
                        'tool': function_name,
                        'args': function_args,
                        'result': serializable_result
                    })
                    
                    # Crear respuesta de función y agregarla a la lista
                    function_response = genai.protos.FunctionResponse(
                        name=function_name,
                        response={'result': serializable_result}
                    )
                    function_responses.append(genai.protos.Part(function_response=function_response))
            
            # Si hubo function calls, enviar TODAS las respuestas juntas
            if has_function_call and function_responses:
                response = chat.send_message(
                    genai.protos.Content(parts=function_responses)
                )
            
            # Si no hay más function calls, terminar
            if not has_function_call:
                break

        logger.info(f"Respuesta final: {final_response}")
        logger.info(f"Tool results: {len(tool_results)}")

        # Actualizar historial de sesión
        # Convertir el historial a formato serializable manteniendo la estructura para Gemini
        try:
            serializable_history = []
            for msg in chat.history:
                # Crear estructura simple para almacenar
                simple_msg = {
                    'role': str(msg.role) if hasattr(msg, 'role') else 'unknown',
                    'parts': []
                }
                
                # Extraer contenido de las partes
                if hasattr(msg, 'parts'):
                    for part in msg.parts:
                        # Solo extraer texto, ignorar function calls para el historial
                        if hasattr(part, 'text') and part.text:
                            simple_msg['parts'].append(str(part.text))
                
                # Solo agregar si tiene contenido de texto
                if simple_msg['parts']:
                    serializable_history.append(simple_msg)
            
            chat_sessions[session_id] = serializable_history
        except Exception as hist_error:
            logger.warning(f"Error serializando historial: {hist_error}. Manteniendo historial anterior.")
            # En caso de error, mantener el historial anterior sin modificar

        return jsonify({
            'response': final_response,
            'tool_results': tool_results,
            'status': 'success'
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Error processing message: {str(e)}',
            'traceback': traceback.format_exc(),
            'status': 'error'
        }), 500