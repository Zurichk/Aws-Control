"""
MCP Tools para AWS IAM
Herramientas para gestión de identidades y accesos
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class IAMMCPTools:
    """Herramientas MCP para operaciones con AWS IAM"""

    # Constantes para descripciones
    DESC_USER_NAME = 'Nombre del usuario IAM'
    DESC_GROUP_NAME = 'Nombre del grupo IAM'
    DESC_ROLE_NAME = 'Nombre del rol IAM'
    DESC_POLICY_ARN = 'ARN de la política'
    DESC_POLICY_NAME = 'Nombre de la política'
    DESC_PATH = 'Ruta del recurso IAM (ej: /)'
    DESC_MAX_ITEMS = 'Número máximo de elementos a retornar'

    def __init__(self):
        self.iam_client = None

    def _get_client(self):
        """Obtiene el cliente IAM"""
        if self.iam_client is None:
            self.iam_client = get_aws_client('iam')
        return self.iam_client

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para IAM"""
        return [
            {
                'name': 'iam_list_users',
                'description': 'Lista usuarios IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path_prefix': {'type': 'string', 'description': 'Prefijo de ruta para filtrar usuarios'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    }
                }
            },
            {
                'name': 'iam_create_user',
                'description': 'Crea un nuevo usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME},
                        'path': {'type': 'string', 'description': self.DESC_PATH, 'default': '/'},
                        'permissions_boundary': {'type': 'string', 'description': 'ARN del límite de permisos'},
                        'tags': {'type': 'array', 'description': 'Tags para el usuario', 'items': {'type': 'object'}}
                    },
                    'required': ['user_name']
                }
            },
            {
                'name': 'iam_delete_user',
                'description': 'Elimina un usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME}
                    },
                    'required': ['user_name']
                }
            },
            {
                'name': 'iam_create_access_key',
                'description': 'Crea una access key para un usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME}
                    },
                    'required': ['user_name']
                }
            },
            {
                'name': 'iam_delete_access_key',
                'description': 'Elimina una access key de un usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME},
                        'access_key_id': {'type': 'string', 'description': 'ID de la access key a eliminar'}
                    },
                    'required': ['user_name', 'access_key_id']
                }
            },
            {
                'name': 'iam_list_groups',
                'description': 'Lista grupos IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path_prefix': {'type': 'string', 'description': 'Prefijo de ruta para filtrar grupos'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    }
                }
            },
            {
                'name': 'iam_create_group',
                'description': 'Crea un nuevo grupo IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_name': {'type': 'string', 'description': self.DESC_GROUP_NAME},
                        'path': {'type': 'string', 'description': self.DESC_PATH, 'default': '/'}
                    },
                    'required': ['group_name']
                }
            },
            {
                'name': 'iam_add_user_to_group',
                'description': 'Agrega un usuario a un grupo IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_name': {'type': 'string', 'description': self.DESC_GROUP_NAME},
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME}
                    },
                    'required': ['group_name', 'user_name']
                }
            },
            {
                'name': 'iam_remove_user_from_group',
                'description': 'Remueve un usuario de un grupo IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_name': {'type': 'string', 'description': self.DESC_GROUP_NAME},
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME}
                    },
                    'required': ['group_name', 'user_name']
                }
            },
            {
                'name': 'iam_list_roles',
                'description': 'Lista roles IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path_prefix': {'type': 'string', 'description': 'Prefijo de ruta para filtrar roles'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    }
                }
            },
            {
                'name': 'iam_create_role',
                'description': 'Crea un nuevo rol IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'role_name': {'type': 'string', 'description': self.DESC_ROLE_NAME},
                        'assume_role_policy_document': {'type': 'string', 'description': 'Documento de política de asunción (JSON)'},
                        'path': {'type': 'string', 'description': self.DESC_PATH, 'default': '/'},
                        'description': {'type': 'string', 'description': 'Descripción del rol'},
                        'max_session_duration': {'type': 'integer', 'description': 'Duración máxima de sesión en segundos', 'default': 3600},
                        'permissions_boundary': {'type': 'string', 'description': 'ARN del límite de permisos'},
                        'tags': {'type': 'array', 'description': 'Tags para el rol', 'items': {'type': 'object'}}
                    },
                    'required': ['role_name', 'assume_role_policy_document']
                }
            },
            {
                'name': 'iam_delete_role',
                'description': 'Elimina un rol IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'role_name': {'type': 'string', 'description': self.DESC_ROLE_NAME}
                    },
                    'required': ['role_name']
                }
            },
            {
                'name': 'iam_attach_role_policy',
                'description': 'Asocia una política administrada a un rol IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'role_name': {'type': 'string', 'description': self.DESC_ROLE_NAME},
                        'policy_arn': {'type': 'string', 'description': self.DESC_POLICY_ARN}
                    },
                    'required': ['role_name', 'policy_arn']
                }
            },
            {
                'name': 'iam_detach_role_policy',
                'description': 'Desasocia una política administrada de un rol IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'role_name': {'type': 'string', 'description': self.DESC_ROLE_NAME},
                        'policy_arn': {'type': 'string', 'description': self.DESC_POLICY_ARN}
                    },
                    'required': ['role_name', 'policy_arn']
                }
            },
            {
                'name': 'iam_list_policies',
                'description': 'Lista políticas IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'scope': {'type': 'string', 'description': 'Alcance de las políticas', 'enum': ['All', 'AWS', 'Local'], 'default': 'All'},
                        'only_attached': {'type': 'boolean', 'description': 'Solo políticas adjuntas', 'default': False},
                        'path_prefix': {'type': 'string', 'description': 'Prefijo de ruta'},
                        'policy_usage_filter': {'type': 'string', 'description': 'Filtro de uso', 'enum': ['PermissionsPolicy', 'PermissionsBoundary']},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    }
                }
            },
            {
                'name': 'iam_create_policy',
                'description': 'Crea una nueva política IAM personalizada',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'policy_name': {'type': 'string', 'description': self.DESC_POLICY_NAME},
                        'policy_document': {'type': 'string', 'description': 'Documento de política (JSON)'},
                        'path': {'type': 'string', 'description': self.DESC_PATH, 'default': '/'},
                        'description': {'type': 'string', 'description': 'Descripción de la política'},
                        'tags': {'type': 'array', 'description': 'Tags para la política', 'items': {'type': 'object'}}
                    },
                    'required': ['policy_name', 'policy_document']
                }
            },
            {
                'name': 'iam_get_user',
                'description': 'Obtiene detalles completos de un usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME}
                    },
                    'required': ['user_name']
                }
            },
            {
                'name': 'iam_list_access_keys',
                'description': 'Lista access keys de un usuario IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_name': {'type': 'string', 'description': self.DESC_USER_NAME},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    }
                }
            },
            {
                'name': 'iam_list_attached_role_policies',
                'description': 'Lista políticas adjuntas a un rol IAM',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'role_name': {'type': 'string', 'description': self.DESC_ROLE_NAME},
                        'path_prefix': {'type': 'string', 'description': 'Prefijo de ruta'},
                        'max_items': {'type': 'integer', 'description': self.DESC_MAX_ITEMS, 'default': 100}
                    },
                    'required': ['role_name']
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una herramienta específica de IAM"""
        try:
            if tool_name == 'iam_list_users':
                return self._list_users(parameters)
            elif tool_name == 'iam_create_user':
                return self._create_user(parameters)
            elif tool_name == 'iam_delete_user':
                return self._delete_user(parameters)
            elif tool_name == 'iam_create_access_key':
                return self._create_access_key(parameters)
            elif tool_name == 'iam_delete_access_key':
                return self._delete_access_key(parameters)
            elif tool_name == 'iam_list_groups':
                return self._list_groups(parameters)
            elif tool_name == 'iam_create_group':
                return self._create_group(parameters)
            elif tool_name == 'iam_add_user_to_group':
                return self._add_user_to_group(parameters)
            elif tool_name == 'iam_remove_user_from_group':
                return self._remove_user_from_group(parameters)
            elif tool_name == 'iam_list_roles':
                return self._list_roles(parameters)
            elif tool_name == 'iam_create_role':
                return self._create_role(parameters)
            elif tool_name == 'iam_delete_role':
                return self._delete_role(parameters)
            elif tool_name == 'iam_attach_role_policy':
                return self._attach_role_policy(parameters)
            elif tool_name == 'iam_detach_role_policy':
                return self._detach_role_policy(parameters)
            elif tool_name == 'iam_list_policies':
                return self._list_policies(parameters)
            elif tool_name == 'iam_create_policy':
                return self._create_policy(parameters)
            elif tool_name == 'iam_get_user':
                return self._get_user(parameters)
            elif tool_name == 'iam_list_access_keys':
                return self._list_access_keys(parameters)
            elif tool_name == 'iam_list_attached_role_policies':
                return self._list_attached_role_policies(parameters)
            else:
                return {'error': f'Herramienta IAM no encontrada: {tool_name}'}

        except Exception as e:
            return {'error': f'Error ejecutando herramienta IAM {tool_name}: {str(e)}'}

    def _list_users(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista usuarios IAM"""
        client = self._get_client()

        iam_params = {}
        if 'path_prefix' in params:
            iam_params['PathPrefix'] = params['path_prefix']
        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_users(**iam_params)

        users = []
        for user in response['Users']:
            users.append({
                'user_name': user['UserName'],
                'user_id': user['UserId'],
                'arn': user['Arn'],
                'path': user['Path'],
                'create_date': user['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'password_last_used': user.get('PasswordLastUsed').strftime('%Y-%m-%d %H:%M:%S') if user.get('PasswordLastUsed') else None,
                'tags': {tag['Key']: tag['Value'] for tag in user.get('Tags', [])}
            })

        return {
            'users': users,
            'total_count': len(users),
            'is_truncated': response.get('IsTruncated', False)
        }

    def _create_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un usuario IAM"""
        client = self._get_client()

        iam_params = {
            'UserName': params['user_name']
        }

        if 'path' in params:
            iam_params['Path'] = params['path']
        if 'permissions_boundary' in params:
            iam_params['PermissionsBoundary'] = params['permissions_boundary']

        response = client.create_user(**iam_params)

        user_arn = response['User']['Arn']

        # Agregar tags si se proporcionaron
        if 'tags' in params:
            client.tag_user(
                UserName=params['user_name'],
                Tags=params['tags']
            )

        return {
            'message': f'Usuario IAM {params["user_name"]} creado exitosamente',
            'user_name': params['user_name'],
            'user_arn': user_arn
        }

    def _delete_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un usuario IAM"""
        client = self._get_client()

        client.delete_user(UserName=params['user_name'])

        return {
            'message': f'Usuario IAM {params["user_name"]} eliminado exitosamente',
            'user_name': params['user_name']
        }

    def _create_access_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una access key para un usuario"""
        client = self._get_client()

        response = client.create_access_key(UserName=params['user_name'])

        return {
            'message': f'Access key creada para usuario {params["user_name"]}',
            'user_name': params['user_name'],
            'access_key_id': response['AccessKey']['AccessKeyId'],
            'secret_access_key': response['AccessKey']['SecretAccessKey'],
            'status': response['AccessKey']['Status'],
            'create_date': response['AccessKey']['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
        }

    def _delete_access_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una access key"""
        client = self._get_client()

        client.delete_access_key(
            UserName=params['user_name'],
            AccessKeyId=params['access_key_id']
        )

        return {
            'message': f'Access key {params["access_key_id"]} eliminada del usuario {params["user_name"]}',
            'user_name': params['user_name'],
            'access_key_id': params['access_key_id']
        }

    def _list_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista grupos IAM"""
        client = self._get_client()

        iam_params = {}
        if 'path_prefix' in params:
            iam_params['PathPrefix'] = params['path_prefix']
        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_groups(**iam_params)

        groups = []
        for group in response['Groups']:
            groups.append({
                'group_name': group['GroupName'],
                'group_id': group['GroupId'],
                'arn': group['Arn'],
                'path': group['Path'],
                'create_date': group['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
            })

        return {
            'groups': groups,
            'total_count': len(groups),
            'is_truncated': response.get('IsTruncated', False)
        }

    def _create_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un grupo IAM"""
        client = self._get_client()

        iam_params = {
            'GroupName': params['group_name']
        }

        if 'path' in params:
            iam_params['Path'] = params['path']

        response = client.create_group(**iam_params)

        return {
            'message': f'Grupo IAM {params["group_name"]} creado exitosamente',
            'group_name': params['group_name'],
            'group_arn': response['Group']['Arn']
        }

    def _add_user_to_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un usuario a un grupo"""
        client = self._get_client()

        client.add_user_to_group(
            GroupName=params['group_name'],
            UserName=params['user_name']
        )

        return {
            'message': f'Usuario {params["user_name"]} agregado al grupo {params["group_name"]}',
            'group_name': params['group_name'],
            'user_name': params['user_name']
        }

    def _remove_user_from_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remueve un usuario de un grupo"""
        client = self._get_client()

        client.remove_user_from_group(
            GroupName=params['group_name'],
            UserName=params['user_name']
        )

        return {
            'message': f'Usuario {params["user_name"]} removido del grupo {params["group_name"]}',
            'group_name': params['group_name'],
            'user_name': params['user_name']
        }

    def _list_roles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista roles IAM"""
        client = self._get_client()

        iam_params = {}
        if 'path_prefix' in params:
            iam_params['PathPrefix'] = params['path_prefix']
        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_roles(**iam_params)

        roles = []
        for role in response['Roles']:
            roles.append({
                'role_name': role['RoleName'],
                'role_id': role['RoleId'],
                'arn': role['Arn'],
                'path': role['Path'],
                'create_date': role['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'description': role.get('Description'),
                'max_session_duration': role.get('MaxSessionDuration'),
                'assume_role_policy_document': role.get('AssumeRolePolicyDocument')
            })

        return {
            'roles': roles,
            'total_count': len(roles),
            'is_truncated': response.get('IsTruncated', False)
        }

    def _create_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un rol IAM"""
        client = self._get_client()

        iam_params = {
            'RoleName': params['role_name'],
            'AssumeRolePolicyDocument': params['assume_role_policy_document']
        }

        if 'path' in params:
            iam_params['Path'] = params['path']
        if 'description' in params:
            iam_params['Description'] = params['description']
        if 'max_session_duration' in params:
            iam_params['MaxSessionDuration'] = params['max_session_duration']
        if 'permissions_boundary' in params:
            iam_params['PermissionsBoundary'] = params['permissions_boundary']

        response = client.create_role(**iam_params)

        role_arn = response['Role']['Arn']

        # Agregar tags si se proporcionaron
        if 'tags' in params:
            client.tag_role(
                RoleName=params['role_name'],
                Tags=params['tags']
            )

        return {
            'message': f'Rol IAM {params["role_name"]} creado exitosamente',
            'role_name': params['role_name'],
            'role_arn': role_arn
        }

    def _delete_role(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina un rol IAM"""
        client = self._get_client()

        client.delete_role(RoleName=params['role_name'])

        return {
            'message': f'Rol IAM {params["role_name"]} eliminado exitosamente',
            'role_name': params['role_name']
        }

    def _attach_role_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Asocia una política a un rol"""
        client = self._get_client()

        client.attach_role_policy(
            RoleName=params['role_name'],
            PolicyArn=params['policy_arn']
        )

        return {
            'message': f'Política {params["policy_arn"]} asociada al rol {params["role_name"]}',
            'role_name': params['role_name'],
            'policy_arn': params['policy_arn']
        }

    def _detach_role_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Desasocia una política de un rol"""
        client = self._get_client()

        client.detach_role_policy(
            RoleName=params['role_name'],
            PolicyArn=params['policy_arn']
        )

        return {
            'message': f'Política {params["policy_arn"]} desasociada del rol {params["role_name"]}',
            'role_name': params['role_name'],
            'policy_arn': params['policy_arn']
        }

    def _list_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista políticas IAM"""
        client = self._get_client()

        iam_params = {}
        if 'scope' in params:
            iam_params['Scope'] = params['scope']
        if 'only_attached' in params:
            iam_params['OnlyAttached'] = params['only_attached']
        if 'path_prefix' in params:
            iam_params['PathPrefix'] = params['path_prefix']
        if 'policy_usage_filter' in params:
            iam_params['PolicyUsageFilter'] = params['policy_usage_filter']
        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_policies(**iam_params)

        policies = []
        for policy in response['Policies']:
            policies.append({
                'policy_name': policy['PolicyName'],
                'policy_id': policy['PolicyId'],
                'arn': policy['Arn'],
                'path': policy['Path'],
                'default_version_id': policy['DefaultVersionId'],
                'attachment_count': policy.get('AttachmentCount', 0),
                'permissions_boundary_usage_count': policy.get('PermissionsBoundaryUsageCount', 0),
                'is_attachable': policy.get('IsAttachable', True),
                'description': policy.get('Description'),
                'create_date': policy['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'update_date': policy['UpdateDate'].strftime('%Y-%m-%d %H:%M:%S')
            })

        return {
            'policies': policies,
            'total_count': len(policies),
            'is_truncated': response.get('IsTruncated', False)
        }

    def _create_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una política IAM personalizada"""
        client = self._get_client()

        iam_params = {
            'PolicyName': params['policy_name'],
            'PolicyDocument': params['policy_document']
        }

        if 'path' in params:
            iam_params['Path'] = params['path']
        if 'description' in params:
            iam_params['Description'] = params['description']

        response = client.create_policy(**iam_params)

        policy_arn = response['Policy']['Arn']

        # Agregar tags si se proporcionaron
        if 'tags' in params:
            client.tag_policy(
                PolicyArn=policy_arn,
                Tags=params['tags']
            )

        return {
            'message': f'Política IAM {params["policy_name"]} creada exitosamente',
            'policy_name': params['policy_name'],
            'policy_arn': policy_arn
        }

    def _get_user(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene detalles completos de un usuario"""
        client = self._get_client()

        response = client.get_user(UserName=params['user_name'])

        user = response['User']

        return {
            'user': {
                'user_name': user['UserName'],
                'user_id': user['UserId'],
                'arn': user['Arn'],
                'path': user['Path'],
                'create_date': user['CreateDate'].strftime('%Y-%m-%d %H:%M:%S'),
                'password_last_used': user.get('PasswordLastUsed').strftime('%Y-%m-%d %H:%M:%S') if user.get('PasswordLastUsed') else None,
                'permissions_boundary': user.get('PermissionsBoundary'),
                'tags': {tag['Key']: tag['Value'] for tag in user.get('Tags', [])}
            }
        }

    def _list_access_keys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista access keys de un usuario"""
        client = self._get_client()

        iam_params = {
            'UserName': params['user_name']
        }

        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_access_keys(**iam_params)

        access_keys = []
        for key in response['AccessKeyMetadata']:
            access_keys.append({
                'access_key_id': key['AccessKeyId'],
                'status': key['Status'],
                'create_date': key['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')
            })

        return {
            'user_name': params['user_name'],
            'access_keys': access_keys,
            'total_count': len(access_keys),
            'is_truncated': response.get('IsTruncated', False)
        }

    def _list_attached_role_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista políticas adjuntas a un rol"""
        client = self._get_client()

        iam_params = {
            'RoleName': params['role_name']
        }

        if 'path_prefix' in params:
            iam_params['PathPrefix'] = params['path_prefix']
        if 'max_items' in params:
            iam_params['MaxItems'] = params['max_items']

        response = client.list_attached_role_policies(**iam_params)

        policies = []
        for policy in response['AttachedPolicies']:
            policies.append({
                'policy_arn': policy['PolicyArn'],
                'policy_name': policy['PolicyName']
            })

        return {
            'role_name': params['role_name'],
            'attached_policies': policies,
            'total_count': len(policies),
            'is_truncated': response.get('IsTruncated', False)
        }