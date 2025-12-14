"""
Rutas web para AWS Systems Manager
Gestión de parámetros, comandos y sesiones
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
from app.utils.aws_client import get_aws_client

systems_manager_bp = Blueprint('systems_manager', __name__, url_prefix='/systems-manager')


@systems_manager_bp.route('/')
def index():
    """Página principal de Systems Manager"""
    return render_template('Gestion/systems_manager/index.html')


@systems_manager_bp.route('/parameters')
def parameters():
    """Lista todos los parámetros de Parameter Store"""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.describe_parameters()

        parameters = []
        for param in response['Parameters']:
            param_info = {
                'name': param['Name'],
                'type': param['Type'],
                'key_id': param.get('KeyId', 'N/A'),
                'last_modified_date': param.get('LastModifiedDate', '').strftime('%Y-%m-%d %H:%M:%S') if param.get('LastModifiedDate') else 'N/A',
                'version': param.get('Version', 'N/A'),
                'tier': param.get('Tier', 'Standard'),
                'policies': param.get('Policies', [])
            }
            parameters.append(param_info)

        return render_template('Gestion/systems_manager/parameters.html', parameters=parameters)
    except Exception as e:
        flash(f'Error obteniendo parámetros: {str(e)}', 'error')
        return render_template('Gestion/systems_manager/parameters.html', parameters=[])


@systems_manager_bp.route('/create-parameter', methods=['GET', 'POST'])
def create_parameter():
    """Crea un nuevo parámetro en Parameter Store"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            value = request.form.get('value')
            param_type = request.form.get('type', 'String')
            description = request.form.get('description')
            tier = request.form.get('tier', 'Standard')
            key_id = request.form.get('key_id')

            if not name or not value:
                flash('Nombre y valor son requeridos', 'error')
                return redirect(request.url)

            ssm = get_aws_client('ssm')

            params = {
                'Name': name,
                'Value': value,
                'Type': param_type,
                'Tier': tier
            }

            if description:
                params['Description'] = description

            if key_id and param_type == 'SecureString':
                params['KeyId'] = key_id

            response = ssm.put_parameter(**params)

            flash(f'Parámetro {name} creado exitosamente (versión {response.get("Version", "N/A")})', 'success')
            return redirect(url_for('systems_manager.parameters'))

        except Exception as e:
            flash(f'Error creando parámetro: {str(e)}', 'error')
            return redirect(request.url)

    # GET request
    return render_template('Gestion/systems_manager/create_parameter.html')


@systems_manager_bp.route('/parameter/<path:param_name>')
def get_parameter(param_name):
    """Obtiene el valor de un parámetro específico"""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)

        parameter = {
            'name': response['Parameter']['Name'],
            'value': response['Parameter']['Value'],
            'type': response['Parameter']['Type'],
            'version': response['Parameter']['Version'],
            'last_modified_date': response['Parameter'].get('LastModifiedDate', '').strftime('%Y-%m-%d %H:%M:%S') if response['Parameter'].get('LastModifiedDate') else 'N/A',
            'tier': response['Parameter'].get('Tier', 'Standard')
        }

        return render_template('Gestion/systems_manager/parameter_detail.html', parameter=parameter)
    except Exception as e:
        flash(f'Error obteniendo parámetro: {str(e)}', 'error')
        return redirect(url_for('systems_manager.parameters'))


@systems_manager_bp.route('/commands')
def commands():
    """Lista comandos ejecutados"""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.list_commands()

        commands = []
        for cmd in response['Commands']:
            cmd_info = {
                'command_id': cmd['CommandId'],
                'document_name': cmd['DocumentName'],
                'status': cmd['Status'],
                'status_details': cmd.get('StatusDetails', ''),
                'requested_date_time': cmd.get('RequestedDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if cmd.get('RequestedDateTime') else 'N/A',
                'completed_date_time': cmd.get('CompletedDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if cmd.get('CompletedDateTime') else 'N/A',
                'target_count': cmd.get('TargetCount', 0),
                'error_count': cmd.get('ErrorCount', 0),
                'delivery_timed_out_count': cmd.get('DeliveryTimedOutCount', 0)
            }
            commands.append(cmd_info)

        return render_template('Gestion/systems_manager/commands.html', commands=commands)
    except Exception as e:
        flash(f'Error obteniendo comandos: {str(e)}', 'error')
        return render_template('Gestion/systems_manager/commands.html', commands=[])


@systems_manager_bp.route('/run-command', methods=['GET', 'POST'])
def run_command():
    """Ejecuta un comando en instancias EC2"""
    if request.method == 'POST':
        try:
            document_name = request.form.get('document_name', 'AWS-RunShellScript')
            targets = request.form.getlist('targets[]')
            commands = request.form.getlist('commands[]')
            timeout_seconds = int(request.form.get('timeout_seconds', 3600))

            if not targets or not commands:
                flash('Targets y comandos son requeridos', 'error')
                return redirect(request.url)

            ssm = get_aws_client('ssm')

            # Preparar targets
            targets_list = []
            for target in targets:
                if target.startswith('tag:'):
                    # Target por tag
                    key, value = target[4:].split(':', 1)
                    targets_list.append({
                        'Key': f'tag:{key}',
                        'Values': [value]
                    })
                else:
                    # Target por instance ID
                    targets_list.append({
                        'Key': 'instanceids',
                        'Values': [target]
                    })

            # Ejecutar comando
            response = ssm.send_command(
                DocumentName=document_name,
                Targets=targets_list,
                Parameters={'commands': commands},
                TimeoutSeconds=timeout_seconds
            )

            flash(f'Comando enviado exitosamente. Command ID: {response["Command"]["CommandId"]}', 'success')
            return redirect(url_for('systems_manager.commands'))

        except Exception as e:
            flash(f'Error ejecutando comando: {str(e)}', 'error')
            return redirect(request.url)

    # GET request
    try:
        ec2 = get_aws_client('ec2')
        instances = ec2.describe_instances()
        instance_list = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    instance_list.append({
                        'id': instance['InstanceId'],
                        'name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                        'state': instance['State']['Name']
                    })

        return render_template('Gestion/systems_manager/run_command.html', instances=instance_list)
    except Exception as e:
        flash(f'Error obteniendo instancias: {str(e)}', 'error')
        return render_template('Gestion/systems_manager/run_command.html', instances=[])


@systems_manager_bp.route('/sessions')
def sessions():
    """Lista sesiones activas"""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.describe_sessions(State='Active')

        sessions = []
        for session in response['Sessions']:
            session_info = {
                'session_id': session['SessionId'],
                'target': session['Target'],
                'status': session['Status'],
                'start_date': session.get('StartDate', '').strftime('%Y-%m-%d %H:%M:%S') if session.get('StartDate') else 'N/A',
                'end_date': session.get('EndDate', '').strftime('%Y-%m-%d %H:%M:%S') if session.get('EndDate') else 'N/A',
                'document_name': session.get('DocumentName', 'N/A'),
                'owner': session.get('Owner', 'N/A')
            }
            sessions.append(session_info)

        return render_template('Gestion/systems_manager/sessions.html', sessions=sessions)
    except Exception as e:
        flash(f'Error obteniendo sesiones: {str(e)}', 'error')
        return render_template('Gestion/systems_manager/sessions.html', sessions=[])


@systems_manager_bp.route('/start-session', methods=['GET', 'POST'])
def start_session():
    """Inicia una nueva sesión en una instancia"""
    if request.method == 'POST':
        try:
            target = request.form.get('target')
            document_name = request.form.get('document_name', 'SSM-SessionManagerRunShell')

            if not target:
                flash('Target es requerido', 'error')
                return redirect(request.url)

            ssm = get_aws_client('ssm')

            params = {
                'Target': target,
                'DocumentName': document_name
            }

            response = ssm.start_session(**params)

            flash(f'Sesión iniciada exitosamente. Session ID: {response["SessionId"]}', 'success')
            return redirect(url_for('systems_manager.sessions'))

        except Exception as e:
            flash(f'Error iniciando sesión: {str(e)}', 'error')
            return redirect(request.url)

    # GET request
    try:
        ec2 = get_aws_client('ec2')
        instances = ec2.describe_instances()
        instance_list = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    instance_list.append({
                        'id': instance['InstanceId'],
                        'name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                        'state': instance['State']['Name']
                    })

        return render_template('Gestion/systems_manager/start_session.html', instances=instance_list)
    except Exception as e:
        flash(f'Error obteniendo instancias: {str(e)}', 'error')
        return render_template('Gestion/systems_manager/start_session.html', instances=[])


@systems_manager_bp.route('/command/<command_id>')
def command_detail(command_id):
    """Obtiene detalles de un comando específico"""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.list_command_invocations(CommandId=command_id)

        if not response['CommandInvocations']:
            flash('Comando no encontrado', 'error')
            return redirect(url_for('systems_manager.commands'))

        invocation = response['CommandInvocations'][0]

        command_detail = {
            'command_id': invocation['CommandId'],
            'instance_id': invocation['InstanceId'],
            'document_name': invocation['DocumentName'],
            'status': invocation['Status'],
            'status_details': invocation.get('StatusDetails', ''),
            'response_code': invocation.get('ResponseCode', 'N/A'),
            'execution_start_date_time': invocation.get('ExecutionStartDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if invocation.get('ExecutionStartDateTime') else 'N/A',
            'execution_end_date_time': invocation.get('ExecutionEndDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if invocation.get('ExecutionEndDateTime') else 'N/A',
            'standard_output_content': invocation.get('StandardOutputContent', ''),
            'standard_error_content': invocation.get('StandardErrorContent', '')
        }

        return render_template('Gestion/systems_manager/command_detail.html', command=command_detail)
    except Exception as e:
        flash(f'Error obteniendo detalles del comando: {str(e)}', 'error')
        return redirect(url_for('systems_manager.commands'))