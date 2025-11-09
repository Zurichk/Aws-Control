from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('sns', __name__)

@bp.route('/')
def index():
    return render_template('Mensajeria/sns/index.html')

@bp.route('/topics')
def topics():
    try:
        sns = get_aws_client('sns')
        topics = sns.list_topics()
        topic_list = []
        for topic_arn in topics['Topics']:
            topic_list.append({
                'arn': topic_arn['TopicArn'],
                'name': topic_arn['TopicArn'].split(':')[-1]
            })
        return render_template('Mensajeria/sns/topics.html', topics=topic_list)
    except Exception as e:
        flash(f'Error obteniendo tópicos SNS: {str(e)}', 'error')
        return render_template('Mensajeria/sns/topics.html', topics=[])

@bp.route('/create_topic', methods=['GET', 'POST'])
def create_topic():
    if request.method == 'POST':
        topic_name = request.form.get('topic_name')
        if not topic_name:
            flash('El nombre del tópico es requerido', 'error')
            return redirect(url_for('create_topic'))

        try:
            sns = get_aws_client('sns')
            response = sns.create_topic(Name=topic_name)
            flash(f'Tópico "{topic_name}" creado exitosamente', 'success')
            return redirect(url_for('topics'))
        except Exception as e:
            flash(f'Error creando tópico: {str(e)}', 'error')
            return redirect(url_for('create_topic'))

    return render_template('Mensajeria/sns/create_topic.html')

@bp.route('/topic/<topic_name>')
def topic_detail(topic_name):
    try:
        sns = get_aws_client('sns')
        # Obtener ARN del tópico
        topics = sns.list_topics()
        topic_arn = None
        for topic in topics['Topics']:
            if topic['TopicArn'].split(':')[-1] == topic_name:
                topic_arn = topic['TopicArn']
                break

        if not topic_arn:
            flash('Tópico no encontrado', 'error')
            return redirect(url_for('topics'))

        # Obtener atributos del tópico
        attributes = sns.get_topic_attributes(TopicArn=topic_arn)

        topic_info = {
            'name': topic_name,
            'arn': topic_arn,
            'attributes': attributes['Attributes']
        }

        return render_template('Mensajeria/sns/topic_detail.html', topic=topic_info)
    except Exception as e:
        flash(f'Error obteniendo detalles del tópico: {str(e)}', 'error')
        return redirect(url_for('topics'))

@bp.route('/publish_message/<topic_name>', methods=['GET', 'POST'])
def publish_message(topic_name):
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not message:
            flash('El mensaje es requerido', 'error')
            return redirect(url_for('publish_message', topic_name=topic_name))

        try:
            sns = get_aws_client('sns')
            # Obtener ARN del tópico
            topics = sns.list_topics()
            topic_arn = None
            for topic in topics['Topics']:
                if topic['TopicArn'].split(':')[-1] == topic_name:
                    topic_arn = topic['TopicArn']
                    break

            if not topic_arn:
                flash('Tópico no encontrado', 'error')
                return redirect(url_for('topics'))

            # Publicar mensaje
            publish_params = {'TopicArn': topic_arn, 'Message': message}
            if subject:
                publish_params['Subject'] = subject

            sns.publish(**publish_params)
            flash('Mensaje publicado exitosamente', 'success')
            return redirect(url_for('topic_detail', topic_name=topic_name))
        except Exception as e:
            flash(f'Error publicando mensaje: {str(e)}', 'error')
            return redirect(url_for('publish_message', topic_name=topic_name))

    return render_template('Mensajeria/sns/publish_message.html', topic_name=topic_name)

@bp.route('/delete_topic/<topic_name>', methods=['POST'])
def delete_topic(topic_name):
    try:
        sns = get_aws_client('sns')
        # Obtener ARN del tópico
        topics = sns.list_topics()
        topic_arn = None
        for topic in topics['Topics']:
            if topic['TopicArn'].split(':')[-1] == topic_name:
                topic_arn = topic['TopicArn']
                break

        if not topic_arn:
            flash('Tópico no encontrado', 'error')
            return redirect(url_for('topics'))

        # Eliminar tópico
        sns.delete_topic(TopicArn=topic_arn)
        flash(f'Tópico "{topic_name}" eliminado exitosamente', 'success')
        return redirect(url_for('topics'))
    except Exception as e:
        flash(f'Error eliminando tópico: {str(e)}', 'error')
        return redirect(url_for('topics'))
