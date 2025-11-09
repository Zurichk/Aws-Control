from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('glue', __name__)

@bp.route('/')
def index():
    """Página principal de AWS Glue"""
    try:
        glue = get_aws_client('glue')
        # Listar crawlers
        crawlers_response = glue.get_crawlers()
        crawlers = crawlers_response.get('Crawlers', [])

        # Listar jobs
        jobs_response = glue.get_jobs()
        jobs = jobs_response.get('Jobs', [])

        return render_template('glue/index.html', crawlers=crawlers, jobs=jobs)
    except Exception as e:
        flash(f'Error al cargar Glue: {str(e)}', 'error')
        return render_template('glue/index.html', crawlers=[], jobs=[])

@bp.route('/crawlers')
def crawlers():
    """Listar todos los crawlers"""
    try:
        glue = get_aws_client('glue')
        crawlers_response = glue.get_crawlers()
        crawlers = crawlers_response.get('Crawlers', [])
        return render_template('glue/crawlers.html', crawlers=crawlers)
    except Exception as e:
        flash(f'Error al listar crawlers: {str(e)}', 'error')
        return render_template('glue/crawlers.html', crawlers=[])

@bp.route('/create-crawler', methods=['GET', 'POST'])
def create_crawler():
    """Crear un nuevo crawler"""
    if request.method == 'POST':
        try:
            glue = get_aws_client('glue')

            crawler_name = request.form.get('crawler_name')
            role = request.form.get('role')
            database_name = request.form.get('database_name')
            s3_targets = request.form.get('s3_targets', '').split('\n')
            s3_targets = [target.strip() for target in s3_targets if target.strip()]

            # Crear crawler
            glue.create_crawler(
                Name=crawler_name,
                Role=role,
                DatabaseName=database_name,
                Targets={
                    'S3Targets': [{'Path': target} for target in s3_targets]
                }
            )

            flash(f'Crawler "{crawler_name}" creado exitosamente', 'success')
            return redirect(url_for('glue.crawlers'))

        except Exception as e:
            flash(f'Error al crear crawler: {str(e)}', 'error')

    return render_template('glue/create_crawler.html')

@bp.route('/crawler/<crawler_name>/start', methods=['POST'])
def start_crawler(crawler_name):
    """Iniciar un crawler"""
    try:
        glue = get_aws_client('glue')
        glue.start_crawler(Name=crawler_name)
        flash(f'Crawler "{crawler_name}" iniciado', 'success')
    except Exception as e:
        flash(f'Error al iniciar crawler: {str(e)}', 'error')

    return redirect(url_for('glue.crawlers'))

@bp.route('/jobs')
def jobs():
    """Listar todos los jobs"""
    try:
        glue = get_aws_client('glue')
        jobs_response = glue.get_jobs()
        jobs = jobs_response.get('Jobs', [])
        return render_template('glue/jobs.html', jobs=jobs)
    except Exception as e:
        flash(f'Error al listar jobs: {str(e)}', 'error')
        return render_template('glue/jobs.html', jobs=[])

@bp.route('/create-job', methods=['GET', 'POST'])
def create_job():
    """Crear un nuevo job ETL"""
    if request.method == 'POST':
        try:
            glue = get_aws_client('glue')

            job_name = request.form.get('job_name')
            role = request.form.get('role')
            script_location = request.form.get('script_location')
            max_capacity = float(request.form.get('max_capacity', 2.0))

            # Crear job
            glue.create_job(
                Name=job_name,
                Role=role,
                Command={
                    'Name': 'glueetl',
                    'ScriptLocation': script_location
                },
                MaxCapacity=max_capacity
            )

            flash(f'Job "{job_name}" creado exitosamente', 'success')
            return redirect(url_for('glue.jobs'))

        except Exception as e:
            flash(f'Error al crear job: {str(e)}', 'error')

    return render_template('glue/create_job.html')

@bp.route('/job/<job_name>/run', methods=['POST'])
def start_job_run(job_name):
    """Ejecutar un job"""
    try:
        glue = get_aws_client('glue')
        response = glue.start_job_run(JobName=job_name)
        job_run_id = response.get('JobRunId')
        flash(f'Job "{job_name}" ejecutado. Run ID: {job_run_id}', 'success')
    except Exception as e:
        flash(f'Error al ejecutar job: {str(e)}', 'error')

    return redirect(url_for('glue.jobs'))