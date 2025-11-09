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
from .Almacenamiento.s3_mcp_tools import S3MCPTools
from .Base_de_Datos.rds_mcp_tools import RDSMCPTools
from .Base_de_Datos.dynamodb_mcp_tools import DynamoDBMCPTools
# from .Mensajeria.sns_mcp_tools import SNSMCPTools
# from .Mensajeria.sqs_mcp_tools import SQSMCPTools
from .Mensajeria.kinesis_mcp_tools import KinesisMCPTools
from .Redes.vpc_mcp_tools import VPCMCPTools
from .Redes.api_gateway_mcp_tools import APIGatewayMCPTools
from .Seguridad.iam_mcp_tools import IAMMCPTools
# from .Seguridad.kms_mcp_tools import KMSMCPTools
from .Analytics.athena_mcp_tools import AthenaMCPTools
from .Analytics.glue_mcp_tools import GlueMCPTools
from .Contenedores.ecs_mcp_tools import ECS_MCP_TOOLS
# from .ML_AI.sagemaker_mcp_tools import SageMakerMCPTools
# from .Gestion.autoscaling_mcp_tools import AutoScalingMCPTools
from .Gestion.cloudwatch_mcp_tools import CloudWatchMCPTools
from .Integracion.cloudformation_mcp_tools import CloudFormationMCPTools

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
            },
            "Almacenamiento": {
                "s3": S3MCPTools(),
            },
            "Base_de_Datos": {
                "rds": RDSMCPTools(),
                "dynamodb": DynamoDBMCPTools(),
                # TODO: Implementar Neptune, DocumentDB, ElastiCache
            },
            "Mensajeria": {
                "kinesis": KinesisMCPTools(),
                # TODO: Implementar SNS, SQS
            },
            "Redes": {
                "vpc": VPCMCPTools(),
                "api_gateway": APIGatewayMCPTools(),
                # TODO: Implementar Route53, CloudFront, ELB
            },
            "Seguridad": {
                "iam": IAMMCPTools(),
                # TODO: Implementar KMS, ACM, Secrets Manager, Security Groups
            },
            "Analytics": {
                "athena": AthenaMCPTools(),
                "glue": GlueMCPTools(),
                # TODO: Implementar EMR
            },
            "Integracion": {
                "cloudformation": CloudFormationMCPTools(),
                # TODO: Implementar API Gateway, Step Functions
            },
            "Contenedores": {
                "ecs": ECS_MCP_TOOLS,
                # TODO: Implementar EKS
            },
            "ML_AI": {
                # TODO: Implementar SageMaker, Bedrock, Rekognition
            },
            "Gestion": {
                "cloudwatch": CloudWatchMCPTools(),
                # TODO: Implementar Auto Scaling, Cost Explorer
            },
            "Config": {
                # TODO: Implementar Config
            },
            "AI_Assistant": {
                # TODO: Implementar Chat
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

    def _convert_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte parámetros de Gemini a tipos Python nativos (recursivamente)"""
        def convert_value(value):
            if isinstance(value, float) and value.is_integer():
                # Convertir floats enteros a int
                return int(value)
            elif isinstance(value, list):
                # Procesar listas recursivamente
                return [convert_value(item) for item in value]
            elif isinstance(value, dict):
                # Procesar diccionarios recursivamente
                return {key: convert_value(val) for key, val in value.items()}
            else:
                return value
        return convert_value(params)

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica con los parámetros dados"""
        try:
            # Convertir parámetros primero
            converted_params = self._convert_params(parameters)

            # Buscar la herramienta en las categorías
            for category, services in self.category_tools.items():
                for service_name, service_instance in services.items():
                    if hasattr(service_instance, "execute_tool"):
                        try:
                            result = service_instance.execute_tool(tool_name, converted_params)
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
            return {"error": f"Error executing tool: {str(e)}"}


# Singleton
_mcp_server = None

def get_mcp_server() -> AWSMCPServer:
    """Obtiene la instancia del servidor MCP"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = AWSMCPServer()
    return _mcp_server
