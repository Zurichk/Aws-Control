from flask import Blueprint, render_template, request, flash
from app.utils.aws_client import get_aws_client

bp = Blueprint('apigateway', __name__)

@bp.route('/')
def index():
    return render_template('Redes/apigateway/index.html')

@bp.route('/apis')
def apis():
    try:
        apigw = get_aws_client('apigateway')
        apis = apigw.get_rest_apis()
        api_list = []
        for api in apis['items']:
            api_list.append({
                'id': api['id'],
                'name': api['name'],
                'description': api.get('description', 'N/A'),
                'endpoint': api.get('endpointConfiguration', {}).get('types', ['N/A'])[0],
                'created': api.get('createdDate', '').strftime('%Y-%m-%d %H:%M:%S') if api.get('createdDate') else 'N/A'
            })
        return render_template('Redes/apigateway/apis.html', apis=api_list)
    except Exception as e:
        flash(f'Error obteniendo APIs de API Gateway: {str(e)}', 'error')
        return render_template('Redes/apigateway/apis.html', apis=[])