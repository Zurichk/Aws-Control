from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.utils.aws_client import get_aws_client

bp = Blueprint('iam', __name__)

@bp.route('/iam')
def index():
    return render_template('Seguridad/index.html')

@bp.route('/iam/users')
def users():
    try:
        iam = get_aws_client('iam')
        users = iam.list_users()
        user_list = []
        for user in users['Users']:
            user_list.append({
                'name': user['UserName'],
                'id': user['UserId'],
                'arn': user['Arn'],
                'create_date': user['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('Seguridad/users.html', users=user_list)
    except Exception as e:
        flash(f'Error obteniendo usuarios IAM: {str(e)}', 'error')
        return render_template('Seguridad/users.html', users=[])

@bp.route('/iam/roles')
def roles():
    try:
        iam = get_aws_client('iam')
        roles = iam.list_roles()
        role_list = []
        for role in roles['Roles']:
            role_list.append({
                'name': role['RoleName'],
                'id': role['RoleId'],
                'arn': role['Arn'],
                'create_date': role['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('Seguridad/roles.html', roles=role_list)
    except Exception as e:
        flash(f'Error obteniendo roles IAM: {str(e)}', 'error')
        return render_template('Seguridad/roles.html', roles=[])

@bp.route('/iam/user/create', methods=['GET', 'POST'])
def create_user():
    """Crear un nuevo usuario IAM"""
    if request.method == 'POST':
        try:
            iam = get_aws_client('iam')
            username = request.form.get('username')
            
            # Crear usuario
            iam.create_user(UserName=username)
            
            flash(f'Usuario IAM "{username}" creado exitosamente', 'success')
            return redirect(url_for('iam.users'))
        except Exception as e:
            flash(f'Error creando usuario IAM: {str(e)}', 'error')
            return redirect(url_for('iam.users'))
    
    return render_template('Seguridad/create_user.html')

@bp.route('/iam/user/<username>/delete', methods=['POST'])
def delete_user(username):
    """Eliminar un usuario IAM"""
    try:
        iam = get_aws_client('iam')
        
        # Primero eliminar access keys
        try:
            access_keys = iam.list_access_keys(UserName=username)
            for key in access_keys['AccessKeyMetadata']:
                iam.delete_access_key(UserName=username, AccessKeyId=key['AccessKeyId'])
        except Exception:
            pass  # Ignorar si no hay keys
        
        # Eliminar usuario
        iam.delete_user(UserName=username)
        
        flash(f'Usuario IAM "{username}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando usuario IAM: {str(e)}', 'error')
    
    return redirect(url_for('iam.users'))

@bp.route('/iam/role/create', methods=['GET', 'POST'])
def create_role():
    """Crear un nuevo rol IAM"""
    if request.method == 'POST':
        try:
            iam = get_aws_client('iam')
            role_name = request.form.get('role_name')
            assume_role_policy = request.form.get('assume_role_policy')
            
            # Crear rol
            iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=assume_role_policy
            )
            
            flash(f'Rol IAM "{role_name}" creado exitosamente', 'success')
            return redirect(url_for('iam.roles'))
        except Exception as e:
            flash(f'Error creando rol IAM: {str(e)}', 'error')
            return redirect(url_for('iam.roles'))
    
    return render_template('Seguridad/create_role.html')

@bp.route('/iam/role/<role_name>/delete', methods=['POST'])
def delete_role(role_name):
    """Eliminar un rol IAM"""
    try:
        iam = get_aws_client('iam')
        
        # Primero detach todas las policies
        try:
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
        except Exception:
            pass
        
        # Eliminar rol
        iam.delete_role(RoleName=role_name)
        
        flash(f'Rol IAM "{role_name}" eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando rol IAM: {str(e)}', 'error')
    
    return redirect(url_for('iam.roles'))

@bp.route('/iam/policies')
def policies():
    """Listar policies IAM"""
    try:
        iam = get_aws_client('iam')
        policies = iam.list_policies(Scope='Local')  # Solo policies de la cuenta
        policy_list = []
        for policy in policies['Policies']:
            policy_list.append({
                'name': policy['PolicyName'],
                'id': policy['PolicyId'],
                'arn': policy['Arn'],
                'create_date': policy['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'description': policy.get('Description', 'Sin descripción')
            })
        return render_template('Seguridad/policies.html', policies=policy_list)
    except Exception as e:
        flash(f'Error obteniendo policies IAM: {str(e)}', 'error')
        return render_template('Seguridad/policies.html', policies=[])

@bp.route('/iam/policy/create', methods=['GET', 'POST'])
def create_policy():
    """Crear una nueva policy IAM"""
    if request.method == 'POST':
        try:
            iam = get_aws_client('iam')
            policy_name = request.form.get('policy_name')
            policy_document = request.form.get('policy_document')
            description = request.form.get('description', '')
            
            # Crear policy
            iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=policy_document,
                Description=description
            )
            
            flash(f'Policy IAM "{policy_name}" creada exitosamente', 'success')
            return redirect(url_for('iam.policies'))
        except Exception as e:
            flash(f'Error creando policy IAM: {str(e)}', 'error')
            return redirect(url_for('iam.policies'))
    
    return render_template('Seguridad/create_policy.html')

@bp.route('/iam/user/<username>/access-keys')
def user_access_keys(username):
    """Listar access keys de un usuario"""
    try:
        iam = get_aws_client('iam')
        access_keys = iam.list_access_keys(UserName=username)
        key_list = []
        for key in access_keys['AccessKeyMetadata']:
            key_list.append({
                'access_key_id': key['AccessKeyId'],
                'status': key['Status'],
                'create_date': key['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'username': username
            })
        return render_template('Seguridad/user_access_keys.html', access_keys=key_list, username=username)
    except Exception as e:
        flash(f'Error obteniendo access keys: {str(e)}', 'error')
        return render_template('Seguridad/user_access_keys.html', access_keys=[], username=username)

@bp.route('/iam/user/<username>/access-key/create', methods=['POST'])
def create_access_key(username):
    """Crear una nueva access key para un usuario"""
    try:
        iam = get_aws_client('iam')
        
        response = iam.create_access_key(UserName=username)
        access_key = response['AccessKey']
        
        flash(f'Access Key creada para usuario "{username}". Guárdala ahora: {access_key["AccessKeyId"]}', 'success')
        return redirect(url_for('iam.user_access_keys', username=username))
    except Exception as e:
        flash(f'Error creando access key: {str(e)}', 'error')
        return redirect(url_for('iam.user_access_keys', username=username))

@bp.route('/iam/user/<username>/access-key/<access_key_id>/delete', methods=['POST'])
def delete_access_key(username, access_key_id):
    """Eliminar una access key"""
    try:
        iam = get_aws_client('iam')

        iam.delete_access_key(UserName=username, AccessKeyId=access_key_id)

        flash(f'Access Key {access_key_id} eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando access key: {str(e)}', 'error')

    return redirect(url_for('iam.user_access_keys', username=username))

@bp.route('/iam/user/<username>/policies')
def user_policies(username):
    """Listar policies adjuntas a un usuario"""
    try:
        iam = get_aws_client('iam')

        # Obtener policies adjuntas directamente
        attached_policies = iam.list_attached_user_policies(UserName=username)
        attached_list = []
        for policy in attached_policies['AttachedPolicies']:
            attached_list.append({
                'name': policy['PolicyName'],
                'arn': policy['PolicyArn'],
                'type': 'Attached'
            })

        # Obtener policies inline
        inline_policies = iam.list_user_policies(UserName=username)
        for policy_name in inline_policies['PolicyNames']:
            attached_list.append({
                'name': policy_name,
                'arn': f'inline:{policy_name}',
                'type': 'Inline'
            })

        return render_template('Seguridad/user_policies.html', policies=attached_list, username=username)
    except Exception as e:
        flash(f'Error obteniendo policies del usuario: {str(e)}', 'error')
        return render_template('Seguridad/user_policies.html', policies=[], username=username)

@bp.route('/iam/user/<username>/policy/attach', methods=['GET', 'POST'])
def attach_user_policy(username):
    """Adjuntar una policy a un usuario"""
    if request.method == 'POST':
        try:
            iam = get_aws_client('iam')
            policy_arn = request.form.get('policy_arn')

            iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)

            flash(f'Policy adjuntada exitosamente al usuario "{username}"', 'success')
            return redirect(url_for('iam.user_policies', username=username))
        except Exception as e:
            flash(f'Error adjuntando policy: {str(e)}', 'error')
            return redirect(url_for('iam.user_policies', username=username))

    # GET: Mostrar formulario
    try:
        iam = get_aws_client('iam')
        policies = iam.list_policies(Scope='All')
        policy_list = []
        for policy in policies['Policies']:
            policy_list.append({
                'name': policy['PolicyName'],
                'arn': policy['Arn']
            })
        return render_template('Seguridad/attach_user_policy.html', policies=policy_list, username=username)
    except Exception as e:
        flash(f'Error obteniendo policies: {str(e)}', 'error')
        return render_template('Seguridad/attach_user_policy.html', policies=[], username=username)

@bp.route('/iam/user/<username>/policy/<policy_arn>/detach', methods=['POST'])
def detach_user_policy(username, policy_arn):
    """Desadjuntar una policy de un usuario"""
    try:
        iam = get_aws_client('iam')

        iam.detach_user_policy(UserName=username, PolicyArn=policy_arn)

        flash(f'Policy desadjuntada exitosamente del usuario "{username}"', 'success')
    except Exception as e:
        flash(f'Error desadjuntando policy: {str(e)}', 'error')

    return redirect(url_for('iam.user_policies', username=username))

@bp.route('/iam/role/<role_name>/policies')
def role_policies(role_name):
    """Listar policies adjuntas a un rol"""
    try:
        iam = get_aws_client('iam')

        # Obtener policies adjuntas
        attached_policies = iam.list_attached_role_policies(RoleName=role_name)
        attached_list = []
        for policy in attached_policies['AttachedPolicies']:
            attached_list.append({
                'name': policy['PolicyName'],
                'arn': policy['PolicyArn'],
                'type': 'Attached'
            })

        # Obtener policies inline
        inline_policies = iam.list_role_policies(RoleName=role_name)
        for policy_name in inline_policies['PolicyNames']:
            attached_list.append({
                'name': policy_name,
                'arn': f'inline:{policy_name}',
                'type': 'Inline'
            })

        return render_template('Seguridad/role_policies.html', policies=attached_list, role_name=role_name)
    except Exception as e:
        flash(f'Error obteniendo policies del rol: {str(e)}', 'error')
        return render_template('Seguridad/role_policies.html', policies=[], role_name=role_name)

@bp.route('/iam/role/<role_name>/policy/attach', methods=['GET', 'POST'])
def attach_role_policy(role_name):
    """Adjuntar una policy a un rol"""
    if request.method == 'POST':
        try:
            iam = get_aws_client('iam')
            policy_arn = request.form.get('policy_arn')

            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

            flash(f'Policy adjuntada exitosamente al rol "{role_name}"', 'success')
            return redirect(url_for('iam.role_policies', role_name=role_name))
        except Exception as e:
            flash(f'Error adjuntando policy: {str(e)}', 'error')
            return redirect(url_for('iam.role_policies', role_name=role_name))

    # GET: Mostrar formulario
    try:
        iam = get_aws_client('iam')
        policies = iam.list_policies(Scope='All')
        policy_list = []
        for policy in policies['Policies']:
            policy_list.append({
                'name': policy['PolicyName'],
                'arn': policy['Arn']
            })
        return render_template('Seguridad/attach_role_policy.html', policies=policy_list, role_name=role_name)
    except Exception as e:
        flash(f'Error obteniendo policies: {str(e)}', 'error')
        return render_template('Seguridad/attach_role_policy.html', policies=[], role_name=role_name)

@bp.route('/iam/role/<role_name>/policy/<policy_arn>/detach', methods=['POST'])
def detach_role_policy(role_name, policy_arn):
    """Desadjuntar una policy de un rol"""
    try:
        iam = get_aws_client('iam')

        iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        flash(f'Policy desadjuntada exitosamente del rol "{role_name}"', 'success')
    except Exception as e:
        flash(f'Error desadjuntando policy: {str(e)}', 'error')

    return redirect(url_for('iam.role_policies', role_name=role_name))