"""
AWS Config MCP Tools - Herramientas para gestión de configuración y cumplimiento
"""

import boto3
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError


class ConfigMCPTools:
    """Herramientas MCP para AWS Config"""

    def __init__(self):
        self.client = boto3.client('config')
        self.tools = [
            {
                "name": "config_list_rules",
                "description": "Lista todas las reglas de Config Rules en la cuenta AWS",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "config_describe_rule",
                "description": "Obtiene detalles completos de una regla de Config específica",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_name": {
                            "type": "string",
                            "description": "Nombre de la regla de Config"
                        }
                    },
                    "required": ["rule_name"]
                }
            },
            {
                "name": "config_create_rule",
                "description": "Crea una nueva regla de Config",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_name": {
                            "type": "string",
                            "description": "Nombre único para la regla"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción de la regla"
                        },
                        "source_identifier": {
                            "type": "string",
                            "description": "Identificador de la regla administrada por AWS"
                        },
                        "resource_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tipos de recursos a evaluar"
                        }
                    },
                    "required": ["rule_name", "source_identifier"]
                }
            },
            {
                "name": "config_delete_rule",
                "description": "Elimina una regla de Config",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_name": {
                            "type": "string",
                            "description": "Nombre de la regla a eliminar"
                        }
                    },
                    "required": ["rule_name"]
                }
            },
            {
                "name": "config_start_evaluation",
                "description": "Inicia la evaluación de una regla de Config",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_name": {
                            "type": "string",
                            "description": "Nombre de la regla a evaluar"
                        }
                    },
                    "required": ["rule_name"]
                }
            },
            {
                "name": "config_list_configuration_items",
                "description": "Lista los elementos de configuración",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Tipo de recurso a filtrar (opcional)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "default": 50
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "config_describe_remediation_configurations",
                "description": "Lista las configuraciones de remediation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config_rule_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Nombres de reglas para filtrar"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "config_put_remediation_configuration",
                "description": "Configura una acción de remediation para una regla",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config_rule_name": {
                            "type": "string",
                            "description": "Nombre de la regla de Config"
                        },
                        "target_type": {
                            "type": "string",
                            "description": "Tipo de target (SSM_DOCUMENT o LAMBDA)",
                            "enum": ["SSM_DOCUMENT", "LAMBDA"]
                        },
                        "target_id": {
                            "type": "string",
                            "description": "ID del target (ARN del documento SSM o función Lambda)"
                        }
                    },
                    "required": ["config_rule_name", "target_type", "target_id"]
                }
            },
            {
                "name": "config_describe_configuration_recorder_status",
                "description": "Obtiene el estado del Configuration Recorder",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "config_start_configuration_recorder",
                "description": "Inicia el Configuration Recorder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "recorder_name": {
                            "type": "string",
                            "description": "Nombre del recorder (opcional, usa default si no se especifica)"
                        }
                    },
                    "required": []
                }
            }
        ]

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles"""
        return self.tools

    # Implementación de las herramientas

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica"""
        try:
            if tool_name == "config_list_rules":
                return await self._list_rules()
            elif tool_name == "config_describe_rule":
                return await self._describe_rule(arguments)
            elif tool_name == "config_create_rule":
                return await self._create_rule(arguments)
            elif tool_name == "config_delete_rule":
                return await self._delete_rule(arguments)
            elif tool_name == "config_start_evaluation":
                return await self._start_evaluation(arguments)
            elif tool_name == "config_list_configuration_items":
                return await self._list_configuration_items(arguments)
            elif tool_name == "config_describe_remediation_configurations":
                return await self._describe_remediation_configurations(arguments)
            elif tool_name == "config_put_remediation_configuration":
                return await self._put_remediation_configuration(arguments)
            elif tool_name == "config_describe_configuration_recorder_status":
                return await self._describe_configuration_recorder_status()
            elif tool_name == "config_start_configuration_recorder":
                return await self._start_configuration_recorder(arguments)
            else:
                return {"error": f"Herramienta no encontrada: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}

    async def _list_rules(self) -> Dict[str, Any]:
        """Lista todas las reglas de Config Rules"""
        try:
            response = self.client.describe_config_rules()
            rules = []
            for rule in response.get('ConfigRules', []):
                rules.append({
                    'name': rule.get('ConfigRuleName'),
                    'state': rule.get('ConfigRuleState'),
                    'description': rule.get('Description'),
                    'compliance_type': rule.get('Compliance', {}).get('ComplianceType', 'UNKNOWN')
                })
            return {'rules': rules, 'count': len(rules)}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _describe_rule(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene detalles de una regla específica"""
        try:
            rule_name = arguments.get('rule_name')
            if not rule_name:
                return {'error': 'rule_name es requerido'}

            response = self.client.describe_config_rules(ConfigRuleNames=[rule_name])
            if not response.get('ConfigRules'):
                return {'error': f'Regla {rule_name} no encontrada'}

            rule = response['ConfigRules'][0]
            return {
                'rule': {
                    'name': rule.get('ConfigRuleName'),
                    'arn': rule.get('ConfigRuleArn'),
                    'state': rule.get('ConfigRuleState'),
                    'description': rule.get('Description'),
                    'source': rule.get('Source', {}),
                    'scope': rule.get('Scope', {}),
                    'compliance': rule.get('Compliance', {})
                }
            }
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _create_rule(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva regla de Config"""
        try:
            rule_name = arguments.get('rule_name')
            source_identifier = arguments.get('source_identifier')

            if not rule_name or not source_identifier:
                return {'error': 'rule_name y source_identifier son requeridos'}

            rule_config = {
                'ConfigRuleName': rule_name,
                'Source': {
                    'Owner': 'AWS',
                    'SourceIdentifier': source_identifier
                }
            }

            if arguments.get('description'):
                rule_config['Description'] = arguments['description']

            if arguments.get('resource_types'):
                rule_config['Scope'] = {
                    'ComplianceResourceTypes': arguments['resource_types']
                }

            response = self.client.put_config_rule(**rule_config)
            return {
                'message': f'Regla {rule_name} creada exitosamente',
                'rule_arn': response.get('ConfigRuleArn')
            }
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _delete_rule(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una regla de Config"""
        try:
            rule_name = arguments.get('rule_name')
            if not rule_name:
                return {'error': 'rule_name es requerido'}

            self.client.delete_config_rule(ConfigRuleName=rule_name)
            return {'message': f'Regla {rule_name} eliminada exitosamente'}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _start_evaluation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia la evaluación de una regla"""
        try:
            rule_name = arguments.get('rule_name')
            if not rule_name:
                return {'error': 'rule_name es requerido'}

            self.client.start_config_rules_evaluation(ConfigRuleNames=[rule_name])
            return {'message': f'Evaluación iniciada para la regla {rule_name}'}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _list_configuration_items(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Lista elementos de configuración"""
        try:
            params = {}
            if arguments.get('resource_type'):
                params['resourceType'] = arguments['resource_type']

            max_results = arguments.get('max_results', 50)
            params['limit'] = min(max_results, 100)  # AWS limita a 100

            response = self.client.list_discovered_resources(**params)
            items = []
            for item in response.get('resourceIdentifiers', []):
                items.append({
                    'resource_type': item.get('resourceType'),
                    'resource_id': item.get('resourceId'),
                    'resource_name': item.get('resourceName')
                })
            return {'items': items, 'count': len(items)}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _describe_remediation_configurations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Lista configuraciones de remediation"""
        try:
            params = {}
            if arguments.get('config_rule_names'):
                params['ConfigRuleNames'] = arguments['config_rule_names']

            response = self.client.describe_remediation_configurations(**params)
            remediations = []
            for rem in response.get('RemediationConfigurations', []):
                remediations.append({
                    'config_rule_name': rem.get('ConfigRuleName'),
                    'target_type': rem.get('TargetType'),
                    'target_id': rem.get('TargetId'),
                    'parameters': rem.get('Parameters', {})
                })
            return {'remediations': remediations, 'count': len(remediations)}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _put_remediation_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Configura una acción de remediation"""
        try:
            config_rule_name = arguments.get('config_rule_name')
            target_type = arguments.get('target_type')
            target_id = arguments.get('target_id')

            if not all([config_rule_name, target_type, target_id]):
                return {'error': 'config_rule_name, target_type y target_id son requeridos'}

            self.client.put_remediation_configuration(
                ConfigRuleName=config_rule_name,
                TargetType=target_type,
                TargetId=target_id
            )
            return {'message': f'Remediation configurada para la regla {config_rule_name}'}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _describe_configuration_recorder_status(self) -> Dict[str, Any]:
        """Obtiene el estado del Configuration Recorder"""
        try:
            response = self.client.describe_configuration_recorder_status()
            recorders = []
            for recorder in response.get('ConfigurationRecordersStatus', []):
                recorders.append({
                    'name': recorder.get('Name'),
                    'status': recorder.get('Status'),
                    'is_enabled': recorder.get('IsEnabled'),
                    'last_status_change_time': recorder.get('LastStatusChangeTime')
                })
            return {'recorders': recorders}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def _start_configuration_recorder(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia el Configuration Recorder"""
        try:
            recorder_name = arguments.get('recorder_name', 'default')
            self.client.start_configuration_recorder(ConfigurationRecorderName=recorder_name)
            return {'message': f'Configuration Recorder {recorder_name} iniciado'}
        except ClientError as e:
            return {"error": f"Error de AWS: {e}"}
        except Exception as e:
            return {"error": str(e)}


# Mantener compatibilidad con el sistema anterior de app.py
CONFIG_MCP_TOOLS = {
    'list_config_rules': {
        'description': 'Listar todas las reglas de AWS Config',
        'parameters': {}
    },
    'put_config_rule': {
        'description': 'Crear o actualizar una regla de AWS Config',
        'parameters': {
            'rule_name': {'type': 'string', 'description': 'Nombre de la regla'},
            'description': {'type': 'string', 'description': 'Descripción de la regla'},
            'source_identifier': {'type': 'string', 'description': 'Identificador de la fuente (ej: S3_BUCKET_VERSIONING_ENABLED)'},
            'resource_types': {'type': 'array', 'description': 'Tipos de recursos a evaluar (opcional)'}
        }
    },
    'delete_config_rules': {
        'description': 'Eliminar una regla de AWS Config',
        'parameters': {
            'rule_name': {'type': 'string', 'description': 'Nombre de la regla a eliminar'}
        }
    },
    'get_compliance_details': {
        'description': 'Obtener detalles de cumplimiento para una regla específica',
        'parameters': {
            'rule_name': {'type': 'string', 'description': 'Nombre de la regla'},
            'limit': {'type': 'integer', 'description': 'Número máximo de resultados (opcional)'}
        }
    }
}
