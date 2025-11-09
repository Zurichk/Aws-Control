from flask import Blueprint, render_template, request, flash
from app.utils.aws_client import get_aws_client

bp = Blueprint('sagemaker', __name__)

@bp.route('/')
def index():
    return render_template('ML_AI/sagemaker/index.html')

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