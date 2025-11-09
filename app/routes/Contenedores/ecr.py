from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client
import boto3

bp = Blueprint('ecr', __name__)

@bp.route('/')
def index():
    return render_template('Contenedores/ecr/index.html')

@bp.route('/repositories')
def repositories():
    try:
        ecr = get_aws_client('ecr')
        repositories = ecr.describe_repositories()
        repo_list = []
        for repo in repositories['repositories']:
            # Get image count for each repository
            try:
                images = ecr.list_images(repositoryName=repo['repositoryName'])
                image_count = len(images.get('imageIds', []))
            except:
                image_count = 0

            repo_list.append({
                'name': repo['repositoryName'],
                'arn': repo['repositoryArn'],
                'uri': repo['repositoryUri'],
                'created_at': repo['createdAt'].strftime('%Y-%m-%d %H:%M:%S'),
                'image_count': image_count,
                'scan_on_push': repo.get('imageScanningConfiguration', {}).get('scanOnPush', False)
            })
        return render_template('Contenedores/ecr/repositories.html', repositories=repo_list)
    except Exception as e:
        flash(f'Error obteniendo repositorios ECR: {str(e)}', 'error')
        return render_template('Contenedores/ecr/repositories.html', repositories=[])

@bp.route('/create-repository', methods=['GET', 'POST'])
def create_repository():
    if request.method == 'POST':
        repo_name = request.form.get('repository_name')
        scan_on_push = request.form.get('scan_on_push') == 'on'

        try:
            ecr = get_aws_client('ecr')
            config = {
                'repositoryName': repo_name,
                'imageScanningConfiguration': {
                    'scanOnPush': scan_on_push
                }
            }
            response = ecr.create_repository(**config)
            flash(f'Repositorio ECR "{repo_name}" creado exitosamente', 'success')
            return redirect(url_for('ecr.repositories'))
        except Exception as e:
            flash(f'Error creando repositorio ECR: {str(e)}', 'error')
    return render_template('Contenedores/ecr/create_repository.html')

@bp.route('/repository/<repo_name>')
def repository_detail(repo_name):
    try:
        ecr = get_aws_client('ecr')

        # Get repository info
        repo_info = ecr.describe_repositories(repositoryNames=[repo_name])
        repository = repo_info['repositories'][0]

        # Get images
        images = ecr.list_images(repositoryName=repo_name)
        image_list = []

        for image_id in images.get('imageIds', []):
            image_detail = {
                'digest': image_id.get('imageDigest', ''),
                'tags': image_id.get('imageTag', 'latest'),
                'pushed_at': None,
                'size': None
            }

            # Get image details if available
            try:
                if 'imageDigest' in image_id:
                    details = ecr.describe_images(
                        repositoryName=repo_name,
                        imageIds=[{'imageDigest': image_id['imageDigest']}]
                    )
                    if details['imageDetails']:
                        img_detail = details['imageDetails'][0]
                        image_detail['pushed_at'] = img_detail.get('imagePushedAt', '').strftime('%Y-%m-%d %H:%M:%S') if img_detail.get('imagePushedAt') else None
                        image_detail['size'] = img_detail.get('imageSizeInBytes', 0)
            except:
                pass

            image_list.append(image_detail)

        return render_template('Contenedores/ecr/repository_detail.html',
                             repository=repository, images=image_list)
    except Exception as e:
        flash(f'Error obteniendo detalles del repositorio: {str(e)}', 'error')
        return redirect(url_for('ecr.repositories'))

@bp.route('/delete-repository/<repo_name>', methods=['POST'])
def delete_repository(repo_name):
    try:
        ecr = get_aws_client('ecr')
        ecr.delete_repository(repositoryName=repo_name, force=True)
        flash(f'Repositorio ECR "{repo_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando repositorio ECR: {str(e)}', 'error')
    return redirect(url_for('ecr.repositories'))

@bp.route('/repository/<repo_name>/policy', methods=['GET', 'POST'])
def repository_policy(repo_name):
    try:
        ecr = get_aws_client('ecr')

        if request.method == 'POST':
            policy_text = request.form.get('policy_text')
            try:
                if policy_text.strip():
                    ecr.set_repository_policy(
                        repositoryName=repo_name,
                        policyText=policy_text
                    )
                    flash('Política del repositorio actualizada exitosamente', 'success')
                else:
                    ecr.delete_repository_policy(repositoryName=repo_name)
                    flash('Política del repositorio eliminada exitosamente', 'success')
                return redirect(url_for('ecr.repository_policy', repo_name=repo_name))
            except Exception as e:
                flash(f'Error actualizando política: {str(e)}', 'error')

        # Get current policy
        try:
            policy = ecr.get_repository_policy(repositoryName=repo_name)
            current_policy = policy['policyText']
        except ecr.exceptions.RepositoryPolicyNotFoundException:
            current_policy = ''

        return render_template('Contenedores/ecr/repository_policy.html',
                             repo_name=repo_name, current_policy=current_policy)
    except Exception as e:
        flash(f'Error obteniendo política del repositorio: {str(e)}', 'error')
        return redirect(url_for('ecr.repositories'))