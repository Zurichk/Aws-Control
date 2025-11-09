from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('rds', __name__)

@bp.route('/rds')
def index():
    return render_template('Base_de_Datos/rds/index.html')

@bp.route('/rds/instances')
def instances():
    try:
        rds = get_aws_client('rds')
        instances = rds.describe_db_instances()
        instance_list = []
        for instance in instances['DBInstances']:
            instance_list.append({
                'id': instance['DBInstanceIdentifier'],
                'status': instance['DBInstanceStatus'],
                'engine': instance['Engine'],
                'engine_version': instance['EngineVersion'],
                'instance_class': instance.get('DBInstanceClass', 'N/A'),
                'storage': instance.get('AllocatedStorage', 0),
                'endpoint': instance.get('Endpoint', {}).get('Address', 'N/A'),
                'port': instance.get('Endpoint', {}).get('Port', 'N/A'),
                'multi_az': instance.get('MultiAZ', False),
                'publicly_accessible': instance.get('PubliclyAccessible', False),
                'created': str(instance.get('InstanceCreateTime', 'N/A'))
            })
        return render_template('Base_de_Datos/rds/instances.html', instances=instance_list)
    except Exception as e:
        flash(f'Error obteniendo instancias RDS: {str(e)}', 'error')
        return render_template('Base_de_Datos/rds/instances.html', instances=[])

@bp.route('/rds/clusters')
def clusters():
    """Lista clusters Aurora"""
    try:
        rds = get_aws_client('rds')
        clusters = rds.describe_db_clusters()
        cluster_list = []
        for cluster in clusters['DBClusters']:
            cluster_list.append({
                'id': cluster['DBClusterIdentifier'],
                'engine': cluster['Engine'],
                'engine_version': cluster.get('EngineVersion', 'N/A'),
                'status': cluster['Status'],
                'endpoint': cluster.get('Endpoint', 'N/A'),
                'reader_endpoint': cluster.get('ReaderEndpoint', 'N/A'),
                'multi_az': cluster.get('MultiAZ', False),
                'members': len(cluster.get('DBClusterMembers', [])),
                'created': str(cluster.get('ClusterCreateTime', 'N/A'))
            })
        return render_template('Base_de_Datos/rds/clusters.html', clusters=cluster_list)
    except Exception as e:
        flash(f'Error obteniendo clusters Aurora: {str(e)}', 'error')
        return render_template('Base_de_Datos/rds/clusters.html', clusters=[])

@bp.route('/rds/snapshots')
def snapshots():
    """Lista snapshots de RDS"""
    try:
        rds = get_aws_client('rds')
        snapshots = rds.describe_db_snapshots()
        snapshot_list = []
        for snapshot in snapshots['DBSnapshots']:
            snapshot_list.append({
                'id': snapshot['DBSnapshotIdentifier'],
                'db_instance': snapshot.get('DBInstanceIdentifier', 'N/A'),
                'status': snapshot['Status'],
                'engine': snapshot['Engine'],
                'allocated_storage': snapshot.get('AllocatedStorage', 0),
                'snapshot_type': snapshot.get('SnapshotType', 'N/A'),
                'created': str(snapshot.get('SnapshotCreateTime', 'N/A'))
            })
        return render_template('Base_de_Datos/rds/snapshots.html', snapshots=snapshot_list)
    except Exception as e:
        flash(f'Error obteniendo snapshots: {str(e)}', 'error')
        return render_template('Base_de_Datos/rds/snapshots.html', snapshots=[])

@bp.route('/rds/instance/<instance_id>/delete', methods=['POST'])
def delete_instance(instance_id):
    """Elimina una instancia RDS"""
    try:
        rds = get_aws_client('rds')
        skip_snapshot = request.form.get('skip_snapshot', 'false').lower() == 'true'
        
        if skip_snapshot:
            rds.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=True
            )
            flash(f'Instancia RDS {instance_id} eliminada exitosamente (sin snapshot final)', 'success')
        else:
            snapshot_id = f"{instance_id}-final-snapshot"
            rds.delete_db_instance(
                DBInstanceIdentifier=instance_id,
                SkipFinalSnapshot=False,
                FinalDBSnapshotIdentifier=snapshot_id
            )
            flash(f'Instancia RDS {instance_id} eliminada con snapshot final: {snapshot_id}', 'success')
    except Exception as e:
        flash(f'Error eliminando instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))

@bp.route('/rds/instance/create', methods=['POST'])
def create_instance():
    """Crea una instancia RDS"""
    try:
        rds = get_aws_client('rds')
        
        db_identifier = request.form.get('db_identifier')
        engine = request.form.get('engine', 'mysql')
        instance_class = request.form.get('instance_class', 'db.t3.micro')
        allocated_storage = int(request.form.get('allocated_storage', 20))
        master_username = request.form.get('master_username', 'admin')
        master_password = request.form.get('master_password')
        
        rds.create_db_instance(
            DBInstanceIdentifier=db_identifier,
            Engine=engine,
            DBInstanceClass=instance_class,
            AllocatedStorage=allocated_storage,
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            BackupRetentionPeriod=7,
            StorageEncrypted=True
        )
        
        flash(f'Instancia RDS {db_identifier} creada exitosamente', 'success')
    except Exception as e:
        flash(f'Error creando instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))

@bp.route('/api/rds/instances')
def api_instances():
    """API endpoint para obtener instancias RDS disponibles"""
    try:
        rds = get_aws_client('rds')
        instances = rds.describe_db_instances()
        instance_list = []
        for instance in instances['DBInstances']:
            instance_list.append({
                'id': instance['DBInstanceIdentifier'],
                'engine': instance['Engine'],
                'instance_class': instance.get('DBInstanceClass', 'N/A'),
                'status': instance['DBInstanceStatus']
            })
        return jsonify({'instances': instance_list})
    except Exception as e:
        return jsonify({'error': str(e), 'instances': []}), 500

@bp.route('/rds/snapshot/create', methods=['POST'])
def create_snapshot():
    """Crea un snapshot manual"""
    try:
        rds = get_aws_client('rds')
        
        instance_id = request.form.get('instance_id')
        snapshot_id = request.form.get('snapshot_id')
        
        rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=instance_id
        )
        
        flash(f'Snapshot {snapshot_id} creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error creando snapshot: {str(e)}', 'error')
    
    return redirect(url_for('rds.snapshots'))

@bp.route('/rds/snapshot/<snapshot_id>/delete', methods=['POST'])
def delete_snapshot(snapshot_id):
    """Elimina un snapshot"""
    try:
        rds = get_aws_client('rds')
        rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
        flash(f'Snapshot {snapshot_id} eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando snapshot: {str(e)}', 'error')
    
    return redirect(url_for('rds.snapshots'))

@bp.route('/rds/instance/<instance_id>/modify', methods=['GET', 'POST'])
def modify_instance(instance_id):
    """Modifica una instancia RDS (instance class, storage)"""
    if request.method == 'GET':
        try:
            rds = get_aws_client('rds')
            instance = rds.describe_db_instances(DBInstanceIdentifier=instance_id)['DBInstances'][0]
            return render_template('Base_de_Datos/rds/modify_instance.html', instance=instance)
        except Exception as e:
            flash(f'Error obteniendo instancia: {str(e)}', 'error')
            return redirect(url_for('rds.instances'))
    
    try:
        rds = get_aws_client('rds')
        
        instance_class = request.form.get('instance_class')
        allocated_storage = request.form.get('allocated_storage')
        
        modify_params = {}
        if instance_class:
            modify_params['DBInstanceClass'] = instance_class
        if allocated_storage:
            modify_params['AllocatedStorage'] = int(allocated_storage)
        
        if modify_params:
            rds.modify_db_instance(
                DBInstanceIdentifier=instance_id,
                **modify_params,
                ApplyImmediately=True
            )
            flash(f'Instancia RDS {instance_id} modificada exitosamente', 'success')
        else:
            flash('No se especificaron cambios', 'warning')
            
    except Exception as e:
        flash(f'Error modificando instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))

@bp.route('/rds/instance/<instance_id>/reboot', methods=['POST'])
def reboot_instance(instance_id):
    """Reinicia una instancia RDS"""
    try:
        rds = get_aws_client('rds')
        rds.reboot_db_instance(DBInstanceIdentifier=instance_id)
        flash(f'Instancia RDS {instance_id} reiniciada exitosamente', 'success')
    except Exception as e:
        flash(f'Error reiniciando instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))

@bp.route('/rds/instance/<instance_id>/stop', methods=['POST'])
def stop_instance(instance_id):
    """Detiene una instancia RDS (solo instancias, no clusters)"""
    try:
        rds = get_aws_client('rds')
        rds.stop_db_instance(DBInstanceIdentifier=instance_id)
        flash(f'Instancia RDS {instance_id} detenida exitosamente', 'success')
    except Exception as e:
        flash(f'Error deteniendo instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))

@bp.route('/rds/instance/<instance_id>/start', methods=['POST'])
def start_instance(instance_id):
    """Inicia una instancia RDS detenida"""
    try:
        rds = get_aws_client('rds')
        rds.start_db_instance(DBInstanceIdentifier=instance_id)
        flash(f'Instancia RDS {instance_id} iniciada exitosamente', 'success')
    except Exception as e:
        flash(f'Error iniciando instancia: {str(e)}', 'error')
    
    return redirect(url_for('rds.instances'))