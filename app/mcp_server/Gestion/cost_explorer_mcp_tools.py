from typing import Dict, Any, List
import boto3
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CostExplorerMCPTools:
    """Herramientas MCP para AWS Cost Explorer"""

    def __init__(self):
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    def get_cost_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene pronóstico de costos de AWS"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1

            response = ce.get_cost_forecast(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY',
                PredictionIntervalLevel=params.get('prediction_interval_level', 80)
            )

            forecast = []
            for result in response['ForecastResultsByTime']:
                forecast.append({
                    'period': f"{result['TimePeriod']['Start']} - {result['TimePeriod']['End']}",
                    'amount': result['MeanValue'],
                    'unit': result['Unit'],
                    'prediction_interval_lower': result.get('PredictionIntervalLowerBound'),
                    'prediction_interval_upper': result.get('PredictionIntervalUpperBound')
                })

            return {
                'forecast': forecast,
                'prediction_interval_level': params.get('prediction_interval_level', 80)
            }

        except Exception as e:
            logger.exception(f"Error obteniendo pronóstico de costos: {e}")
            return {
                'error': str(e),
                'forecast': [],
                'message': f"Error al obtener pronóstico de costos: {str(e)}"
            }

    def get_cost_categories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene categorías de costos por servicio"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1

            response = ce.get_cost_and_usage_with_resources(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )

            categories = []
            max_results = params.get('max_results', 10)

            for group in response['ResultsByTime'][0]['Groups'][:max_results]:
                categories.append({
                    'service': group['Keys'][0],
                    'amount': group['Metrics']['UnblendedCost']['Amount'],
                    'unit': group['Metrics']['UnblendedCost']['Unit']
                })

            # Ordenar por monto descendente
            categories.sort(key=lambda x: float(x['amount']), reverse=True)

            return {
                'categories': categories,
                'total_categories': len(categories)
            }

        except Exception as e:
            logger.exception(f"Error obteniendo categorías de costos: {e}")
            return {
                'error': str(e),
                'categories': [],
                'message': f"Error al obtener categorías de costos: {str(e)}"
            }

    def get_savings_plans_utilization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene utilización de Savings Plans"""
        try:
            ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer solo en us-east-1

            response = ce.get_savings_plans_utilization(
                TimePeriod={
                    'Start': params['start_date'],
                    'End': params['end_date']
                }
            )

            savings_plans = []
            for sp in response['SavingsPlansUtilizationsByTime']:
                savings_plans.append({
                    'period': f"{sp['TimePeriod']['Start']} - {sp['TimePeriod']['End']}",
                    'total_commitment': sp['Total']['TotalCommitment'],
                    'used_commitment': sp['Total']['UsedCommitment'],
                    'unused_commitment': sp['Total']['UnusedCommitment'],
                    'utilization_percentage': sp['Total']['UtilizationPercentage'],
                    'unit': sp['Total']['Unit']
                })

            return {
                'savings_plans': savings_plans,
                'total_periods': len(savings_plans)
            }

        except Exception as e:
            logger.exception(f"Error obteniendo utilización de Savings Plans: {e}")
            return {
                'error': str(e),
                'savings_plans': [],
                'message': f"Error al obtener utilización de Savings Plans: {str(e)}"
            }

# Instancia global de las herramientas
cost_explorer_tools = CostExplorerMCPTools()

# Definición de herramientas MCP para Cost Explorer
COST_EXPLORER_MCP_TOOLS = [
    {
        "name": "get_cost_forecast",
        "description": "Obtiene pronóstico de costos de AWS para un período futuro",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Fecha inicio del pronóstico (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Fecha fin del pronóstico (YYYY-MM-DD)"
                },
                "prediction_interval_level": {
                    "type": "integer",
                    "description": "Nivel de intervalo de predicción (por defecto: 80)",
                    "default": 80,
                    "minimum": 50,
                    "maximum": 99
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_cost_categories",
        "description": "Obtiene desglose de costos por categoría/servicio",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Fecha inicio del análisis (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Fecha fin del análisis (YYYY-MM-DD)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de categorías a retornar (por defecto: 10)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["start_date", "end_date"]
        }
    },
    {
        "name": "get_savings_plans_utilization",
        "description": "Obtiene información de utilización de Savings Plans",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Fecha inicio del análisis (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Fecha fin del análisis (YYYY-MM-DD)"
                }
            },
            "required": ["start_date", "end_date"]
        }
    }
]