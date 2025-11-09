from flask import Blueprint, render_template, request, flash, redirect, url_for, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('sqs', __name__)

@bp.route('/')
def index():
    return render_template('Mensajeria/sqs/index.html')

@bp.route('/queues')
def queues():
    try:
        sqs = get_aws_client('sqs')
        queues = sqs.list_queues()
        queue_list = []
        if 'QueueUrls' in queues:
            for queue_url in queues['QueueUrls']:
                queue_attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
                attrs = queue_attrs['Attributes']
                queue_list.append({
                    'url': queue_url,
                    'name': queue_url.split('/')[-1],
                    'messages': attrs.get('ApproximateNumberOfMessages', '0'),
                    'visibility_timeout': attrs.get('VisibilityTimeout', 'N/A')
                })
        return render_template('Mensajeria/sqs/queues.html', queues=queue_list)
    except Exception as e:
        flash(f'Error obteniendo colas SQS: {str(e)}', 'error')
        return render_template('Mensajeria/sqs/queues.html', queues=[])

@bp.route('/queue/create', methods=['GET', 'POST'])
def create_queue():
    """Crear una nueva cola SQS"""
    if request.method == 'POST':
        try:
            sqs = get_aws_client('sqs')
            queue_name = request.form.get('queue_name')
            queue_type = request.form.get('queue_type', 'standard')  # standard o fifo
            
            attributes = {}
            if queue_type == 'fifo':
                attributes['FifoQueue'] = 'true'
                if not queue_name.endswith('.fifo'):
                    queue_name += '.fifo'
            
            response = sqs.create_queue(QueueName=queue_name, Attributes=attributes)
            
            flash(f'Cola "{queue_name}" creada exitosamente', 'success')
            return redirect(url_for('sqs.queues'))
        except Exception as e:
            flash(f'Error creando cola: {str(e)}', 'error')
            return redirect(url_for('sqs.create_queue'))
    
    return render_template('Mensajeria/sqs/create_queue.html')

@bp.route('/queue/<queue_name>')
def queue_detail(queue_name):
    """Ver detalles de una cola SQS"""
    try:
        sqs = get_aws_client('sqs')
        
        # Obtener URL de la cola
        queues = sqs.list_queues()
        queue_url = None
        if 'QueueUrls' in queues:
            for url in queues['QueueUrls']:
                if url.split('/')[-1] == queue_name:
                    queue_url = url
                    break
        
        if not queue_url:
            flash('Cola no encontrada', 'error')
            return redirect(url_for('sqs.queues'))
        
        # Obtener atributos de la cola
        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
        
        queue_data = {
            'name': queue_name,
            'url': queue_url,
            'attributes': attrs['Attributes']
        }
        
        return render_template('Mensajeria/sqs/queue_detail.html', queue=queue_data)
    except Exception as e:
        flash(f'Error obteniendo detalles de la cola: {str(e)}', 'error')
        return redirect(url_for('sqs.queues'))

@bp.route('/queue/<queue_name>/send', methods=['GET', 'POST'])
def send_message(queue_name):
    """Enviar un mensaje a una cola SQS"""
    if request.method == 'POST':
        try:
            sqs = get_aws_client('sqs')
            
            # Obtener URL de la cola
            queues = sqs.list_queues()
            queue_url = None
            if 'QueueUrls' in queues:
                for url in queues['QueueUrls']:
                    if url.split('/')[-1] == queue_name:
                        queue_url = url
                        break
            
            if not queue_url:
                flash('Cola no encontrada', 'error')
                return redirect(url_for('sqs.send_message', queue_name=queue_name))
            
            message_body = request.form.get('message_body')
            message_group_id = request.form.get('message_group_id')  # Para colas FIFO
            
            if message_group_id:
                sqs.send_message(QueueUrl=queue_url, MessageBody=message_body, MessageGroupId=message_group_id)
            else:
                sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
            
            flash('Mensaje enviado exitosamente', 'success')
            return redirect(url_for('sqs.queue_detail', queue_name=queue_name))
        except Exception as e:
            flash(f'Error enviando mensaje: {str(e)}', 'error')
            return redirect(url_for('sqs.send_message', queue_name=queue_name))
    
    return render_template('Mensajeria/sqs/send_message.html', queue_name=queue_name)

@bp.route('/queue/<queue_name>/receive')
def receive_messages(queue_name):
    """Recibir mensajes de una cola SQS"""
    try:
        sqs = get_aws_client('sqs')
        
        # Obtener URL de la cola
        queues = sqs.list_queues()
        queue_url = None
        if 'QueueUrls' in queues:
            for url in queues['QueueUrls']:
                if url.split('/')[-1] == queue_name:
                    queue_url = url
                    break
        
        if not queue_url:
            flash('Cola no encontrada', 'error')
            return redirect(url_for('sqs.queues'))
        
        # Recibir mensajes
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
        messages = response.get('Messages', [])
        
        return render_template('Mensajeria/sqs/receive_messages.html', 
                             queue_name=queue_name, messages=messages)
    except Exception as e:
        flash(f'Error recibiendo mensajes: {str(e)}', 'error')
        return redirect(url_for('sqs.queue_detail', queue_name=queue_name))

@bp.route('/queue/<queue_name>/delete', methods=['POST'])
def delete_queue(queue_name):
    """Eliminar una cola SQS"""
    try:
        sqs = get_aws_client('sqs')
        
        # Obtener URL de la cola
        queues = sqs.list_queues()
        queue_url = None
        if 'QueueUrls' in queues:
            for url in queues['QueueUrls']:
                if url.split('/')[-1] == queue_name:
                    queue_url = url
                    break
        
        if not queue_url:
            flash('Cola no encontrada', 'error')
            return redirect(url_for('sqs.queues'))
        
        sqs.delete_queue(QueueUrl=queue_url)
        
        flash(f'Cola "{queue_name}" eliminada exitosamente', 'success')
        return redirect(url_for('sqs.queues'))
    except Exception as e:
        flash(f'Error eliminando cola: {str(e)}', 'error')
        return redirect(url_for('sqs.queues'))