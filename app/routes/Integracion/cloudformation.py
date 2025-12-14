from flask import Blueprint, render_template, request, flash, redirect, url_for, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('cloudformation', __name__)

@bp.route('/')
@bp.route('/stacks')
def stacks():
    try:
        cf = get_aws_client('cloudformation')
        stacks = cf.describe_stacks()
        stack_list = []
        for stack in stacks['Stacks']:
            stack_list.append({
                'name': stack['StackName'],
                'status': stack['StackStatus'],
                'description': stack.get('Description', 'N/A'),
                'creation_time': stack['CreationTime'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('Integracion/stacks.html', stacks=stack_list)
    except Exception as e:
        flash(f'Error obteniendo stacks de CloudFormation: {str(e)}', 'error')
        return render_template('Integracion/stacks.html', stacks=[])

@bp.route('/stack/<stack_name>')
def stack_detail(stack_name):
    try:
        cf = get_aws_client('cloudformation')
        
        # Obtener detalles del stack
        stack_response = cf.describe_stacks(StackName=stack_name)
        stack = stack_response['Stacks'][0]
        
        # Obtener eventos del stack
        events_response = cf.describe_stack_events(StackName=stack_name)
        events = events_response['StackEvents'][:50]  # Últimos 50 eventos
        
        # Obtener recursos del stack
        resources_response = cf.describe_stack_resources(StackName=stack_name)
        resources = resources_response['StackResources']
        
        return render_template('Integracion/stack_detail.html', 
                             stack=stack, events=events, resources=resources)
    except Exception as e:
        flash(f'Error obteniendo detalles del stack: {str(e)}', 'error')
        return redirect(url_for('cloudformation.stacks'))

@bp.route('/create', methods=['GET', 'POST'])
def create_stack():
    if request.method == 'POST':
        try:
            stack_name = request.form.get('stack_name')
            template_body = request.form.get('template_body')
            template_url = request.form.get('template_url')
            parameters = []
            
            # Procesar parámetros dinámicos
            param_keys = request.form.getlist('param_key[]')
            param_values = request.form.getlist('param_value[]')
            
            for key, value in zip(param_keys, param_values):
                if key and value:
                    parameters.append({'ParameterKey': key, 'ParameterValue': value})
            
            cf = get_aws_client('cloudformation')
            
            kwargs = {
                'StackName': stack_name,
                'Parameters': parameters
            }
            
            if template_body:
                kwargs['TemplateBody'] = template_body
            elif template_url:
                kwargs['TemplateURL'] = template_url
            else:
                flash('Debe proporcionar un template (body o URL)', 'error')
                return redirect(url_for('cloudformation.create_stack'))
            
            response = cf.create_stack(**kwargs)
            flash(f'Stack {stack_name} creado exitosamente. ID: {response["StackId"]}', 'success')
            return redirect(url_for('cloudformation.stacks'))
            
        except Exception as e:
            flash(f'Error creando stack: {str(e)}', 'error')
            return redirect(url_for('cloudformation.create_stack'))
    
    return render_template('Integracion/create_stack.html')

@bp.route('/update/<stack_name>', methods=['GET', 'POST'])
def update_stack(stack_name):
    if request.method == 'POST':
        try:
            template_body = request.form.get('template_body')
            template_url = request.form.get('template_url')
            parameters = []
            
            # Procesar parámetros dinámicos
            param_keys = request.form.getlist('param_key[]')
            param_values = request.form.getlist('param_value[]')
            
            for key, value in zip(param_keys, param_values):
                if key and value:
                    parameters.append({'ParameterKey': key, 'ParameterValue': value})
            
            cf = get_aws_client('cloudformation')
            
            kwargs = {
                'StackName': stack_name,
                'Parameters': parameters
            }
            
            if template_body:
                kwargs['TemplateBody'] = template_body
            elif template_url:
                kwargs['TemplateURL'] = template_url
            else:
                flash('Debe proporcionar un template (body o URL)', 'error')
                return redirect(url_for('cloudformation.update_stack', stack_name=stack_name))
            
            response = cf.update_stack(**kwargs)
            flash(f'Stack {stack_name} actualizado exitosamente', 'success')
            return redirect(url_for('cloudformation.stack_detail', stack_name=stack_name))
            
        except Exception as e:
            flash(f'Error actualizando stack: {str(e)}', 'error')
            return redirect(url_for('cloudformation.update_stack', stack_name=stack_name))
    
    # GET: Mostrar formulario con información actual del stack
    try:
        cf = get_aws_client('cloudformation')
        stack_response = cf.describe_stacks(StackName=stack_name)
        stack = stack_response['Stacks'][0]
        return render_template('Integracion/update_stack.html', stack=stack)
    except Exception as e:
        flash(f'Error obteniendo stack: {str(e)}', 'error')
        return redirect(url_for('cloudformation.stacks'))

@bp.route('/delete/<stack_name>', methods=['POST'])
def delete_stack(stack_name):
    try:
        cf = get_aws_client('cloudformation')
        cf.delete_stack(StackName=stack_name)
        flash(f'Stack {stack_name} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando stack: {str(e)}', 'error')
    
    return redirect(url_for('cloudformation.stacks'))