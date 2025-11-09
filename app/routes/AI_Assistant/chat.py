import os
import json
import uuid
import logging
import google.generativeai as genai
from flask import Blueprint, render_template, request, jsonify, session
from app.utils.aws_client import get_aws_client
from app.mcp_server import get_mcp_server

bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# Almacenar historiales de chat en memoria (para producción usar Redis o base de datos)
chat_sessions = {}

# System prompt with AWS services information
SYSTEM_PROMPT = """
Eres un asistente experto en AWS que ayuda a los usuarios a aprender y usar servicios de AWS a través de un panel de control web.

INFORMACIÓN DE SERVICIOS DISPONIBLES EN EL PANEL:

SERVICIOS DE COMPUTO:
- EC2: Instancias de servidor virtual en la nube
- Lambda: Computación serverless, ejecuta código sin servidores
- ECS: Servicio de contenedores elásticos para Docker

SERVICIOS DE ALMACENAMIENTO:
- S3: Almacenamiento de objetos escalable y duradero

SERVICIOS DE BASE DE DATOS:
- RDS: Bases de datos relacionales administradas (MySQL, PostgreSQL, etc.)
- DynamoDB: Base de datos NoSQL completamente administrada

SERVICIOS DE MENSAJERÍA:
- SNS: Servicio de notificaciones simples (pub/sub)
- SQS: Servicio de colas de mensajes

SERVICIOS DE REDES:
- VPC: Redes virtuales privadas
- Route 53: Servicio de DNS
- ELB: Load Balancers para distribución de tráfico
- CloudFront: CDN para distribución de contenido
- API Gateway: Creación y gestión de APIs REST/HTTP/WebSocket

SERVICIOS DE SEGURIDAD:
- IAM: Gestión de identidades y accesos
- KMS: Servicio de administración de claves de encriptación

SERVICIOS DE ANALYTICS:
- Kinesis: Procesamiento de datos en streaming en tiempo real

SERVICIOS DE CONTENEDORES:
- ECS: Orquestación de contenedores Docker

SERVICIOS DE MACHINE LEARNING:
- SageMaker: Plataforma completa para ML (notebooks, training, deployment)

SERVICIOS DE GESTIÓN:
- CloudFormation: Infraestructura como código
- CloudWatch: Monitoreo y logging

ESTRUCTURA DEL PANEL WEB:
- Navegación organizada por categorías (Computo, Almacenamiento, Base de Datos, etc.)
- Cada servicio tiene su propia página con:
  * Descripción detallada del servicio
  * Lista de recursos actuales
  * Botones para crear nuevos recursos
  * Información educativa sobre el servicio

TU FUNCIÓN:
1. Guiar a los usuarios paso a paso para completar tareas específicas
2. Explicar conceptos de AWS de manera clara y educativa
3. Recomendar qué servicios usar para diferentes casos de uso
4. Ayudar a entender la interfaz del panel web
5. Dar consejos sobre mejores prácticas de AWS
6. Responder preguntas sobre arquitectura y diseño de soluciones
7. **PUEDES EJECUTAR ACCIONES REALES EN AWS** usando las herramientas disponibles

HERRAMIENTAS DISPONIBLES:

BÚSQUEDA Y CONSULTA (11):
- search_amis: Buscar AMIs disponibles con filtros
- list_ec2_instances: Listar instancias EC2
- list_vpcs: Listar VPCs
- describe_vpc: Detalles completos de una VPC
- list_s3_buckets: Listar buckets S3
- list_security_groups: Listar security groups
- list_subnets: Listar subnets
- list_load_balancers: Listar ALB/NLB
- list_target_groups: Listar target groups
- list_autoscaling_groups: Listar ASG
- list_rds_instances: Listar instancias RDS
- list_dynamodb_tables: Listar tablas DynamoDB

CREACIÓN DE RECURSOS (9):
- create_ec2_instance: Crear instancias EC2
- create_secure_vpc: Crear VPCs seguras
- create_security_group: Crear security groups
- create_s3_bucket: Crear buckets S3
- create_ami_from_instance: Crear AMI desde una instancia
- create_target_group: Crear target group para ELB
- create_launch_template: Crear Launch Template
- create_autoscaling_group: Crear Auto Scaling Group

GESTIÓN DE INSTANCIAS (4):
- stop_ec2_instance: Detener instancias
- start_ec2_instance: Iniciar instancias detenidas
- modify_instance_security_groups: Modificar security groups de una instancia
- terminate_ec2_instance: Terminar instancias

COSTOS (1):
- get_aws_costs: Consultar costos

FLUJO COMPLETO PARA AUTO SCALING:
1. Usar search_amis para encontrar o create_ami_from_instance para crear AMI personalizada
2. Crear Launch Template con create_launch_template
3. Crear Target Group con create_target_group (si se usa con load balancer)
4. Crear Auto Scaling Group con create_autoscaling_group
5. Opcionalmente listar con list_autoscaling_groups para verificar

FLUJO PARA LOAD BALANCING:
1. Crear Target Group con create_target_group
2. Los load balancers se pueden listar con list_load_balancers
3. Los target groups se listan con list_target_groups

GESTIÓN DE SECURITY GROUPS EN INSTANCIAS:
- Si el usuario pide "asignar un security group a una instancia", usa modify_instance_security_groups
- Esta herramienta REEMPLAZA todos los security groups actuales con los nuevos
- No requiere detener la instancia, funciona con instancias running o stopped
- Después de modificar, la instancia mantiene su estado (running/stopped)
- Ejemplo: modify_instance_security_groups(instance_id="i-xxx", security_group_ids=["sg-xxx", "sg-yyy"])

CONTROL DE ESTADO DE INSTANCIAS:
- start_ec2_instance: Inicia una instancia que está stopped
- stop_ec2_instance: Detiene una instancia que está running
- terminate_ec2_instance: Elimina permanentemente una instancia

IMPORTANTE SOBRE AMIs:
- Antes de crear una instancia EC2, puedes buscar AMIs disponibles usando search_amis
- Si el usuario pide "Ubuntu", "Amazon Linux", "Windows Server", etc., BUSCA la AMI primero
- Si el usuario no especifica AMI, usa búsqueda para encontrar la más apropiada
- Las AMIs tienen formato ami-XXXXXXXX
- Las AMIs de Amazon (owner=amazon) son las más comunes y confiables
- Para Linux usa platform=linux, para Windows usa platform=windows

INSTRUCCIONES DE RESPUESTA:
- Sé educativo pero conciso
- Usa ejemplos prácticos cuando sea posible
- **IMPORTANTE: Si el usuario pide crear/modificar/listar recursos, EJECUTA LA HERRAMIENTA INMEDIATAMENTE sin anunciar que lo vas a hacer**
- Primero ejecuta, luego explica qué se creó
- Si mencionan servicios específicos, explica cómo usarlos en el panel
- Mantén un tono amigable y profesional
- Si no sabes algo específico, admítelo y sugiere alternativas

EJEMPLO DE USO CORRECTO:
Usuario: "Créame un bucket S3 llamado mi-bucket"
Tú: [EJECUTAS create_s3_bucket inmediatamente]
Tú: "✅ He creado el bucket S3 'mi-bucket' en us-east-1 con:
- Versionado habilitado
- Encriptación AES256
- Acceso público bloqueado"

EJEMPLO INCORRECTO (NO HAGAS ESTO):
Usuario: "Créame un bucket S3"
Tú: "¡Claro! Voy a crear un bucket S3..." ❌ NO ANUNCIES, EJECUTA DIRECTAMENTE
[Usas la herramienta create_ec2_instance]
Tú: "✅ He creado exitosamente: [detalles de la instancia]"

Usuario: "Asigna el security group sg-xxx a la instancia i-yyy"
Tú: "¡Perfecto! Voy a asignar ese security group a la instancia..."
[Usas modify_instance_security_groups]
Tú: "✅ Security group asignado. La instancia mantiene su estado actual."

Recuerda: Tu objetivo es ayudar a los usuarios a aprender AWS mientras usan este panel de control educativo, Y PUEDES EJECUTAR ACCIONES REALES.
"""

def make_serializable(obj):
    """Convierte objetos no serializables a tipos primitivos"""
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Para cualquier otro tipo (datetime, etc.), convertir a string
        return str(obj)

@bp.route('/')
def index():
    # Generar o recuperar session_id
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    return render_template('AI_Assistant/chat/index.html', session_id=session['chat_session_id'])

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
        tools_definition = mcp_server.get_tools()
        
        # Convertir herramientas a formato simple para Gemini
        tools_for_gemini = []
        for tool in tools_definition:
            # Simplificar el schema - usar solo tipos básicos
            properties = {}
            for prop_name, prop_def in tool['parameters']['properties'].items():
                prop_type = prop_def.get('type', 'string').upper()
                
                # Convertir a formato simple
                simple_prop = {'type_': prop_type}
                
                if 'description' in prop_def:
                    simple_prop['description'] = prop_def['description']
                    
                # Manejar enums
                if 'enum' in prop_def:
                    simple_prop['enum'] = prop_def['enum']
                
                # Manejar arrays - necesitan definir el tipo de items
                if prop_type == 'ARRAY':
                    if 'items' in prop_def:
                        items_type = prop_def['items'].get('type', 'string').upper()
                        simple_prop['items'] = genai.protos.Schema(type_=items_type)
                    else:
                        # Si no hay items definidos, asumir string
                        simple_prop['items'] = genai.protos.Schema(type_='STRING')
                
                # Manejar objetos
                if prop_type == 'OBJECT':
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
            tools_for_gemini.append(function_declaration)

        # Crear el modelo con herramientas
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=tools_for_gemini
        )

        # Recuperar o crear historial de chat
        if session_id not in chat_sessions:
            # Inicializar con system prompt
            chat_sessions[session_id] = [
                {'role': 'user', 'parts': [SYSTEM_PROMPT]},
                {'role': 'model', 'parts': ['¡Entendido! Estoy listo para ayudarte con AWS. Puedo ejecutar acciones reales usando las herramientas disponibles. ¿Qué necesitas?']}
            ]
        
        # Crear el chat con historial existente
        chat = model.start_chat(history=chat_sessions[session_id])

        # Enviar mensaje del usuario
        response = chat.send_message(user_message)
        
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
                
            # Procesar cada parte
            has_function_call = False
            for part in response.candidates[0].content.parts:
                # Si hay texto, agregarlo
                if part.text:
                    final_response += part.text
                
                # Si hay function call, ejecutarla
                if part.function_call:
                    has_function_call = True
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    # Ejecutar la herramienta
                    result = mcp_server.execute_tool(function_name, function_args)
                    
                    # Convertir resultado a formato serializable
                    serializable_result = make_serializable(result)
                    
                    # Guardar resultado para mostrar al usuario
                    tool_results.append({
                        'tool': function_name,
                        'args': function_args,
                        'result': serializable_result
                    })
                    
                    # Crear respuesta de función
                    function_response = genai.protos.FunctionResponse(
                        name=function_name,
                        response={'result': serializable_result}
                    )
                    
                    # Enviar resultado al modelo
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(function_response=function_response)]
                        )
                    )
                    break  # Procesar una función a la vez
            
            # Si no hay más function calls, terminar
            if not has_function_call:
                break

        # Actualizar historial de sesión
        # Convertir el historial a formato serializable para evitar errores con RepeatedComposite
        try:
            serializable_history = []
            for msg in chat.history:
                # Crear mensaje serializable
                msg_dict = {
                    'role': str(msg.role) if hasattr(msg, 'role') else 'user',
                    'parts': []
                }
                
                # Extraer solo texto de las partes
                for part in msg.parts:
                    if hasattr(part, 'text') and part.text:
                        msg_dict['parts'].append(str(part.text))
                
                # Solo agregar si tiene contenido
                if msg_dict['parts']:
                    serializable_history.append(msg_dict)
            
            chat_sessions[session_id] = serializable_history
        except Exception as hist_error:
            logger.warning(f"Error serializando historial: {hist_error}. Manteniendo historial anterior.")
            # En caso de error, no actualizar el historial

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