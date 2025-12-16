"""
Herramientas MCP para AWS Systems Manager
Gestión de parámetros, comandos y sesiones
"""
import boto3
from typing import List, Dict, Any, Optional
from app.utils.aws_client import get_aws_client


class SystemsManagerMCPTools:
    """Herramientas MCP para AWS Systems Manager"""

    def __init__(self):
        self.ssm = None

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas MCP disponibles"""
        return [
            {
                "name": "ssm_list_parameters",
                "description": "Lista parámetros almacenados en Parameter Store",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de resultados (1-10)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 10
                        },
                        "parameter_filters": {
                            "type": "array",
                            "description": "Filtros para los parámetros",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string", "enum": ["Name", "Type", "KeyId", "Path", "Tier"]},
                                    "option": {"type": "string", "enum": ["Equal", "BeginsWith"]},
                                    "values": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["key", "option", "values"]
                            }
                        }
                    }
                }
            },
            {
                "name": "ssm_get_parameter",
                "description": "Obtiene el valor de un parámetro específico",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del parámetro"
                        },
                        "with_decryption": {
                            "type": "boolean",
                            "description": "Si es True, desencripta parámetros SecureString",
                            "default": True
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "ssm_put_parameter",
                "description": "Crea o actualiza un parámetro en Parameter Store",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del parámetro"
                        },
                        "value": {
                            "type": "string",
                            "description": "Valor del parámetro"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["String", "StringList", "SecureString"],
                            "description": "Tipo del parámetro"
                        },
                        "description": {
                            "type": "string",
                            "description": "Descripción del parámetro"
                        },
                        "tier": {
                            "type": "string",
                            "enum": ["Standard", "Advanced", "Intelligent-Tiering"],
                            "description": "Tier del parámetro",
                            "default": "Standard"
                        },
                        "key_id": {
                            "type": "string",
                            "description": "ID de la clave KMS para parámetros SecureString"
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": "Si es True, sobrescribe el parámetro si existe",
                            "default": False
                        }
                    },
                    "required": ["name", "value", "type"]
                }
            },
            {
                "name": "ssm_delete_parameter",
                "description": "Elimina un parámetro de Parameter Store",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nombre del parámetro a eliminar"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "ssm_send_command",
                "description": "Ejecuta un comando en instancias EC2 usando Run Command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_name": {
                            "type": "string",
                            "description": "Nombre del documento SSM",
                            "default": "AWS-RunShellScript"
                        },
                        "targets": {
                            "type": "array",
                            "description": "Lista de targets (instancias o tags)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string"},
                                    "values": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["key", "values"]
                            }
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parámetros del comando",
                            "properties": {
                                "commands": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Lista de comandos a ejecutar"
                                }
                            }
                        },
                        "timeout_seconds": {
                            "type": "integer",
                            "description": "Timeout en segundos",
                            "default": 3600,
                            "minimum": 30,
                            "maximum": 172800
                        }
                    },
                    "required": ["targets", "parameters"]
                }
            },
            {
                "name": "ssm_list_commands",
                "description": "Lista comandos ejecutados con Run Command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "default": 50,
                            "maximum": 50
                        },
                        "command_id": {
                            "type": "string",
                            "description": "ID específico del comando"
                        }
                    }
                }
            },
            {
                "name": "ssm_get_command_invocation",
                "description": "Obtiene detalles de la ejecución de un comando en una instancia específica",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command_id": {
                            "type": "string",
                            "description": "ID del comando"
                        },
                        "instance_id": {
                            "type": "string",
                            "description": "ID de la instancia"
                        }
                    },
                    "required": ["command_id", "instance_id"]
                }
            },
            {
                "name": "ssm_start_session",
                "description": "Inicia una sesión interactiva en una instancia EC2",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "ID de la instancia objetivo"
                        },
                        "document_name": {
                            "type": "string",
                            "description": "Nombre del documento de sesión",
                            "default": "SSM-SessionManagerRunShell"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parámetros adicionales de la sesión"
                        }
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "ssm_describe_sessions",
                "description": "Lista sesiones activas de Session Manager",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "string",
                            "enum": ["Active", "History"],
                            "description": "Estado de las sesiones",
                            "default": "Active"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "default": 20,
                            "maximum": 20
                        }
                    }
                }
            },
            {
                "name": "ssm_terminate_session",
                "description": "Termina una sesión activa",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "ID de la sesión a terminar"
                        }
                    },
                    "required": ["session_id"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta MCP específica"""
        try:
            if not self.ssm:
                self.ssm = get_aws_client('ssm')

            if tool_name == "ssm_list_parameters":
                return self._list_parameters(**parameters)
            elif tool_name == "ssm_get_parameter":
                return self._get_parameter(**parameters)
            elif tool_name == "ssm_put_parameter":
                return self._put_parameter(**parameters)
            elif tool_name == "ssm_delete_parameter":
                return self._delete_parameter(**parameters)
            elif tool_name == "ssm_send_command":
                return self._send_command(**parameters)
            elif tool_name == "ssm_list_commands":
                return self._list_commands(**parameters)
            elif tool_name == "ssm_get_command_invocation":
                return self._get_command_invocation(**parameters)
            elif tool_name == "ssm_start_session":
                return self._start_session(**parameters)
            elif tool_name == "ssm_describe_sessions":
                return self._describe_sessions(**parameters)
            elif tool_name == "ssm_terminate_session":
                return self._terminate_session(**parameters)
            else:
                return {"error": f"Herramienta no encontrada: {tool_name}"}

        except Exception as e:
            return {"error": str(e)}

    def _list_parameters(self, **kwargs) -> Dict[str, Any]:
        """Lista parámetros de Parameter Store"""
        try:
            kwargs = {
                "MaxResults": min(kwargs.get("max_results", 10), 10)
            }

            if kwargs.get("parameter_filters"):
                kwargs["ParameterFilters"] = kwargs.get('parameter_filters')

            response = self.ssm.describe_parameters(**kwargs)

            parameters = []
            for param in response.get("Parameters", []):
                parameters.append({
                    "name": param.get("Name"),
                    "type": param.get("Type"),
                    "key_id": param.get("KeyId"),
                    "last_modified_date": param.get("LastModifiedDate").isoformat() if param.get("LastModifiedDate") else None,
                    "version": param.get("Version"),
                    "tier": param.get("Tier", "Standard")
                })

            return {
                "parameters": parameters,
                "next_token": response.get("NextToken")
            }

        except Exception as e:
            return {"error": f"Error listando parámetros: {str(e)}"}

    def _get_parameter(self, **kwargs) -> Dict[str, Any]:
        """Obtiene un parámetro específico"""
        try:
            response = self.ssm.get_parameter(
                Name=kwargs.get('name'),
                WithDecryption=kwargs.get("with_decryption", True)
            )

            parameter = response.get("Parameter", {})
            return {
                "name": parameter.get("Name"),
                "value": parameter.get("Value"),
                "type": parameter.get("Type"),
                "version": parameter.get("Version"),
                "last_modified_date": parameter.get("LastModifiedDate").isoformat() if parameter.get("LastModifiedDate") else None,
                "tier": parameter.get("Tier", "Standard")
            }

        except Exception as e:
            return {"error": f"Error obteniendo parámetro: {str(e)}"}

    def _put_parameter(self, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza un parámetro"""
        try:
            kwargs = {
                "Name": kwargs.get('name'),
                "Value": kwargs.get('value'),
                "Type": kwargs.get('type'),
                "Overwrite": kwargs.get("overwrite", False)
            }

            if kwargs.get("description"):
                kwargs["Description"] = kwargs.get('description')

            if kwargs.get("tier"):
                kwargs["Tier"] = kwargs.get('tier')

            if kwargs.get("type") == "SecureString" and kwargs.get("key_id"):
                kwargs["KeyId"] = kwargs.get('key_id')

            response = self.ssm.put_parameter(**kwargs)

            return {
                "version": response.get("Version"),
                "tier": response.get("Tier")
            }

        except Exception as e:
            return {"error": f"Error creando parámetro: {str(e)}"}

    def _delete_parameter(self, **kwargs) -> Dict[str, Any]:
        """Elimina un parámetro"""
        try:
            self.ssm.delete_parameter(Name=kwargs.get('name'))
            return {"message": f"Parámetro {kwargs.get('name')} eliminado exitosamente"}

        except Exception as e:
            return {"error": f"Error eliminando parámetro: {str(e)}"}

    def _send_command(self, **kwargs) -> Dict[str, Any]:
        """Ejecuta un comando usando Run Command"""
        try:
            kwargs = {
                "DocumentName": kwargs.get("document_name", "AWS-RunShellScript"),
                "Targets": kwargs.get('targets'),
                "Parameters": kwargs.get('parameters')
            }

            if kwargs.get("timeout_seconds"):
                kwargs["TimeoutSeconds"] = kwargs.get('timeout_seconds')

            response = self.ssm.send_command(**kwargs)

            return {
                "command_id": response["Command"]["CommandId"],
                "status": response["Command"].get("Status"),
                "requested_date_time": response["Command"].get("RequestedDateTime").isoformat() if response["Command"].get("RequestedDateTime") else None
            }

        except Exception as e:
            return {"error": f"Error ejecutando comando: {str(e)}"}

    def _list_commands(self, **kwargs) -> Dict[str, Any]:
        """Lista comandos ejecutados"""
        try:
            kwargs = {
                "MaxResults": min(kwargs.get("max_results", 50), 50)
            }

            if kwargs.get("command_id"):
                kwargs["CommandId"] = kwargs.get('command_id')

            response = self.ssm.list_commands(**kwargs)

            commands = []
            for cmd in response.get("Commands", []):
                commands.append({
                    "command_id": cmd.get("CommandId"),
                    "document_name": cmd.get("DocumentName"),
                    "status": cmd.get("Status"),
                    "status_details": cmd.get("StatusDetails"),
                    "requested_date_time": cmd.get("RequestedDateTime").isoformat() if cmd.get("RequestedDateTime") else None,
                    "target_count": cmd.get("TargetCount"),
                    "error_count": cmd.get("ErrorCount")
                })

            return {
                "commands": commands,
                "next_token": response.get("NextToken")
            }

        except Exception as e:
            return {"error": f"Error listando comandos: {str(e)}"}

    def _get_command_invocation(self, **kwargs) -> Dict[str, Any]:
        """Obtiene detalles de la ejecución de un comando"""
        try:
            response = self.ssm.get_command_invocation(
                CommandId=kwargs.get('command_id'),
                InstanceId=kwargs.get('instance_id')
            )

            return {
                "command_id": response.get("CommandId"),
                "instance_id": response.get("InstanceId"),
                "status": response.get("Status"),
                "status_details": response.get("StatusDetails"),
                "response_code": response.get("ResponseCode"),
                "execution_start_date_time": response.get("ExecutionStartDateTime").isoformat() if response.get("ExecutionStartDateTime") else None,
                "execution_end_date_time": response.get("ExecutionEndDateTime").isoformat() if response.get("ExecutionEndDateTime") else None,
                "standard_output_content": response.get("StandardOutputContent"),
                "standard_error_content": response.get("StandardErrorContent")
            }

        except Exception as e:
            return {"error": f"Error obteniendo invocación del comando: {str(e)}"}

    def _start_session(self, **kwargs) -> Dict[str, Any]:
        """Inicia una sesión interactiva"""
        try:
            kwargs = {
                "Target": kwargs.get('target')
            }

            if kwargs.get("document_name"):
                kwargs["DocumentName"] = kwargs.get('document_name')

            if kwargs.get("parameters"):
                kwargs["Parameters"] = kwargs.get('parameters')

            response = self.ssm.start_session(**kwargs)

            return {
                "session_id": response.get("SessionId"),
                "stream_url": response.get("StreamUrl"),
                "token_value": response.get("TokenValue")
            }

        except Exception as e:
            return {"error": f"Error iniciando sesión: {str(e)}"}

    def _describe_sessions(self, **kwargs) -> Dict[str, Any]:
        """Lista sesiones activas"""
        try:
            kwargs = {
                "State": kwargs.get("state", "Active"),
                "MaxResults": min(kwargs.get("max_results", 20), 20)
            }

            response = self.ssm.describe_sessions(**kwargs)

            sessions = []
            for session in response.get("Sessions", []):
                sessions.append({
                    "session_id": session.get("SessionId"),
                    "target": session.get("Target"),
                    "status": session.get("Status"),
                    "start_date": session.get("StartDate").isoformat() if session.get("StartDate") else None,
                    "end_date": session.get("EndDate").isoformat() if session.get("EndDate") else None,
                    "document_name": session.get("DocumentName"),
                    "owner": session.get("Owner")
                })

            return {
                "sessions": sessions,
                "next_token": response.get("NextToken")
            }

        except Exception as e:
            return {"error": f"Error describiendo sesiones: {str(e)}"}

    def _terminate_session(self, **kwargs) -> Dict[str, Any]:
        """Termina una sesión activa"""
        try:
            response = self.ssm.terminate_session(SessionId=kwargs.get('session_id'))

            return {
                "session_id": response.get("SessionId")
            }

        except Exception as e:
            return {"error": f"Error terminando sesión: {str(e)}"}