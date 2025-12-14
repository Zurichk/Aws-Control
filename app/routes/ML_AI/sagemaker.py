from flask import Blueprint, render_template, request, flash
from app.utils.aws_client import get_aws_client

bp = Blueprint('sagemaker', __name__)

@bp.route('/')
def index():
    try:
        sagemaker = get_aws_client('sagemaker')
        response = sagemaker.list_notebook_instances()
        notebooks = []
        for nb in response['NotebookInstances']:
            notebooks.append({
                'name': nb['NotebookInstanceName'],
                'status': nb['NotebookInstanceStatus'],
                'type': nb['InstanceType'],
                'lifecycle_config': nb.get('DefaultCodeRepository', 'N/A'),
                'created': nb.get('CreationTime', '').strftime('%Y-%m-%d %H:%M:%S') if nb.get('CreationTime') else 'N/A'
            })
        return render_template('ML_AI/index.html', notebooks=notebooks)
    except Exception as e:
        flash(f'Error obteniendo notebooks de SageMaker: {str(e)}', 'error')
        return render_template('ML_AI/index.html', notebooks=[])

@bp.route('/notebooks')
def notebooks():
    try:
        sagemaker = get_aws_client('sagemaker')
        notebooks = sagemaker.list_notebook_instances()
        notebook_list = []
        for nb in notebooks['NotebookInstances']:
            notebook_list.append({
                'name': nb['NotebookInstanceName'],
                'status': nb['NotebookInstanceStatus'],
                'type': nb['InstanceType'],
                'lifecycle_config': nb.get('DefaultCodeRepository', 'N/A'),
                'created': nb.get('CreationTime', '').strftime('%Y-%m-%d %H:%M:%S') if nb.get('CreationTime') else 'N/A'
            })
        return render_template('ML_AI/sagemaker/notebooks.html', notebooks=notebook_list)
    except Exception as e:
        flash(f'Error obteniendo notebooks de SageMaker: {str(e)}', 'error')
        return render_template('ML_AI/sagemaker/notebooks.html', notebooks=[])

@bp.route('/endpoints')
def endpoints():
    """Lista todos los endpoints de SageMaker"""
    try:
        sagemaker = get_aws_client('sagemaker')
        response = sagemaker.list_endpoints()
        
        endpoints = []
        for endpoint in response['Endpoints']:
            endpoints.append({
                'name': endpoint['EndpointName'],
                'arn': endpoint['EndpointArn'],
                'status': endpoint['EndpointStatus'],
                'config_name': endpoint.get('EndpointConfigName', 'N/A'),
                'creation_time': endpoint.get('CreationTime', '').strftime('%Y-%m-%d %H:%M:%S') if endpoint.get('CreationTime') else 'N/A',
                'last_modified_time': endpoint.get('LastModifiedTime', '').strftime('%Y-%m-%d %H:%M:%S') if endpoint.get('LastModifiedTime') else 'N/A'
            })
        
        return render_template('ML_AI/sagemaker/endpoints.html', endpoints=endpoints)
    except Exception as e:
        flash(f'Error obteniendo endpoints de SageMaker: {str(e)}', 'error')
        return render_template('ML_AI/sagemaker/endpoints.html', endpoints=[])

@bp.route('/create-endpoint', methods=['GET', 'POST'])
def create_endpoint():
    """Crea un nuevo endpoint de SageMaker"""
    if request.method == 'POST':
        try:
            endpoint_name = request.form.get('endpoint_name')
            config_name = request.form.get('config_name')
            
            if not endpoint_name or not config_name:
                flash('Nombre del endpoint y configuración son requeridos', 'error')
                return redirect(request.url)
            
            sagemaker = get_aws_client('sagemaker')
            
            # Crear el endpoint
            response = sagemaker.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=config_name
            )
            
            flash(f'Endpoint {endpoint_name} creado exitosamente', 'success')
            return redirect(url_for('sagemaker.endpoints'))
            
        except Exception as e:
            flash(f'Error creando endpoint: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - mostrar formulario
    try:
        sagemaker = get_aws_client('sagemaker')
        configs = sagemaker.list_endpoint_configs()['EndpointConfigs']
        config_names = [config['EndpointConfigName'] for config in configs]
        return render_template('ML_AI/sagemaker/create_endpoint.html', config_names=config_names)
    except Exception as e:
        flash(f'Error obteniendo configuraciones: {str(e)}', 'error')
        return render_template('ML_AI/sagemaker/create_endpoint.html', config_names=[])

@bp.route('/invoke-endpoint', methods=['GET', 'POST'])
def invoke_endpoint():
    """Invoca un endpoint de SageMaker"""
    if request.method == 'POST':
        try:
            endpoint_name = request.form.get('endpoint_name')
            input_data = request.form.get('input_data')
            content_type = request.form.get('content_type', 'application/json')
            
            if not endpoint_name or not input_data:
                flash('Nombre del endpoint y datos de entrada son requeridos', 'error')
                return redirect(request.url)
            
            sagemaker_runtime = get_aws_client('sagemaker-runtime')
            
            # Invocar el endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType=content_type,
                Body=input_data
            )
            
            # Leer la respuesta
            result = response['Body'].read().decode('utf-8')
            
            return render_template('ML_AI/sagemaker/invoke_result.html', 
                                 endpoint_name=endpoint_name, 
                                 result=result,
                                 input_data=input_data)
            
        except Exception as e:
            flash(f'Error invocando endpoint: {str(e)}', 'error')
            return redirect(request.url)
    
    # GET request - mostrar formulario
    try:
        sagemaker = get_aws_client('sagemaker')
        endpoints = sagemaker.list_endpoints()['Endpoints']
        endpoint_names = [endpoint['EndpointName'] for endpoint in endpoints if endpoint['EndpointStatus'] == 'InService']
        return render_template('ML_AI/sagemaker/invoke_endpoint.html', endpoint_names=endpoint_names)
    except Exception as e:
        flash(f'Error obteniendo endpoints: {str(e)}', 'error')
        return render_template('ML_AI/sagemaker/invoke_endpoint.html', endpoint_names=[])