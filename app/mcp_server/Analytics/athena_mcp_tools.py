"""
Herramientas MCP para Amazon Athena
Ejecución de consultas SQL en datos de S3
"""
import boto3
import json
from typing import Dict, Any, List
from ...utils.aws_client import get_aws_client


class AthenaMCPTools:
    """Herramientas MCP para operaciones con Amazon Athena"""

    def list_query_executions(self, max_results: int = 50, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Listar ejecuciones de consultas recientes

        Args:
            max_results: Número máximo de resultados (default: 50)
            region: Región de AWS

        Returns:
            Dict con lista de ejecuciones de consultas
        """
        try:
            athena = get_aws_client('athena', region)
            response = athena.list_query_executions(MaxResults=max_results)

            executions = []
            for execution_id in response.get('QueryExecutionIds', []):
                try:
                    execution_detail = athena.get_query_execution(QueryExecutionId=execution_id)
                    execution = execution_detail['QueryExecution']
                    executions.append({
                        'QueryExecutionId': execution_id,
                        'Query': execution.get('Query', ''),
                        'Status': execution['Status']['State'],
                        'StartTime': execution.get('EngineExecutionTimeInMillis', 0),
                        'Database': execution.get('QueryExecutionContext', {}).get('Database', ''),
                        'WorkGroup': execution.get('WorkGroup', ''),
                        'SubmissionDateTime': execution.get('Status', {}).get('SubmissionDateTime', '').isoformat() if execution.get('Status', {}).get('SubmissionDateTime') else ''
                    })
                except Exception as e:
                    # Skip executions that can't be retrieved
                    continue

            return {
                'success': True,
                'message': f'Encontradas {len(executions)} ejecuciones de consultas',
                'executions': executions,
                'count': len(executions),
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error listando ejecuciones: {str(e)}',
                'region': region
            }

    def start_query_execution(self, query: str, database: str = 'default', workgroup: str = 'primary', region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Iniciar la ejecución de una consulta SQL

        Args:
            query: Consulta SQL a ejecutar
            database: Base de datos/catalog (default: default)
            workgroup: Workgroup de Athena (default: primary)
            region: Región de AWS

        Returns:
            Dict con resultado de la ejecución
        """
        try:
            athena = get_aws_client('athena', region)

            response = athena.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': database
                },
                WorkGroup=workgroup
            )

            execution_id = response['QueryExecutionId']

            return {
                'success': True,
                'message': f'Consulta iniciada exitosamente',
                'execution_id': execution_id,
                'query': query,
                'database': database,
                'workgroup': workgroup,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error iniciando consulta: {str(e)}',
                'query': query,
                'region': region
            }

    def stop_query_execution(self, execution_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Detener una consulta en ejecución

        Args:
            execution_id: ID de la ejecución de consulta
            region: Región de AWS

        Returns:
            Dict con resultado de la operación
        """
        try:
            athena = get_aws_client('athena', region)
            athena.stop_query_execution(QueryExecutionId=execution_id)

            return {
                'success': True,
                'message': f'Consulta {execution_id} detenida exitosamente',
                'execution_id': execution_id,
                'region': region
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deteniendo consulta: {str(e)}',
                'execution_id': execution_id,
                'region': region
            }

    def get_query_results(self, execution_id: str, region: str = 'us-east-1') -> Dict[str, Any]:
        """
        Obtener resultados de una consulta ejecutada

        Args:
            execution_id: ID de la ejecución de consulta
            region: Región de AWS

        Returns:
            Dict con los resultados de la consulta
        """
        try:
            athena = get_aws_client('athena', region)

            # Obtener detalles de la ejecución primero
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

                return {
                    'success': True,
                    'message': f'Resultados obtenidos exitosamente',
                    'execution_id': execution_id,
                    'status': status,
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows),
                    'query': execution.get('Query', ''),
                    'database': execution.get('QueryExecutionContext', {}).get('Database', ''),
                    'region': region
                }

            elif status in ['FAILED', 'CANCELLED']:
                error_message = execution['Status'].get('StateChangeReason', 'Consulta fallida')
                return {
                    'success': False,
                    'message': f'Consulta fallida: {error_message}',
                    'execution_id': execution_id,
                    'status': status,
                    'error': error_message,
                    'region': region
                }

            else:
                return {
                    'success': False,
                    'message': f'Consulta aún en ejecución (estado: {status})',
                    'execution_id': execution_id,
                    'status': status,
                    'region': region
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error obteniendo resultados: {str(e)}',
                'execution_id': execution_id,
                'region': region
            }