"""
MCP Server para operaciones AWS
Permite que el chat interactúe directamente con AWS mediante herramientas organizadas por categorías
"""
import json
import logging
from typing import Any, Dict, List
import boto3
from dotenv import load_dotenv
import os

# Importar herramientas por categorías
from .Computo.ec2_mcp_tools import EC2MCPTools
from .Computo.lambda_mcp_tools import LambdaMCPTools
from .Computo.batch_mcp_tools import BatchMCPTools
from .Almacenamiento.s3_mcp_tools import S3MCPTools
from .Almacenamiento.ebs_mcp_tools import EBSMCPTools
from .Base_de_Datos.rds_mcp_tools import RDSMCPTools
from .Base_de_Datos.dynamodb_mcp_tools import DynamoDBMCPTools
from .Base_de_Datos.elasticache_mcp_tools import ElastiCacheMCPTools
from .Base_de_Datos.neptune_mcp_tools import NeptuneMCPTools
from .Base_de_Datos.documentdb_mcp_tools import DocumentDBMCPTools
# from .Mensajeria.sns_mcp_tools import SNSMCPTools
# from .Mensajeria.sqs_mcp_tools import SQSMCPTools
from .Mensajeria.kinesis_mcp_tools import KinesisMCPTools
from .Mensajeria.sns_mcp_tools import SNSMCPTools
from .Mensajeria.sqs_mcp_tools import SQSMCPTools
from .Mensajeria.eventbridge_mcp_tools import EventBridgeMCPTools
from .Redes.vpc_mcp_tools import VPCMCPTools
from .Redes.api_gateway_mcp_tools import APIGatewayMCPTools
from .Redes.route53_mcp_tools import Route53MCPTools
from .Redes.cloudfront_mcp_tools import CloudFrontMCPTools
from .Redes.elbv2_mcp_tools import ELBv2MCPTools
from .Seguridad.iam_mcp_tools import IAMMCPTools
from .Seguridad.kms_mcp_tools import KMSMCPTools
from .Seguridad.acm_mcp_tools import AcmMCPTools
from .Seguridad.secretsmanager_mcp_tools import SecretsManagerMCPTools
from .Analytics.athena_mcp_tools import AthenaMCPTools
from .Analytics.glue_mcp_tools import GlueMCPTools
from .Analytics.emr_mcp_tools import EMRMCPTools
from .Contenedores.ecs_mcp_tools import ECS_MCP_TOOLS
from .Contenedores.ecr_mcp_tools import ECRMCPTools
from .Contenedores.eks_mcp_tools import EKSMCPTools
from .ML_AI.sagemaker_mcp_tools import SageMakerMCPTools
from .ML_AI.bedrock_mcp_tools import BedrockMCPTools
from .ML_AI.rekognition_mcp_tools import RekognitionMCPTools
from .ML_AI.polly_mcp_tools import PollyMCPTools
# from .Gestion.autoscaling_mcp_tools import AutoScalingMCPTools
from .Gestion.cost_explorer_mcp_tools import CostExplorerMCPTools
from .Gestion.cloudwatch_mcp_tools import CloudWatchMCPTools
from .Gestion.autoscaling_mcp_tools import AutoScalingMCPTools
from .Gestion.systems_manager_mcp_tools import SystemsManagerMCPTools
from .Gestion.cloudtrail_mcp_tools import CloudTrailMCPTools
from .Integracion.cloudformation_mcp_tools import CloudFormationMCPTools
from .Config.config_mcp_tools import ConfigMCPTools
from .AI_Assistant.ai_assistant_mcp_tools import AIAssistantMCPTools

load_dotenv()

logger = logging.getLogger(__name__)


class AWSMCPServer:
    """Servidor MCP para operaciones AWS organizadas por categorías"""

    def __init__(self):
        # Inicializar instancias de herramientas por categoría
        self.category_tools = {
            "Computo": {
                "ec2": EC2MCPTools(),
                "lambda": LambdaMCPTools(),
                "batch": BatchMCPTools(),
            },
            "Almacenamiento": {
                "s3": S3MCPTools(),
                "ebs": EBSMCPTools(),
            },
            "Base_de_Datos": {
                "rds": RDSMCPTools(),
                "dynamodb": DynamoDBMCPTools(),
                "elasticache": ElastiCacheMCPTools(),
                "neptune": NeptuneMCPTools(),
                "documentdb": DocumentDBMCPTools(),
            },
            "Mensajeria": {
                "kinesis": KinesisMCPTools(),
                "sns": SNSMCPTools(),
                "sqs": SQSMCPTools(),
                "eventbridge": EventBridgeMCPTools(),
            },
            "Redes": {
                "vpc": VPCMCPTools(),
                "api_gateway": APIGatewayMCPTools(),
                "route53": Route53MCPTools(),
                "cloudfront": CloudFrontMCPTools(),
                "elbv2": ELBv2MCPTools(),
            },
            "Seguridad": {
                "iam": IAMMCPTools(),
                "kms": KMSMCPTools(),
                "acm": AcmMCPTools(),
                "secretsmanager": SecretsManagerMCPTools(),
            },
            "Analytics": {
                "athena": AthenaMCPTools(),
                "glue": GlueMCPTools(),
                "emr": EMRMCPTools(),
            },
            "Integracion": {
                "cloudformation": CloudFormationMCPTools(),
                # TODO: Implementar API Gateway, Step Functions
            },
            "Contenedores": {
                "ecs": ECS_MCP_TOOLS,
                "ecr": ECRMCPTools(),
                "eks": EKSMCPTools(),
            },
            "ML_AI": {
                "sagemaker": SageMakerMCPTools(),
                "bedrock": BedrockMCPTools(),
                "rekognition": RekognitionMCPTools(),
                "polly": PollyMCPTools(),
            },
            "Gestion": {
                "cloudwatch": CloudWatchMCPTools(),
                "cost_explorer": CostExplorerMCPTools(),
                "autoscaling": AutoScalingMCPTools(),
                "systems_manager": SystemsManagerMCPTools(),
                "cloudtrail": CloudTrailMCPTools(),
            },
            "Config": {
                "config": ConfigMCPTools(),
            },
            "AI_Assistant": {
                "ai_assistant": AIAssistantMCPTools(),
            }
        }

        self.tools = self._register_tools()

    def _register_tools(self) -> List[Dict[str, Any]]:
        """Registra todas las herramientas disponibles organizadas por categorías"""
        tools = []

        # Registrar herramientas de cada categoría
        for category, services in self.category_tools.items():
            for service_name, service_instance in services.items():
                if hasattr(service_instance, "get_tools"):
                    # Es una instancia de clase con método get_tools()
                    category_tools = service_instance.get_tools()
                    tools.extend(category_tools)
                elif isinstance(service_instance, dict):
                    # Es un diccionario de herramientas directamente
                    for tool_name, tool_info in service_instance.items():
                        if isinstance(tool_info, dict) and 'function' in tool_info:
                            # Convertir el formato del diccionario al formato esperado
                            tool = {
                                'name': tool_name,
                                'description': tool_info.get('description', ''),
                                'parameters': tool_info.get('parameters', {}),
                                'function': tool_info['function']
                            }
                            tools.append(tool)

        return tools

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles"""
        return self.tools
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Alias de get_tools() para compatibilidad"""
        return self.get_tools()

    def _convert_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte parámetros de Gemini a tipos Python nativos (recursivamente)"""
        def convert_value(value):
            # Manejar valores None
            if value is None:
                return None
            
            # Convertir floats enteros a int
            if isinstance(value, float) and value.is_integer():
                return int(value)
            
            # Procesar listas
            elif isinstance(value, list):
                result = []
                for item in value:
                    # Si el item es una lista pero debería ser un dict (como en filtros AWS)
                    # Verificar si es una lista de dos elementos que representa un key-value
                    if isinstance(item, list) and len(item) == 2:
                        # Podría ser un filtro mal formado, intentar detectar el patrón
                        # Si contiene strings que parecen nombres de keys de AWS
                        if isinstance(item[0], str) and isinstance(item[1], str):
                            # Podría ser ['Name', 'Values'] en lugar de {'Name': ..., 'Values': ...}
                            # Por ahora, convertir recursivamente
                            result.append(convert_value(item))
                        else:
                            result.append(convert_value(item))
                    else:
                        result.append(convert_value(item))
                return result
            
            # Procesar diccionarios
            elif isinstance(value, dict):
                return {str(key): convert_value(val) for key, val in value.items()}
            
            # Otros tipos, devolver tal cual
            else:
                return value
        
        converted = convert_value(params)
        logger.debug(f"Converted params: {converted}")
        return converted

    def _fix_aws_filters(self, params: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """
        Corrige filtros y parámetros mal formados que vienen de Gemini.
        Los filtros de AWS deben ser: [{'Name': 'xxx', 'Values': ['yyy']}]
        Pero Gemini a veces los envía como: [['Values', 'Name'], ...]
        """
        # Corregir el parámetro 'owners' si viene mal formado
        if 'owners' in params:
            if isinstance(params['owners'], dict):
                # Si es un diccionario, intentar extraer el valor correcto
                # o usar valor por defecto
                logger.warning(f"'owners' mal formado: {params['owners']}")
                params['owners'] = ['amazon']  # Valor por defecto
            elif not isinstance(params['owners'], list):
                # Si no es una lista, convertirlo
                params['owners'] = [str(params['owners'])]
        
        # Corregir filtros
        if 'filters' in params and isinstance(params['filters'], list):
            fixed_filters = []
            for f in params['filters']:
                # Si es una lista en lugar de un dict, es un filtro mal formado
                if isinstance(f, list):
                    # Ignorar filtros mal formados
                    logger.warning(f"Filtro mal formado ignorado: {f}")
                    continue
                # Si es un dict válido, mantenerlo
                elif isinstance(f, dict) and 'Name' in f and 'Values' in f:
                    fixed_filters.append(f)
                else:
                    logger.warning(f"Filtro con formato incorrecto ignorado: {f}")
            
            # Si no quedaron filtros válidos, usar valores por defecto según la herramienta
            if not fixed_filters:
                params.pop('filters', None)
                logger.info(f"Filtros eliminados para {tool_name}, sin filtros válidos")
                
                # Para list_amis, agregar filtros por defecto si se está buscando Linux o Amazon
                if tool_name == 'ec2_list_amis':
                    # Si se especificó 'owners' como amazon, agregar filtro básico
                    if params.get('owners') == ['amazon']:
                        params['filters'] = [
                            {'Name': 'state', 'Values': ['available']},
                            {'Name': 'architecture', 'Values': ['x86_64']}
                        ]
                        logger.info("Filtros por defecto aplicados para AMIs de Amazon")
            else:
                params['filters'] = fixed_filters
        
        return params

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica con los parámetros dados"""
        try:
            # Convertir parámetros primero
            converted_params = self._convert_params(parameters)
            
            # Corregir filtros de AWS si es necesario
            converted_params = self._fix_aws_filters(converted_params, tool_name)
            
            # Log de parámetros para debugging
            logger.info(f"Ejecutando herramienta: {tool_name} con parámetros: {converted_params}")

            # Buscar la herramienta en self.tools primero (para herramientas con funciones directas)
            for tool in self.tools:
                if tool['name'] == tool_name:
                    if 'function' in tool:
                        # Desempaquetar parámetros usando **kwargs
                        return tool['function'](**converted_params)
                    break

            # Si no se encontró, buscar en las instancias de servicio que tienen execute_tool
            for category, services in self.category_tools.items():
                for service_name, service_instance in services.items():
                    if hasattr(service_instance, "execute_tool"):
                        try:
                            result = service_instance.execute_tool(tool_name, converted_params)
                            if result.get('success') != False or 'error' not in result:
                                return result
                        except Exception:
                            continue  # Intentar con el siguiente servicio

            # Si no se encontró la herramienta
            return {
                "error": f"Tool '{tool_name}' not found in any service category",
                "available_tools": [tool["name"] for tool in self.tools]
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            import traceback
            return {"error": f"Error executing tool: {str(e)}", "traceback": traceback.format_exc()}


# Singleton
_mcp_server = None

def get_mcp_server() -> AWSMCPServer:
    """Obtiene la instancia del servidor MCP"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = AWSMCPServer()
    return _mcp_server
