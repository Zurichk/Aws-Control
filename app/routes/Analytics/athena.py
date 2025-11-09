from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.utils.aws_client import get_aws_client
import json

bp = Blueprint('athena', __name__)

@bp.route('/')
def index():
    """Página principal de Athena"""
    try:
        athena = get_aws_client('athena')
        # Listar ejecuciones de consultas recientes
        executions = athena.list_query_executions(MaxResults=20)
        execution_list = []

        for execution_id in executions.get('QueryExecutionIds', []):
            execution_detail = athena.get_query_execution(QueryExecutionId=execution_id)
            execution = execution_detail['QueryExecution']
            execution_list.append({
                'QueryExecutionId': execution_id,
                'Query': execution.get('Query', ''),
                'Status': execution['Status']['State'],
                'StartTime': execution.get('EngineExecutionTimeInMillis', 0),
                'Database': execution.get('QueryExecutionContext', {}).get('Database', ''),
                'WorkGroup': execution.get('WorkGroup', ''),
                'SubmissionDateTime': execution.get('Status', {}).get('SubmissionDateTime', '').isoformat() if execution.get('Status', {}).get('SubmissionDateTime') else ''
            })

        return render_template('athena/index.html', executions=execution_list)
    except Exception as e:
        flash(f'Error obteniendo ejecuciones de consultas: {str(e)}', 'error')
        return render_template('athena/index.html', executions=[])

@bp.route('/execute', methods=['GET', 'POST'])
def execute_query():
    """Ejecutar una nueva consulta"""
    if request.method == 'POST':
        query = request.form.get('query')
        database = request.form.get('database', 'default')
        workgroup = request.form.get('workgroup', 'primary')
        region = request.form.get('region', 'us-east-1')

        if not query:
            flash('La consulta SQL es requerida', 'error')
            return redirect(url_for('athena.execute_query'))

        try:
            athena = get_aws_client('athena', region)

            # Iniciar ejecución de consulta
            response = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': database
                },
                WorkGroup=workgroup
            )

            execution_id = response['QueryExecutionId']
            flash(f'Consulta iniciada exitosamente. ID: {execution_id}', 'success')
            return redirect(url_for('athena.query_results', execution_id=execution_id))

        except Exception as e:
            flash(f'Error ejecutando consulta: {str(e)}', 'error')

    return render_template('athena/execute.html')

@bp.route('/results/<execution_id>')
def query_results(execution_id):
    """Mostrar resultados de una consulta"""
    try:
        athena = get_aws_client('athena')

        # Obtener detalles de la ejecución
        execution_detail = athena.get_query_execution(QueryExecutionId=execution_id)
        execution = execution_detail['QueryExecution']

        status = execution['Status']['State']

        if status == 'SUCCEEDED':
            # Obtener resultados
            results_response = athena.get_query_results(QueryExecutionId=execution_id)
            columns = []
            rows = []

            if results_response.get('ResultSet'):
                result_set = results_response['ResultSet']

                # Extraer nombres de columnas
                if result_set.get('ResultSetMetadata', {}).get('ColumnInfo'):
                    columns = [col['Name'] for col in result_set['ResultSetMetadata']['ColumnInfo']]

                # Extraer filas de datos
                if result_set.get('Rows'):
                    for row in result_set['Rows'][1:]:  # Skip header row
                        row_data = []
                        for data in row.get('Data', []):
                            row_data.append(data.get('VarCharValue', ''))
                        rows.append(row_data)

            return render_template('athena/results.html',
                                 execution_id=execution_id,
                                 status=status,
                                 columns=columns,
                                 rows=rows,
                                 query=execution.get('Query', ''),
                                 database=execution.get('QueryExecutionContext', {}).get('Database', ''))

        elif status in ['FAILED', 'CANCELLED']:
            error_message = execution['Status'].get('StateChangeReason', 'Consulta fallida')
            return render_template('athena/results.html',
                                 execution_id=execution_id,
                                 status=status,
                                 error=error_message,
                                 query=execution.get('Query', ''))

        else:
            # Consulta aún en ejecución
            return render_template('athena/results.html',
                                 execution_id=execution_id,
                                 status=status,
                                 query=execution.get('Query', ''))

    except Exception as e:
        flash(f'Error obteniendo resultados: {str(e)}', 'error')
        return redirect(url_for('athena.index'))

@bp.route('/stop/<execution_id>', methods=['POST'])
def stop_query(execution_id):
    """Detener una consulta en ejecución"""
    try:
        athena = get_aws_client('athena')
        athena.stop_query_execution(QueryExecutionId=execution_id)
        flash(f'Consulta {execution_id} detenida exitosamente', 'success')
    except Exception as e:
        flash(f'Error deteniendo consulta: {str(e)}', 'error')

    return redirect(url_for('athena.index'))