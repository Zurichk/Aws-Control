from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('ecs', __name__)

@bp.route('/')
def index():
    return render_template('Contenedores/ecs/index.html')

@bp.route('/clusters')
def clusters():
    try:
        ecs = get_aws_client('ecs')
        clusters = ecs.list_clusters()
        cluster_list = []
        if clusters['clusterArns']:
            cluster_details = ecs.describe_clusters(clusters=clusters['clusterArns'])
            for cluster in cluster_details['clusters']:
                cluster_list.append({
                    'name': cluster['clusterName'],
                    'arn': cluster['clusterArn'],
                    'status': cluster['status'],
                    'services': cluster.get('activeServicesCount', 0),
                    'tasks': cluster.get('runningTasksCount', 0)
                })
        return render_template('Contenedores/ecs/clusters.html', clusters=cluster_list)
    except Exception as e:
        flash(f'Error obteniendo clusters ECS: {str(e)}', 'error')
        return render_template('Contenedores/ecs/clusters.html', clusters=[])

@bp.route('/create-cluster', methods=['GET', 'POST'])
def create_cluster():
    if request.method == 'POST':
        cluster_name = request.form.get('cluster_name')
        try:
            ecs = get_aws_client('ecs')
            response = ecs.create_cluster(clusterName=cluster_name)
            flash(f'Cluster ECS "{cluster_name}" creado exitosamente', 'success')
            return redirect(url_for('ecs.clusters'))
        except Exception as e:
            flash(f'Error creando cluster ECS: {str(e)}', 'error')
    return render_template('Contenedores/ecs/create_cluster.html')

@bp.route('/delete-cluster/<cluster_name>', methods=['POST'])
def delete_cluster(cluster_name):
    try:
        ecs = get_aws_client('ecs')
        ecs.delete_cluster(cluster=cluster_name)
        flash(f'Cluster ECS "{cluster_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando cluster ECS: {str(e)}', 'error')
    return redirect(url_for('ecs.clusters'))

@bp.route('/cluster/<cluster_name>/services')
def services(cluster_name):
    try:
        ecs = get_aws_client('ecs')
        services_response = ecs.list_services(cluster=cluster_name)
        service_list = []
        if services_response['serviceArns']:
            service_details = ecs.describe_services(
                cluster=cluster_name,
                services=services_response['serviceArns']
            )
            for service in service_details['services']:
                service_list.append({
                    'name': service['serviceName'],
                    'arn': service['serviceArn'],
                    'status': service['status'],
                    'desired_count': service['desiredCount'],
                    'running_count': service['runningCount'],
                    'task_definition': service['taskDefinition'].split('/')[-1]
                })
        return render_template('Contenedores/ecs/services.html', 
                             cluster_name=cluster_name, 
                             services=service_list)
    except Exception as e:
        flash(f'Error obteniendo servicios ECS: {str(e)}', 'error')
        return render_template('Contenedores/ecs/services.html', 
                             cluster_name=cluster_name, 
                             services=[])

@bp.route('/cluster/<cluster_name>/create-service', methods=['GET', 'POST'])
def create_service(cluster_name):
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        task_definition = request.form.get('task_definition')
        desired_count = int(request.form.get('desired_count', 1))
        
        try:
            ecs = get_aws_client('ecs')
            ecs.create_service(
                cluster=cluster_name,
                serviceName=service_name,
                taskDefinition=task_definition,
                desiredCount=desired_count
            )
            flash(f'Servicio "{service_name}" creado exitosamente', 'success')
            return redirect(url_for('ecs.services', cluster_name=cluster_name))
        except Exception as e:
            flash(f'Error creando servicio: {str(e)}', 'error')
    
    # Obtener task definitions disponibles
    try:
        ecs = get_aws_client('ecs')
        task_defs = ecs.list_task_definitions()
        task_definitions = [td.split('/')[-1] for td in task_defs['taskDefinitionArns']]
    except:
        task_definitions = []
    
    return render_template('Contenedores/ecs/create_service.html', 
                         cluster_name=cluster_name,
                         task_definitions=task_definitions)

@bp.route('/cluster/<cluster_name>/update-service/<service_name>', methods=['GET', 'POST'])
def update_service(cluster_name, service_name):
    if request.method == 'POST':
        desired_count = int(request.form.get('desired_count', 1))
        
        try:
            ecs = get_aws_client('ecs')
            ecs.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=desired_count
            )
            flash(f'Servicio "{service_name}" actualizado exitosamente', 'success')
            return redirect(url_for('ecs.services', cluster_name=cluster_name))
        except Exception as e:
            flash(f'Error actualizando servicio: {str(e)}', 'error')
    
    # Obtener información actual del servicio
    try:
        ecs = get_aws_client('ecs')
        service_details = ecs.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        service = service_details['services'][0] if service_details['services'] else None
    except:
        service = None
    
    return render_template('Contenedores/ecs/update_service.html', 
                         cluster_name=cluster_name,
                         service=service)

@bp.route('/cluster/<cluster_name>/delete-service/<service_name>', methods=['POST'])
def delete_service(cluster_name, service_name):
    try:
        ecs = get_aws_client('ecs')
        ecs.delete_service(cluster=cluster_name, service=service_name)
        flash(f'Servicio "{service_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando servicio: {str(e)}', 'error')
    return redirect(url_for('ecs.services', cluster_name=cluster_name))

@bp.route('/cluster/<cluster_name>/tasks')
def tasks(cluster_name):
    try:
        ecs = get_aws_client('ecs')
        tasks_response = ecs.list_tasks(cluster=cluster_name)
        task_list = []
        if tasks_response['taskArns']:
            task_details = ecs.describe_tasks(
                cluster=cluster_name,
                tasks=tasks_response['taskArns']
            )
            for task in task_details['tasks']:
                task_list.append({
                    'arn': task['taskArn'],
                    'task_id': task['taskArn'].split('/')[-1],
                    'status': task['lastStatus'],
                    'desired_status': task['desiredStatus'],
                    'task_definition': task['taskDefinitionArn'].split('/')[-1],
                    'created_at': task['createdAt']
                })
        return render_template('Contenedores/ecs/tasks.html', 
                             cluster_name=cluster_name, 
                             tasks=task_list)
    except Exception as e:
        flash(f'Error obteniendo tareas ECS: {str(e)}', 'error')
        return render_template('Contenedores/ecs/tasks.html', 
                             cluster_name=cluster_name, 
                             tasks=[])

@bp.route('/cluster/<cluster_name>/run-task', methods=['GET', 'POST'])
def run_task(cluster_name):
    if request.method == 'POST':
        task_definition = request.form.get('task_definition')
        count = int(request.form.get('count', 1))
        
        try:
            ecs = get_aws_client('ecs')
            response = ecs.run_task(
                cluster=cluster_name,
                taskDefinition=task_definition,
                count=count
            )
            task_count = len(response['tasks'])
            flash(f'{task_count} tarea(s) ejecutada(s) exitosamente', 'success')
            return redirect(url_for('ecs.tasks', cluster_name=cluster_name))
        except Exception as e:
            flash(f'Error ejecutando tarea: {str(e)}', 'error')
    
    # Obtener task definitions disponibles
    try:
        ecs = get_aws_client('ecs')
        task_defs = ecs.list_task_definitions()
        task_definitions = [td.split('/')[-1] for td in task_defs['taskDefinitionArns']]
    except:
        task_definitions = []
    
    return render_template('Contenedores/ecs/run_task.html', 
                         cluster_name=cluster_name,
                         task_definitions=task_definitions)

@bp.route('/stop-task/<cluster_name>/<task_id>', methods=['POST'])
def stop_task(cluster_name, task_id):
    try:
        ecs = get_aws_client('ecs')
        ecs.stop_task(cluster=cluster_name, task=task_id)
        flash(f'Tarea "{task_id}" detenida exitosamente', 'success')
    except Exception as e:
        flash(f'Error deteniendo tarea: {str(e)}', 'error')
    return redirect(url_for('ecs.tasks', cluster_name=cluster_name))

@bp.route('/task-definitions')
def task_definitions():
    try:
        ecs = get_aws_client('ecs')
        task_defs = ecs.list_task_definitions()
        task_definition_list = []
        
        for td_arn in task_defs['taskDefinitionArns']:
            try:
                td_details = ecs.describe_task_definition(taskDefinition=td_arn)
                td = td_details['taskDefinition']
                task_definition_list.append({
                    'family': td['family'],
                    'revision': td['revision'],
                    'status': td['status'],
                    'cpu': td.get('cpu', 'N/A'),
                    'memory': td.get('memory', 'N/A'),
                    'container_count': len(td.get('containerDefinitions', []))
                })
            except:
                # Si hay error describiendo una definición, continuar
                continue
                
        return render_template('Contenedores/ecs/task_definitions.html', 
                             task_definitions=task_definition_list)
    except Exception as e:
        flash(f'Error obteniendo definiciones de tareas: {str(e)}', 'error')
        return render_template('Contenedores/ecs/task_definitions.html', 
                             task_definitions=[])

@bp.route('/register-task-definition', methods=['GET', 'POST'])
def register_task_definition():
    if request.method == 'POST':
        family = request.form.get('family')
        cpu = request.form.get('cpu')
        memory = request.form.get('memory')
        container_name = request.form.get('container_name')
        image = request.form.get('image')
        
        try:
            container_definitions = [{
                'name': container_name,
                'image': image,
                'essential': True
            }]
            
            task_def = {
                'family': family,
                'containerDefinitions': container_definitions
            }
            
            if cpu:
                task_def['cpu'] = cpu
            if memory:
                task_def['memory'] = memory
            
            ecs = get_aws_client('ecs')
            ecs.register_task_definition(**task_def)
            
            flash(f'Definición de tarea "{family}" registrada exitosamente', 'success')
            return redirect(url_for('ecs.task_definitions'))
        except Exception as e:
            flash(f'Error registrando definición de tarea: {str(e)}', 'error')
    
    return render_template('Contenedores/ecs/register_task_definition.html')