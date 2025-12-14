"""
Rutas para AWS Batch
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('batch', __name__)

@bp.route('/')
def index():
    """Página principal de AWS Batch"""
    return render_template('Computo/batch/index.html')

@bp.route('/jobs')
def list_jobs():
    """Lista trabajos de AWS Batch"""
    try:
        batch = get_aws_client('batch')
        response = batch.list_jobs()

        jobs = []
        for job_summary in response.get('jobSummaryList', []):
            jobs.append({
                'job_id': job_summary['jobId'],
                'job_name': job_summary['jobName'],
                'job_queue': job_summary['jobQueue'],
                'status': job_summary['status'],
                'created_at': job_summary.get('createdAt', ''),
                'started_at': job_summary.get('startedAt', ''),
                'stopped_at': job_summary.get('stoppedAt', '')
            })

        return render_template('Computo/batch/jobs.html', jobs=jobs)
    except Exception as e:
        flash(f'Error obteniendo trabajos: {str(e)}', 'error')
        return render_template('Computo/batch/jobs.html', jobs=[])

@bp.route('/job/<job_id>')
def job_detail(job_id):
    """Detalle de un trabajo específico"""
    try:
        batch = get_aws_client('batch')
        response = batch.describe_jobs(jobs=[job_id])

        if not response.get('jobs'):
            flash('Trabajo no encontrado', 'error')
            return redirect(url_for('batch.list_jobs'))

        job = response['jobs'][0]

        job_data = {
            'job_id': job['jobId'],
            'job_name': job['jobName'],
            'job_queue': job['jobQueue'],
            'job_definition': job['jobDefinition'],
            'status': job['status'],
            'status_reason': job.get('statusReason', ''),
            'created_at': job.get('createdAt', ''),
            'started_at': job.get('startedAt', ''),
            'stopped_at': job.get('stoppedAt', ''),
            'container': job.get('container', {}),
            'parameters': job.get('parameters', {}),
            'attempts': job.get('attempts', [])
        }

        return render_template('Computo/batch/job_detail.html', job=job_data)
    except Exception as e:
        flash(f'Error obteniendo detalle del trabajo: {str(e)}', 'error')
        return redirect(url_for('batch.list_jobs'))

@bp.route('/submit_job', methods=['GET', 'POST'])
def submit_job():
    """Enviar un nuevo trabajo"""
    try:
        batch = get_aws_client('batch')

        if request.method == 'POST':
            job_name = request.form.get('job_name')
            job_queue = request.form.get('job_queue')
            job_definition = request.form.get('job_definition')
            command = request.form.get('command')
            vcpus = int(request.form.get('vcpus', 1))
            memory = int(request.form.get('memory', 128))

            # Preparar overrides de contenedor
            container_overrides = {
                'vcpus': vcpus,
                'memory': memory
            }

            if command:
                container_overrides['command'] = command.split()

            # Parámetros adicionales
            parameters = {}
            param_keys = request.form.getlist('param_key[]')
            param_values = request.form.getlist('param_value[]')
            for key, value in zip(param_keys, param_values):
                if key and value:
                    parameters[key] = value

            submit_params = {
                'jobName': job_name,
                'jobQueue': job_queue,
                'jobDefinition': job_definition,
                'containerOverrides': container_overrides
            }

            if parameters:
                submit_params['parameters'] = parameters

            response = batch.submit_job(**submit_params)
            flash(f'Trabajo {response["jobId"]} enviado exitosamente', 'success')
            return redirect(url_for('batch.job_detail', job_id=response['jobId']))

        # Obtener colas de trabajo disponibles
        job_queues = []
        try:
            response = batch.describe_job_queues()
            job_queues = [queue['jobQueueName'] for queue in response.get('jobQueues', [])]
        except:
            job_queues = []

        # Obtener definiciones de trabajo disponibles
        job_definitions = []
        try:
            response = batch.describe_job_definitions()
            job_definitions = [jd['jobDefinitionName'] for jd in response.get('jobDefinitions', [])]
        except:
            job_definitions = []

        return render_template('Computo/batch/submit_job.html',
                             job_queues=job_queues,
                             job_definitions=job_definitions)

    except Exception as e:
        flash(f'Error enviando trabajo: {str(e)}', 'error')
        return redirect(url_for('batch.list_jobs'))

@bp.route('/job/<job_id>/terminate', methods=['POST'])
def terminate_job(job_id):
    """Terminar un trabajo"""
    try:
        batch = get_aws_client('batch')
        reason = request.form.get('reason', 'Terminado por usuario')

        batch.terminate_job(jobId=job_id, reason=reason)
        flash(f'Trabajo {job_id} terminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error terminando trabajo: {str(e)}', 'error')

    return redirect(url_for('batch.job_detail', job_id=job_id))

@bp.route('/compute_environments')
def list_compute_environments():
    """Lista entornos de cómputo"""
    try:
        batch = get_aws_client('batch')
        response = batch.describe_compute_environments()

        compute_envs = []
        for ce in response.get('computeEnvironments', []):
            compute_envs.append({
                'compute_environment_name': ce['computeEnvironmentName'],
                'compute_environment_arn': ce['computeEnvironmentArn'],
                'status': ce['status'],
                'state': ce['state'],
                'type': ce['type'],
                'ecs_cluster_arn': ce.get('ecsClusterArn', ''),
                'service_role': ce.get('serviceRole', '')
            })

        return render_template('Computo/batch/compute_environments.html', compute_environments=compute_envs)
    except Exception as e:
        flash(f'Error obteniendo entornos de cómputo: {str(e)}', 'error')
        return render_template('Computo/batch/compute_environments.html', compute_environments=[])

@bp.route('/create_compute_environment', methods=['GET', 'POST'])
def create_compute_environment():
    """Crear un nuevo entorno de cómputo"""
    try:
        batch = get_aws_client('batch')
        ec2 = get_aws_client('ec2')

        if request.method == 'POST':
            ce_name = request.form.get('compute_environment_name')
            ce_type = request.form.get('type')
            state = request.form.get('state', 'ENABLED')

            create_params = {
                'computeEnvironmentName': ce_name,
                'type': ce_type,
                'state': state
            }

            if ce_type == 'MANAGED':
                # Configuración para entornos manejados
                min_cpus = int(request.form.get('minvCpus', 0))
                max_cpus = int(request.form.get('maxvCpus', 256))
                desired_cpus = int(request.form.get('desiredvCpus', 0))
                instance_types = request.form.getlist('instance_types[]')
                subnets = request.form.getlist('subnets[]')
                security_groups = request.form.getlist('security_groups[]')

                create_params['computeResources'] = {
                    'minvCpus': min_cpus,
                    'maxvCpus': max_cpus,
                    'desiredvCpus': desired_cpus,
                    'instanceTypes': instance_types,
                    'subnets': subnets,
                    'securityGroupIds': security_groups,
                    'instanceRole': request.form.get('instance_role'),
                    'allocationStrategy': request.form.get('allocation_strategy', 'BEST_FIT')
                }

            elif ce_type == 'UNMANAGED':
                # Para entornos no manejados, especificar ECS cluster ARN
                create_params['ecsClusterArn'] = request.form.get('ecs_cluster_arn')

            response = batch.create_compute_environment(**create_params)
            flash(f'Entorno de cómputo {ce_name} creado exitosamente', 'success')
            return redirect(url_for('batch.list_compute_environments'))

        # Obtener datos para el formulario
        subnets = []
        security_groups = []
        try:
            # Obtener subnets
            vpc_response = ec2.describe_subnets()
            subnets = [{'id': s['SubnetId'], 'cidr': s['CidrBlock']} for s in vpc_response.get('Subnets', [])]

            # Obtener security groups
            sg_response = ec2.describe_security_groups()
            security_groups = [{'id': sg['GroupId'], 'name': sg.get('GroupName', 'N/A')} for sg in sg_response.get('SecurityGroups', [])]
        except:
            pass

        return render_template('Computo/batch/create_compute_environment.html',
                             subnets=subnets,
                             security_groups=security_groups)

    except Exception as e:
        flash(f'Error creando entorno de cómputo: {str(e)}', 'error')
        return redirect(url_for('batch.list_compute_environments'))

@bp.route('/compute_environment/<ce_name>/delete', methods=['POST'])
def delete_compute_environment(ce_name):
    """Eliminar un entorno de cómputo"""
    try:
        batch = get_aws_client('batch')
        batch.delete_compute_environment(computeEnvironment=ce_name)
        flash(f'Entorno de cómputo {ce_name} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando entorno de cómputo: {str(e)}', 'error')

    return redirect(url_for('batch.list_compute_environments'))