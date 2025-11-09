from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('dynamodb', __name__)

@bp.route('/')
def index():
    return render_template('Base_de_Datos/dynamodb/index.html')

@bp.route('/tables')
def tables():
    try:
        dynamodb = get_aws_client('dynamodb')
        tables = dynamodb.list_tables()
        table_list = []
        for table_name in tables['TableNames']:
            table_info = dynamodb.describe_table(TableName=table_name)
            table = table_info['Table']
            table_list.append({
                'name': table['TableName'],
                'status': table['TableStatus'],
                'item_count': table.get('ItemCount', 0),
                'size_bytes': table.get('TableSizeBytes', 0),
                'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED'),
                'created': table.get('CreationDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if table.get('CreationDateTime') else 'N/A'
            })
        return render_template('Base_de_Datos/dynamodb/tables.html', tables=table_list)
    except Exception as e:
        flash(f'Error obteniendo tablas DynamoDB: {str(e)}', 'error')
        return render_template('Base_de_Datos/dynamodb/tables.html', tables=[])

@bp.route('/table/<table_name>')
def table_detail(table_name):
    """Detalle de una tabla DynamoDB"""
    try:
        dynamodb = get_aws_client('dynamodb')
        table_info = dynamodb.describe_table(TableName=table_name)
        table = table_info['Table']
        
        # Obtener schema de claves
        key_schema = []
        for key in table['KeySchema']:
            key_type = 'Partition Key' if key['KeyType'] == 'HASH' else 'Sort Key'
            key_schema.append({
                'name': key['AttributeName'],
                'type': key_type
            })
        
        # Obtener atributos
        attributes = []
        for attr in table.get('AttributeDefinitions', []):
            attr_type = {'S': 'String', 'N': 'Number', 'B': 'Binary'}.get(attr['AttributeType'], attr['AttributeType'])
            attributes.append({
                'name': attr['AttributeName'],
                'type': attr_type
            })
        
        table_data = {
            'name': table['TableName'],
            'status': table['TableStatus'],
            'item_count': table.get('ItemCount', 0),
            'size_bytes': table.get('TableSizeBytes', 0),
            'billing_mode': table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED'),
            'key_schema': key_schema,
            'attributes': attributes,
            'stream_enabled': table.get('StreamSpecification', {}).get('StreamEnabled', False),
            'created': table.get('CreationDateTime', '').strftime('%Y-%m-%d %H:%M:%S') if table.get('CreationDateTime') else 'N/A'
        }
        
        return render_template('Base_de_Datos/dynamodb/table_detail.html', table=table_data)
    except Exception as e:
        flash(f'Error obteniendo detalles de tabla: {str(e)}', 'error')
        return redirect(url_for('dynamodb.tables'))

@bp.route('/table/create', methods=['POST'])
def create_table():
    """Crea una tabla DynamoDB"""
    try:
        dynamodb = get_aws_client('dynamodb')
        
        table_name = request.form.get('table_name')
        partition_key = request.form.get('partition_key')
        partition_key_type = request.form.get('partition_key_type', 'S')
        sort_key = request.form.get('sort_key')
        sort_key_type = request.form.get('sort_key_type', 'S')
        billing_mode = request.form.get('billing_mode', 'PAY_PER_REQUEST')
        
        # Schema de claves
        key_schema = [
            {'AttributeName': partition_key, 'KeyType': 'HASH'}
        ]
        
        attribute_definitions = [
            {'AttributeName': partition_key, 'AttributeType': partition_key_type}
        ]
        
        # Sort key opcional
        if sort_key:
            key_schema.append({'AttributeName': sort_key, 'KeyType': 'RANGE'})
            attribute_definitions.append({'AttributeName': sort_key, 'AttributeType': sort_key_type})
        
        # Parámetros de creación
        create_params = {
            'TableName': table_name,
            'KeySchema': key_schema,
            'AttributeDefinitions': attribute_definitions,
            'BillingMode': billing_mode
        }
        
        # Si es PROVISIONED, agregar capacidad
        if billing_mode == 'PROVISIONED':
            read_capacity = int(request.form.get('read_capacity', 5))
            write_capacity = int(request.form.get('write_capacity', 5))
            create_params['ProvisionedThroughput'] = {
                'ReadCapacityUnits': read_capacity,
                'WriteCapacityUnits': write_capacity
            }
        
        dynamodb.create_table(**create_params)
        flash(f'Tabla {table_name} creada exitosamente', 'success')
    except Exception as e:
        flash(f'Error creando tabla: {str(e)}', 'error')
    
    return redirect(url_for('dynamodb.tables'))

@bp.route('/table/<table_name>/delete', methods=['POST'])
def delete_table(table_name):
    """Elimina una tabla DynamoDB"""
    try:
        dynamodb = get_aws_client('dynamodb')
        dynamodb.delete_table(TableName=table_name)
        flash(f'Tabla {table_name} eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando tabla: {str(e)}', 'error')
    
    return redirect(url_for('dynamodb.tables'))

@bp.route('/table/<table_name>/items')
def table_items(table_name):
    """Lista items de una tabla (scan limitado)"""
    try:
        dynamodb = get_aws_client('dynamodb')
        response = dynamodb.scan(
            TableName=table_name,
            Limit=50  # Limitar a 50 items
        )
        
        items = response.get('Items', [])
        return render_template('Base_de_Datos/dynamodb/items.html', 
                             table_name=table_name, 
                             items=items,
                             count=len(items))
    except Exception as e:
        flash(f'Error obteniendo items: {str(e)}', 'error')
        return redirect(url_for('dynamodb.tables'))

@bp.route('/table/<table_name>/update', methods=['GET', 'POST'])
def update_table(table_name):
    """Actualiza configuración de tabla (capacidad, streams)"""
    try:
        dynamodb = get_aws_client('dynamodb')
        table_info = dynamodb.describe_table(TableName=table_name)
        table = table_info['Table']
        
        if request.method == 'POST':
            # Actualizar capacidad si es PROVISIONED
            billing_mode = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
            if billing_mode == 'PROVISIONED':
                read_capacity = int(request.form.get('read_capacity'))
                write_capacity = int(request.form.get('write_capacity'))
                
                dynamodb.update_table(
                    TableName=table_name,
                    ProvisionedThroughput={
                        'ReadCapacityUnits': read_capacity,
                        'WriteCapacityUnits': write_capacity
                    }
                )
            
            # Habilitar/deshabilitar streams
            enable_streams = request.form.get('enable_streams') == 'on'
            if enable_streams:
                stream_view_type = request.form.get('stream_view_type', 'NEW_AND_OLD_IMAGES')
                dynamodb.update_table(
                    TableName=table_name,
                    StreamSpecification={
                        'StreamEnabled': True,
                        'StreamViewType': stream_view_type
                    }
                )
            else:
                dynamodb.update_table(
                    TableName=table_name,
                    StreamSpecification={
                        'StreamEnabled': False
                    }
                )
            
            flash(f'Tabla {table_name} actualizada exitosamente', 'success')
            return redirect(url_for('dynamodb.table_detail', table_name=table_name))
        
        # Datos para el formulario
        current_read_capacity = table.get('ProvisionedThroughput', {}).get('ReadCapacityUnits', 0)
        current_write_capacity = table.get('ProvisionedThroughput', {}).get('WriteCapacityUnits', 0)
        stream_enabled = table.get('StreamSpecification', {}).get('StreamEnabled', False)
        stream_view_type = table.get('StreamSpecification', {}).get('StreamViewType', 'NEW_AND_OLD_IMAGES')
        
        return render_template('Base_de_Datos/dynamodb/update_table.html',
                             table_name=table_name,
                             billing_mode=billing_mode,
                             current_read_capacity=current_read_capacity,
                             current_write_capacity=current_write_capacity,
                             stream_enabled=stream_enabled,
                             stream_view_type=stream_view_type)
                             
    except Exception as e:
        flash(f'Error actualizando tabla: {str(e)}', 'error')
        return redirect(url_for('dynamodb.table_detail', table_name=table_name))

@bp.route('/table/<table_name>/scan', methods=['GET', 'POST'])
def scan_items(table_name):
    """Escanea items de una tabla con filtros opcionales"""
    try:
        dynamodb = get_aws_client('dynamodb')
        
        # Parámetros de scan
        scan_params = {'TableName': table_name}
        
        # Filtro opcional
        if request.method == 'POST':
            filter_expression = request.form.get('filter_expression')
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            
            # Valores de expresión si hay placeholders
            expression_values = request.form.get('expression_values')
            if expression_values:
                try:
                    scan_params['ExpressionAttributeValues'] = json.loads(expression_values)
                except json.JSONDecodeError:
                    flash('Error en formato JSON de valores de expresión', 'error')
        
        # Ejecutar scan
        response = dynamodb.scan(**scan_params)
        items = response.get('Items', [])
        count = response.get('Count', 0)
        
        return render_template('Base_de_Datos/dynamodb/scan_items.html',
                             table_name=table_name,
                             items=items,
                             count=count,
                             filter_expression=request.form.get('filter_expression', ''),
                             expression_values=request.form.get('expression_values', ''))
                             
    except Exception as e:
        flash(f'Error escaneando items: {str(e)}', 'error')
        return redirect(url_for('dynamodb.table_detail', table_name=table_name))

@bp.route('/table/<table_name>/put_item', methods=['GET', 'POST'])
def put_item(table_name):
    """Inserta o actualiza un item en la tabla"""
    try:
        dynamodb = get_aws_client('dynamodb')
        
        if request.method == 'POST':
            item_data = request.form.get('item_data')
            if not item_data:
                flash('Datos del item requeridos', 'error')
                return redirect(request.url)
            
            try:
                item = json.loads(item_data)
                dynamodb.put_item(
                    TableName=table_name,
                    Item=item
                )
                flash('Item insertado/actualizado exitosamente', 'success')
                return redirect(url_for('dynamodb.table_items', table_name=table_name))
            except json.JSONDecodeError:
                flash('Error en formato JSON del item', 'error')
            except Exception as e:
                flash(f'Error insertando item: {str(e)}', 'error')
        
        return render_template('Base_de_Datos/dynamodb/put_item.html', table_name=table_name)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('dynamodb.table_detail', table_name=table_name))

@bp.route('/table/<table_name>/delete_item', methods=['POST'])
def delete_item(table_name):
    """Elimina un item de la tabla"""
    try:
        dynamodb = get_aws_client('dynamodb')
        
        key_data = request.form.get('key_data')
        if not key_data:
            flash('Datos de clave requeridos', 'error')
            return redirect(url_for('dynamodb.table_items', table_name=table_name))
        
        try:
            key = json.loads(key_data)
            dynamodb.delete_item(
                TableName=table_name,
                Key=key
            )
            flash('Item eliminado exitosamente', 'success')
        except json.JSONDecodeError:
            flash('Error en formato JSON de la clave', 'error')
        except Exception as e:
            flash(f'Error eliminando item: {str(e)}', 'error')
            
        return redirect(url_for('dynamodb.table_items', table_name=table_name))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('dynamodb.table_detail', table_name=table_name))

@bp.route('/table/<table_name>/query', methods=['GET', 'POST'])
def query_items(table_name):
    """Consulta items usando clave de partición y opcionalmente clave de ordenamiento"""
    try:
        dynamodb = get_aws_client('dynamodb')
        table_info = dynamodb.describe_table(TableName=table_name)
        table = table_info['Table']
        
        # Obtener esquema de claves
        partition_key = None
        sort_key = None
        for key in table['KeySchema']:
            if key['KeyType'] == 'HASH':
                partition_key = key['AttributeName']
            elif key['KeyType'] == 'RANGE':
                sort_key = key['AttributeName']
        
        if request.method == 'POST':
            # Construir expresión de clave
            key_condition = request.form.get('key_condition')
            if not key_condition:
                flash('Expresión de clave requerida', 'error')
                return redirect(request.url)
            
            query_params = {
                'TableName': table_name,
                'KeyConditionExpression': key_condition
            }
            
            # Valores de expresión
            expression_values = request.form.get('expression_values')
            if expression_values:
                try:
                    query_params['ExpressionAttributeValues'] = json.loads(expression_values)
                except json.JSONDecodeError:
                    flash('Error en formato JSON de valores de expresión', 'error')
                    return redirect(request.url)
            
            # Filtro opcional
            filter_expression = request.form.get('filter_expression')
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            
            # Ejecutar query
            response = dynamodb.query(**query_params)
            items = response.get('Items', [])
            count = response.get('Count', 0)
            
            return render_template('Base_de_Datos/dynamodb/query_items.html',
                                 table_name=table_name,
                                 partition_key=partition_key,
                                 sort_key=sort_key,
                                 items=items,
                                 count=count,
                                 key_condition=key_condition,
                                 expression_values=expression_values,
                                 filter_expression=filter_expression)
        
        return render_template('Base_de_Datos/dynamodb/query_items.html',
                             table_name=table_name,
                             partition_key=partition_key,
                             sort_key=sort_key)
                             
    except Exception as e:
        flash(f'Error consultando items: {str(e)}', 'error')
        return redirect(url_for('dynamodb.table_detail', table_name=table_name))