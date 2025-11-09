from flask import Blueprint, render_template, request, flash
from app.utils.aws_client import get_aws_client

bp = Blueprint('elbv2', __name__)

@bp.route('/elbv2')
def index():
    return render_template('Redes/elbv2/index.html')

@bp.route('/elbv2/load-balancers')
def load_balancers():
    try:
        elbv2 = get_aws_client('elbv2')
        lbs = elbv2.describe_load_balancers()
        lb_list = []
        for lb in lbs['LoadBalancers']:
            lb_list.append({
                'name': lb['LoadBalancerName'],
                'arn': lb['LoadBalancerArn'],
                'dns_name': lb['DNSName'],
                'state': lb['State']['Code'],
                'type': lb['Type']
            })
        return render_template('Redes/elbv2/load_balancers.html', load_balancers=lb_list)
    except Exception as e:
        flash(f'Error obteniendo load balancers: {str(e)}', 'error')
        return render_template('Redes/elbv2/load_balancers.html', load_balancers=[])