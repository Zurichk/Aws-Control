from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('lambda_bp', __name__)

@bp.route('/')
def index():
    return render_template('Computo/lambda_service/index.html')

@bp.route('/functions')
def functions():
    try:
        lambda_client = get_aws_client('lambda')
        functions = lambda_client.list_functions()
        function_list = []
        for function in functions['Functions']:
            function_list.append({
                'name': function['FunctionName'],
                'arn': function['FunctionArn'],
                'runtime': function['Runtime'],
                'last_modified': function['LastModified']
            })
        return render_template('Computo/lambda_service/functions.html', functions=function_list)
    except Exception as e:
        flash(f'Error obteniendo funciones Lambda: {str(e)}', 'error')
        return render_template('Computo/lambda_service/functions.html', functions=[])

@bp.route('/create-function', methods=['GET', 'POST'])
def create_function():
    """Crear una nueva función Lambda"""
    if request.method == 'POST':
        try:
            function_name = request.form.get('function_name')
            runtime = request.form.get('runtime')
            role_arn = request.form.get('role_arn')
            handler = request.form.get('handler')
            code_zip = request.files.get('code_zip')
            description = request.form.get('description', '')
            timeout = int(request.form.get('timeout', 30))
            memory_size = int(request.form.get('memory_size', 128))

            lambda_client = get_aws_client('lambda')

            # Preparar el código
            if code_zip:
                code = {'ZipFile': code_zip.read()}
            else:
                # Código inline simple para testing
                code = {'ZipFile': b'dummy code'}

            lambda_client.create_function(
                FunctionName=function_name,
                Runtime=runtime,
                Role=role_arn,
                Handler=handler,
                Code=code,
                Description=description,
                Timeout=timeout,
                MemorySize=memory_size
            )

            flash(f'Función Lambda "{function_name}" creada exitosamente', 'success')
            return redirect(url_for('lambda_bp.functions'))

        except Exception as e:
            flash(f'Error creando función Lambda: {str(e)}', 'error')

    # GET: Mostrar formulario
    return render_template('Computo/lambda_service/create_function.html')

@bp.route('/delete-function/<function_name>', methods=['POST'])
def delete_function(function_name):
    """Eliminar una función Lambda"""
    try:
        lambda_client = get_aws_client('lambda')
        lambda_client.delete_function(FunctionName=function_name)
        flash(f'Función Lambda "{function_name}" eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando función Lambda: {str(e)}', 'error')
    return redirect(url_for('lambda_bp.functions'))

@bp.route('/update-code/<function_name>', methods=['GET', 'POST'])
def update_code(function_name):
    """Actualizar el código de una función Lambda"""
    if request.method == 'POST':
        try:
            code_zip = request.files.get('code_zip')
            lambda_client = get_aws_client('lambda')

            if code_zip:
                code = {'ZipFile': code_zip.read()}
                lambda_client.update_function_code(
                    FunctionName=function_name,
                    ZipFile=code['ZipFile']
                )
                flash(f'Código de función "{function_name}" actualizado exitosamente', 'success')
            else:
                flash('Debe proporcionar un archivo ZIP con el código', 'error')

        except Exception as e:
            flash(f'Error actualizando código: {str(e)}', 'error')

    return render_template('Computo/lambda_service/update_code.html', function_name=function_name)

@bp.route('/invoke/<function_name>', methods=['GET', 'POST'])
def invoke_function(function_name):
    """Invocar una función Lambda"""
    result = None
    if request.method == 'POST':
        try:
            payload = request.form.get('payload', '{}')
            lambda_client = get_aws_client('lambda')

            response = lambda_client.invoke(
                FunctionName=function_name,
                Payload=payload
            )

            result = {
                'status_code': response['StatusCode'],
                'payload': response['Payload'].read().decode('utf-8'),
                'executed_version': response.get('ExecutedVersion', 'N/A')
            }

            if 'FunctionError' in response:
                result['error'] = response['FunctionError']

        except Exception as e:
            result = {'error': str(e)}

    return render_template('Computo/lambda_service/invoke_function.html',
                         function_name=function_name, result=result)

@bp.route('/layers')
def layers():
    """Listar layers de Lambda"""
    try:
        lambda_client = get_aws_client('lambda')
        response = lambda_client.list_layers()
        layers_list = response.get('Layers', [])
        return render_template('Computo/lambda_service/layers.html', layers=layers_list)
    except Exception as e:
        flash(f'Error obteniendo layers: {str(e)}', 'error')
        return render_template('Computo/lambda_service/layers.html', layers=[])

@bp.route('/create-layer', methods=['GET', 'POST'])
def create_layer():
    """Crear un nuevo layer de Lambda"""
    if request.method == 'POST':
        try:
            layer_name = request.form.get('layer_name')
            description = request.form.get('description', '')
            compatible_runtimes = request.form.getlist('compatible_runtimes')
            layer_zip = request.files.get('layer_zip')

            lambda_client = get_aws_client('lambda')

            if layer_zip:
                content = {'ZipFile': layer_zip.read()}
                lambda_client.publish_layer_version(
                    LayerName=layer_name,
                    Content=content,
                    CompatibleRuntimes=compatible_runtimes,
                    Description=description
                )
                flash(f'Layer "{layer_name}" creado exitosamente', 'success')
                return redirect(url_for('lambda_bp.layers'))
            else:
                flash('Debe proporcionar un archivo ZIP para el layer', 'error')

        except Exception as e:
            flash(f'Error creando layer: {str(e)}', 'error')

    return render_template('Computo/lambda_service/create_layer.html')

@bp.route('/function-versions/<function_name>')
def function_versions(function_name):
    """Listar versiones de una función Lambda"""
    try:
        lambda_client = get_aws_client('lambda')
        response = lambda_client.list_versions_by_function(FunctionName=function_name)
        versions = response.get('Versions', [])
        return render_template('Computo/lambda_service/function_versions.html',
                             function_name=function_name, versions=versions)
    except Exception as e:
        flash(f'Error obteniendo versiones: {str(e)}', 'error')
        return render_template('Computo/lambda_service/function_versions.html',
                             function_name=function_name, versions=[])

@bp.route('/create-alias/<function_name>', methods=['GET', 'POST'])
def create_alias(function_name):
    """Crear un alias para una función Lambda"""
    if request.method == 'POST':
        try:
            alias_name = request.form.get('alias_name')
            function_version = request.form.get('function_version')
            description = request.form.get('description', '')

            lambda_client = get_aws_client('lambda')
            response = lambda_client.create_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=function_version,
                Description=description
            )

            flash(f'Alias "{alias_name}" creado exitosamente', 'success')
            return redirect(url_for('lambda_bp.function_versions', function_name=function_name))

        except Exception as e:
            flash(f'Error creando alias: {str(e)}', 'error')

    # Obtener versiones disponibles
    try:
        lambda_client = get_aws_client('lambda')
        response = lambda_client.list_versions_by_function(FunctionName=function_name)
        versions = response.get('Versions', [])
    except Exception:
        versions = []

    return render_template('Computo/lambda_service/create_alias.html',
                         function_name=function_name, versions=versions)

@bp.route('/update-configuration/<function_name>', methods=['GET', 'POST'])
def update_configuration(function_name):
    """Actualizar configuración de una función Lambda"""
    if request.method == 'POST':
        try:
            description = request.form.get('description')
            timeout = request.form.get('timeout')
            memory_size = request.form.get('memory_size')
            environment_variables = request.form.get('environment_variables')

            lambda_client = get_aws_client('lambda')

            update_params = {}
            if description is not None:
                update_params['Description'] = description
            if timeout:
                update_params['Timeout'] = int(timeout)
            if memory_size:
                update_params['MemorySize'] = int(memory_size)
            if environment_variables:
                # Parsear variables de entorno (formato: KEY1=VALUE1,KEY2=VALUE2)
                env_dict = {}
                for pair in environment_variables.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        env_dict[key.strip()] = value.strip()
                update_params['Environment'] = {'Variables': env_dict}

            if update_params:
                response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    **update_params
                )
                flash(f'Configuración de "{function_name}" actualizada exitosamente', 'success')
                return redirect(url_for('lambda_bp.functions'))
            else:
                flash('No se proporcionaron cambios para actualizar', 'warning')

        except Exception as e:
            flash(f'Error actualizando configuración: {str(e)}', 'error')

    # Obtener configuración actual
    try:
        lambda_client = get_aws_client('lambda')
        response = lambda_client.get_function(FunctionName=function_name)
        function_config = response['Configuration']
    except Exception:
        function_config = {}

    return render_template('Computo/lambda_service/update_configuration.html',
                         function_name=function_name, function=function_config)