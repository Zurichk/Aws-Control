"""
MCP Tools para AWS Auto Scaling
Herramientas para gestión de grupos de Auto Scaling y políticas de escalado
"""
import boto3
from typing import Dict, List, Any, Optional
from app.utils.aws_client import get_aws_client


class AutoScalingMCPTools:
    """Herramientas MCP para AWS Auto Scaling"""

    def __init__(self):
        self.autoscaling = None

    def _get_autoscaling_client(self):
        """Obtiene el cliente Auto Scaling"""
        if self.autoscaling is None:
            self.autoscaling = get_aws_client('autoscaling')
        return self.autoscaling

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna la lista de herramientas disponibles para Auto Scaling"""
        return [
            {
                'name': 'autoscaling_list_groups',
                'description': 'Lista todos los grupos de Auto Scaling',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'group_names': {
                            'type': 'array',
                            'description': 'Lista específica de nombres de grupos',
                            'items': {'type': 'string'}
                        },
                        'max_records': {
                            'type': 'integer',
                            'description': 'Número máximo de registros',
                            'default': 100
                        }
                    }
                },
                'function': self.list_autoscaling_groups
            },
            {
                'name': 'autoscaling_create_group',
                'description': 'Crea un nuevo grupo de Auto Scaling',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'auto_scaling_group_name': {
                            'type': 'string',
                            'description': 'Nombre del grupo de Auto Scaling'
                        },
                        'launch_template_id': {
                            'type': 'string',
                            'description': 'ID del launch template'
                        },
                        'launch_template_name': {
                            'type': 'string',
                            'description': 'Nombre del launch template'
                        },
                        'min_size': {
                            'type': 'integer',
                            'description': 'Tamaño mínimo del grupo',
                            'default': 1
                        },
                        'max_size': {
                            'type': 'integer',
                            'description': 'Tamaño máximo del grupo',
                            'default': 3
                        },
                        'desired_capacity': {
                            'type': 'integer',
                            'description': 'Capacidad deseada del grupo',
                            'default': 1
                        },
                        'availability_zones': {
                            'type': 'array',
                            'description': 'Zonas de disponibilidad',
                            'items': {'type': 'string'}
                        }
                    },
                    'required': ['auto_scaling_group_name']
                },
                'function': self.create_autoscaling_group
            },
            {
                'name': 'autoscaling_update_group',
                'description': 'Actualiza un grupo de Auto Scaling existente',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'auto_scaling_group_name': {
                            'type': 'string',
                            'description': 'Nombre del grupo de Auto Scaling'
                        },
                        'min_size': {
                            'type': 'integer',
                            'description': 'Nuevo tamaño mínimo'
                        },
                        'max_size': {
                            'type': 'integer',
                            'description': 'Nuevo tamaño máximo'
                        },
                        'desired_capacity': {
                            'type': 'integer',
                            'description': 'Nueva capacidad deseada'
                        }
                    },
                    'required': ['auto_scaling_group_name']
                },
                'function': self.update_autoscaling_group
            },
            {
                'name': 'autoscaling_delete_group',
                'description': 'Elimina un grupo de Auto Scaling',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'auto_scaling_group_name': {
                            'type': 'string',
                            'description': 'Nombre del grupo de Auto Scaling a eliminar'
                        },
                        'force_delete': {
                            'type': 'boolean',
                            'description': 'Forzar eliminación incluso si hay instancias',
                            'default': False
                        }
                    },
                    'required': ['auto_scaling_group_name']
                },
                'function': self.delete_autoscaling_group
            },
            {
                'name': 'autoscaling_create_scaling_policy',
                'description': 'Crea una política de escalado para un grupo de Auto Scaling',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'auto_scaling_group_name': {
                            'type': 'string',
                            'description': 'Nombre del grupo de Auto Scaling'
                        },
                        'policy_name': {
                            'type': 'string',
                            'description': 'Nombre de la política'
                        },
                        'policy_type': {
                            'type': 'string',
                            'description': 'Tipo de política (SimpleScaling, StepScaling, TargetTrackingScaling)',
                            'enum': ['SimpleScaling', 'StepScaling', 'TargetTrackingScaling']
                        },
                        'adjustment_type': {
                            'type': 'string',
                            'description': 'Tipo de ajuste (solo para SimpleScaling/StepScaling)',
                            'enum': ['ChangeInCapacity', 'ExactCapacity', 'PercentChangeInCapacity']
                        },
                        'scaling_adjustment': {
                            'type': 'integer',
                            'description': 'Ajuste de escalado (para SimpleScaling)'
                        },
                        'target_value': {
                            'type': 'number',
                            'description': 'Valor objetivo (para TargetTrackingScaling)'
                        }
                    },
                    'required': ['auto_scaling_group_name', 'policy_name', 'policy_type']
                },
                'function': self.create_scaling_policy
            },
            {
                'name': 'autoscaling_delete_scaling_policy',
                'description': 'Elimina una política de escalado',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'auto_scaling_group_name': {
                            'type': 'string',
                            'description': 'Nombre del grupo de Auto Scaling'
                        },
                        'policy_name': {
                            'type': 'string',
                            'description': 'Nombre de la política a eliminar'
                        }
                    },
                    'required': ['auto_scaling_group_name', 'policy_name']
                },
                'function': self.delete_scaling_policy
            }
        ]

    def list_autoscaling_groups(self, group_names: Optional[List[str]] = None,
                               max_records: int = 100) -> Dict[str, Any]:
        """Lista grupos de Auto Scaling"""
        try:
            autoscaling = self._get_autoscaling_client()

            params = {'MaxRecords': max_records}
            if group_names:
                params['AutoScalingGroupNames'] = group_names

            response = autoscaling.describe_auto_scaling_groups(**params)

            groups = []
            for group in response.get('AutoScalingGroups', []):
                groups.append({
                    'auto_scaling_group_name': group['AutoScalingGroupName'],
                    'min_size': group['MinSize'],
                    'max_size': group['MaxSize'],
                    'desired_capacity': group['DesiredCapacity'],
                    'availability_zones': group.get('AvailabilityZones', []),
                    'launch_template': group.get('LaunchTemplate', {}),
                    'instances': [{
                        'instance_id': inst['InstanceId'],
                        'lifecycle_state': inst['LifecycleState'],
                        'health_status': inst['HealthStatus']
                    } for inst in group.get('Instances', [])]
                })

            return {
                'success': True,
                'auto_scaling_groups': groups,
                'total_count': len(groups)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error listando grupos de Auto Scaling: {str(e)}'
            }

    def create_autoscaling_group(self, auto_scaling_group_name: str,
                                launch_template_id: Optional[str] = None,
                                launch_template_name: Optional[str] = None,
                                min_size: int = 1, max_size: int = 3,
                                desired_capacity: int = 1,
                                availability_zones: Optional[List[str]] = None) -> Dict[str, Any]:
        """Crea un grupo de Auto Scaling"""
        try:
            autoscaling = self._get_autoscaling_client()

            # Preparar launch template
            launch_template = {}
            if launch_template_id:
                launch_template['LaunchTemplateId'] = launch_template_id
            elif launch_template_name:
                launch_template['LaunchTemplateName'] = launch_template_name

            params = {
                'AutoScalingGroupName': auto_scaling_group_name,
                'MinSize': min_size,
                'MaxSize': max_size,
                'DesiredCapacity': desired_capacity
            }

            if launch_template:
                params['LaunchTemplate'] = launch_template
            if availability_zones:
                params['AvailabilityZones'] = availability_zones

            autoscaling.create_auto_scaling_group(**params)

            return {
                'success': True,
                'message': f'Grupo de Auto Scaling {auto_scaling_group_name} creado exitosamente',
                'auto_scaling_group_name': auto_scaling_group_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando grupo de Auto Scaling: {str(e)}'
            }

    def update_autoscaling_group(self, auto_scaling_group_name: str,
                                min_size: Optional[int] = None,
                                max_size: Optional[int] = None,
                                desired_capacity: Optional[int] = None) -> Dict[str, Any]:
        """Actualiza un grupo de Auto Scaling"""
        try:
            autoscaling = self._get_autoscaling_client()

            params = {'AutoScalingGroupName': auto_scaling_group_name}
            if min_size is not None:
                params['MinSize'] = min_size
            if max_size is not None:
                params['MaxSize'] = max_size
            if desired_capacity is not None:
                params['DesiredCapacity'] = desired_capacity

            autoscaling.update_auto_scaling_group(**params)

            return {
                'success': True,
                'message': f'Grupo de Auto Scaling {auto_scaling_group_name} actualizado exitosamente',
                'auto_scaling_group_name': auto_scaling_group_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error actualizando grupo de Auto Scaling: {str(e)}'
            }

    def delete_autoscaling_group(self, auto_scaling_group_name: str,
                                force_delete: bool = False) -> Dict[str, Any]:
        """Elimina un grupo de Auto Scaling"""
        try:
            autoscaling = self._get_autoscaling_client()

            autoscaling.delete_auto_scaling_group(
                AutoScalingGroupName=auto_scaling_group_name,
                ForceDelete=force_delete
            )

            return {
                'success': True,
                'message': f'Grupo de Auto Scaling {auto_scaling_group_name} eliminado exitosamente',
                'auto_scaling_group_name': auto_scaling_group_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error eliminando grupo de Auto Scaling: {str(e)}'
            }

    def create_scaling_policy(self, auto_scaling_group_name: str, policy_name: str,
                             policy_type: str, adjustment_type: Optional[str] = None,
                             scaling_adjustment: Optional[int] = None,
                             target_value: Optional[float] = None) -> Dict[str, Any]:
        """Crea una política de escalado"""
        try:
            autoscaling = self._get_autoscaling_client()

            params = {
                'AutoScalingGroupName': auto_scaling_group_name,
                'PolicyName': policy_name,
                'PolicyType': policy_type
            }

            if policy_type in ['SimpleScaling', 'StepScaling']:
                if adjustment_type:
                    params['AdjustmentType'] = adjustment_type
                if scaling_adjustment is not None:
                    params['ScalingAdjustment'] = scaling_adjustment
            elif policy_type == 'TargetTrackingScaling':
                if target_value is not None:
                    params['TargetTrackingConfiguration'] = {
                        'TargetValue': target_value,
                        'PredefinedMetricSpecification': {
                            'PredefinedMetricType': 'ASGAverageCPUUtilization'
                        }
                    }

            response = autoscaling.put_scaling_policy(**params)

            return {
                'success': True,
                'message': f'Política de escalado {policy_name} creada exitosamente',
                'policy_arn': response.get('PolicyARN'),
                'auto_scaling_group_name': auto_scaling_group_name,
                'policy_name': policy_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error creando política de escalado: {str(e)}'
            }

    def delete_scaling_policy(self, auto_scaling_group_name: str, policy_name: str) -> Dict[str, Any]:
        """Elimina una política de escalado"""
        try:
            autoscaling = self._get_autoscaling_client()

            autoscaling.delete_policy(
                AutoScalingGroupName=auto_scaling_group_name,
                PolicyName=policy_name
            )

            return {
                'success': True,
                'message': f'Política de escalado {policy_name} eliminada exitosamente',
                'auto_scaling_group_name': auto_scaling_group_name,
                'policy_name': policy_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error eliminando política de escalado: {str(e)}'
            }