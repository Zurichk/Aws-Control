"""
Rutas web para AWS EventBridge
Gestión de buses de eventos, reglas y targets
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import boto3
from app.utils.aws_client import get_aws_client

eventbridge_bp = Blueprint('eventbridge', __name__, url_prefix='/eventbridge')


@eventbridge_bp.route('/')
def index():
    """Página principal de EventBridge"""
    return render_template('Mensajeria/eventbridge/index.html')


@eventbridge_bp.route('/event-buses')
def list_event_buses():
    """Lista todos los event buses"""
    try:
        events = get_aws_client('events')

        # Obtener event buses
        response = events.list_event_buses()

        event_buses = []
        for bus in response['EventBuses']:
            bus_info = {
                'name': bus['Name'],
                'arn': bus['Arn'],
                'description': bus.get('Description', ''),
                'policy': bus.get('Policy', ''),
                'creation_time': bus.get('CreationTime', 'N/A'),
                'last_modified_time': bus.get('LastModifiedTime', 'N/A')
            }
            event_buses.append(bus_info)

        return render_template('Mensajeria/eventbridge/event_buses.html', event_buses=event_buses)

    except Exception as e:
        flash(f'Error al listar event buses: {str(e)}', 'error')
        return render_template('Mensajeria/eventbridge/event_buses.html', event_buses=[])


@eventbridge_bp.route('/create-event-bus', methods=['GET', 'POST'])
def create_event_bus():
    """Crear un nuevo event bus"""
    if request.method == 'POST':
        try:
            bus_name = request.form.get('bus_name')
            description = request.form.get('description')

            events = get_aws_client('events')

            create_params = {'Name': bus_name}
            if description:
                create_params['Description'] = description

            response = events.create_event_bus(**create_params)

            flash(f'Event bus {bus_name} creado exitosamente', 'success')
            return redirect(url_for('eventbridge.list_event_buses'))

        except Exception as e:
            flash(f'Error al crear event bus: {str(e)}', 'error')

    return render_template('Mensajeria/eventbridge/create_event_bus.html')


@eventbridge_bp.route('/rules')
def list_rules():
    """Lista todas las reglas de EventBridge"""
    try:
        events = get_aws_client('events')

        # Obtener reglas
        response = events.list_rules()

        rules = []
        for rule in response['Rules']:
            rule_info = {
                'name': rule['Name'],
                'arn': rule['Arn'],
                'event_pattern': rule.get('EventPattern', ''),
                'schedule_expression': rule.get('ScheduleExpression', ''),
                'state': rule['State'],
                'description': rule.get('Description', ''),
                'managed_by': rule.get('ManagedBy', ''),
                'role_arn': rule.get('RoleArn', ''),
                'event_bus_name': rule.get('EventBusName', 'default'),
                'created_by': rule.get('CreatedBy', ''),
                'creation_time': rule.get('CreationTime', 'N/A')
            }
            rules.append(rule_info)

        return render_template('Mensajeria/eventbridge/rules.html', rules=rules)

    except Exception as e:
        flash(f'Error al listar reglas: {str(e)}', 'error')
        return render_template('Mensajeria/eventbridge/rules.html', rules=[])


@eventbridge_bp.route('/create-rule', methods=['GET', 'POST'])
def create_rule():
    """Crear una nueva regla de EventBridge"""
    if request.method == 'POST':
        try:
            rule_name = request.form.get('rule_name')
            event_bus_name = request.form.get('event_bus_name', 'default')
            description = request.form.get('description')
            event_pattern = request.form.get('event_pattern')
            schedule_expression = request.form.get('schedule_expression')
            state = request.form.get('state', 'ENABLED')
            role_arn = request.form.get('role_arn')

            events = get_aws_client('events')

            create_params = {
                'Name': rule_name,
                'EventBusName': event_bus_name,
                'State': state
            }

            if description:
                create_params['Description'] = description

            if event_pattern:
                create_params['EventPattern'] = event_pattern

            if schedule_expression:
                create_params['ScheduleExpression'] = schedule_expression

            if role_arn:
                create_params['RoleArn'] = role_arn

            response = events.put_rule(**create_params)

            flash(f'Regla {rule_name} creada exitosamente', 'success')
            return redirect(url_for('eventbridge.list_rules'))

        except Exception as e:
            flash(f'Error al crear regla: {str(e)}', 'error')

    return render_template('Mensajeria/eventbridge/create_rule.html')


@eventbridge_bp.route('/rule/<rule_name>/targets')
def list_targets(rule_name):
    """Lista los targets de una regla específica"""
    try:
        event_bus_name = request.args.get('event_bus_name', 'default')
        events = get_aws_client('events')

        # Obtener targets de la regla
        response = events.list_targets_by_rule(
            Rule=rule_name,
            EventBusName=event_bus_name
        )

        targets = []
        for target in response['Targets']:
            target_info = {
                'id': target['Id'],
                'arn': target['Arn'],
                'role_arn': target.get('RoleArn', ''),
                'input': target.get('Input', ''),
                'input_path': target.get('InputPath', ''),
                'input_transformer': target.get('InputTransformer', {}),
                'kinesis_parameters': target.get('KinesisParameters', {}),
                'run_command_parameters': target.get('RunCommandParameters', {}),
                'ecs_parameters': target.get('EcsParameters', {}),
                'batch_parameters': target.get('BatchParameters', {}),
                'sqs_parameters': target.get('SqsParameters', {}),
                'http_parameters': target.get('HttpParameters', {}),
                'redshift_data_parameters': target.get('RedshiftDataParameters', {}),
                'sage_maker_pipeline_parameters': target.get('SageMakerPipelineParameters', {}),
                'event_bus_name': event_bus_name,
                'rule_name': rule_name
            }
            targets.append(target_info)

        return render_template('Mensajeria/eventbridge/targets.html',
                             targets=targets, rule_name=rule_name, event_bus_name=event_bus_name)

    except Exception as e:
        flash(f'Error al listar targets: {str(e)}', 'error')
        return render_template('Mensajeria/eventbridge/targets.html',
                             targets=[], rule_name=rule_name, event_bus_name=event_bus_name)


@eventbridge_bp.route('/rule/<rule_name>/add-target', methods=['GET', 'POST'])
def add_target(rule_name):
    """Agregar un target a una regla"""
    event_bus_name = request.args.get('event_bus_name', 'default')

    if request.method == 'POST':
        try:
            target_id = request.form.get('target_id')
            target_arn = request.form.get('target_arn')
            role_arn = request.form.get('role_arn')
            input_text = request.form.get('input')

            events = get_aws_client('events')

            target = {
                'Id': target_id,
                'Arn': target_arn
            }

            if role_arn:
                target['RoleArn'] = role_arn

            if input_text:
                target['Input'] = input_text

            response = events.put_targets(
                Rule=rule_name,
                EventBusName=event_bus_name,
                Targets=[target]
            )

            flash(f'Target {target_id} agregado exitosamente a la regla {rule_name}', 'success')
            return redirect(url_for('eventbridge.list_targets', rule_name=rule_name, event_bus_name=event_bus_name))

        except Exception as e:
            flash(f'Error al agregar target: {str(e)}', 'error')

    return render_template('Mensajeria/eventbridge/add_target.html',
                         rule_name=rule_name, event_bus_name=event_bus_name)


@eventbridge_bp.route('/rule/<rule_name>/remove-target/<target_id>', methods=['POST'])
def remove_target(rule_name, target_id):
    """Remover un target de una regla"""
    try:
        event_bus_name = request.form.get('event_bus_name', 'default')
        events = get_aws_client('events')

        response = events.remove_targets(
            Rule=rule_name,
            EventBusName=event_bus_name,
            Ids=[target_id]
        )

        flash(f'Target {target_id} removido exitosamente de la regla {rule_name}', 'success')

    except Exception as e:
        flash(f'Error al remover target: {str(e)}', 'error')

    return redirect(url_for('eventbridge.list_targets', rule_name=rule_name, event_bus_name=event_bus_name))


@eventbridge_bp.route('/put-events', methods=['GET', 'POST'])
def put_events():
    """Enviar eventos personalizados a EventBridge"""
    if request.method == 'POST':
        try:
            event_bus_name = request.form.get('event_bus_name', 'default')
            source = request.form.get('source')
            detail_type = request.form.get('detail_type')
            detail = request.form.get('detail')

            events = get_aws_client('events')

            event_entry = {
                'Source': source,
                'DetailType': detail_type,
                'Detail': detail,
                'EventBusName': event_bus_name
            }

            response = events.put_events(Entries=[event_entry])

            if response.get('FailedEntryCount', 0) == 0:
                flash('Evento enviado exitosamente', 'success')
            else:
                flash(f'Error al enviar evento: {response.get("Entries", [{}])[0].get("ErrorMessage", "Error desconocido")}', 'error')

            return redirect(url_for('eventbridge.put_events'))

        except Exception as e:
            flash(f'Error al enviar evento: {str(e)}', 'error')

    return render_template('Mensajeria/eventbridge/put_events.html')