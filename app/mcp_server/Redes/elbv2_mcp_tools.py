import boto3
import os
from typing import Dict, List, Any, Optional

class ELBv2MCPTools:
    """Herramientas MCP para gestión de ELBv2 Load Balancers"""

    def __init__(self):
        self.client_name = 'elbv2'

    def _get_client(self):
        """Obtener cliente de ELBv2"""
        return boto3.client(
            self.client_name,
            region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        )

    def list_load_balancers(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todos los load balancers de ELBv2

        Args:
            params: Parámetros opcionales
                - names: Lista de nombres de load balancers específicos

        Returns:
            Dict con lista de load balancers
        """
        try:
            elbv2 = self._get_client()
            kwargs = {}
            if params and 'names' in params:
                kwargs['Names'] = params['names']

            response = elbv2.describe_load_balancers(**kwargs)

            load_balancers = []
            for lb in response['LoadBalancers']:
                load_balancers.append({
                    'name': lb['LoadBalancerName'],
                    'arn': lb['LoadBalancerArn'],
                    'dns_name': lb['DNSName'],
                    'state': lb['State']['Code'],
                    'type': lb['Type'],
                    'scheme': lb['Scheme'],
                    'vpc_id': lb.get('VpcId'),
                    'created_time': lb.get('CreatedTime', '').isoformat() if lb.get('CreatedTime') else None
                })

            return {
                'success': True,
                'load_balancers': load_balancers,
                'total_count': len(load_balancers)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_load_balancer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo load balancer

        Args:
            params: Parámetros del load balancer
                - name (str): Nombre del load balancer
                - subnets (list): Lista de subnet IDs
                - security_groups (list, opcional): Lista de security group IDs
                - scheme (str, opcional): 'internet-facing' o 'internal' (default: internet-facing)
                - type (str, opcional): 'application' o 'network' (default: application)

        Returns:
            Dict con resultado de la creación
        """
        try:
            required_params = ['name', 'subnets']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            elbv2 = self._get_client()

            # Configurar load balancer
            lb_config = {
                'Name': params['name'],
                'Subnets': params['subnets'],
                'Scheme': params.get('scheme', 'internet-facing'),
                'Type': params.get('type', 'application')
            }

            if 'security_groups' in params:
                lb_config['SecurityGroups'] = params['security_groups']

            response = elbv2.create_load_balancer(**lb_config)

            return {
                'success': True,
                'load_balancer_arn': response['LoadBalancers'][0]['LoadBalancerArn'],
                'load_balancer_name': response['LoadBalancers'][0]['LoadBalancerName'],
                'dns_name': response['LoadBalancers'][0]['DNSName'],
                'state': response['LoadBalancers'][0]['State']['Code']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_load_balancer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina un load balancer

        Args:
            params: Parámetros de eliminación
                - load_balancer_arn (str): ARN del load balancer a eliminar

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            required_params = ['load_balancer_arn']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            elbv2 = self._get_client()
            elbv2.delete_load_balancer(LoadBalancerArn=params['load_balancer_arn'])

            return {
                'success': True,
                'message': f'Load Balancer {params["load_balancer_arn"]} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_target_groups(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todos los target groups

        Args:
            params: Parámetros opcionales
                - load_balancer_arn: ARN del load balancer para filtrar target groups
                - names: Lista de nombres de target groups específicos

        Returns:
            Dict con lista de target groups
        """
        try:
            elbv2 = self._get_client()
            kwargs = {}
            if params:
                if 'load_balancer_arn' in params:
                    kwargs['LoadBalancerArn'] = params['load_balancer_arn']
                if 'names' in params:
                    kwargs['Names'] = params['names']

            response = elbv2.describe_target_groups(**kwargs)

            target_groups = []
            for tg in response['TargetGroups']:
                target_groups.append({
                    'name': tg['TargetGroupName'],
                    'arn': tg['TargetGroupArn'],
                    'protocol': tg['Protocol'],
                    'port': tg['Port'],
                    'vpc_id': tg['VpcId'],
                    'health_check_path': tg.get('HealthCheckPath', '/'),
                    'health_check_port': tg.get('HealthCheckPort', 'traffic-port'),
                    'healthy_threshold_count': tg.get('HealthyThresholdCount', 5),
                    'unhealthy_threshold_count': tg.get('UnhealthyThresholdCount', 2)
                })

            return {
                'success': True,
                'target_groups': target_groups,
                'total_count': len(target_groups)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_target_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo target group

        Args:
            params: Parámetros del target group
                - name (str): Nombre del target group
                - protocol (str, opcional): Protocolo (HTTP, HTTPS, TCP, etc.) (default: HTTP)
                - port (int, opcional): Puerto (default: 80)
                - vpc_id (str): ID de la VPC
                - health_check_path (str, opcional): Path para health check (default: /)

        Returns:
            Dict con resultado de la creación
        """
        try:
            required_params = ['name', 'vpc_id']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            elbv2 = self._get_client()

            # Configurar target group
            tg_config = {
                'Name': params['name'],
                'Protocol': params.get('protocol', 'HTTP'),
                'Port': int(params.get('port', 80)),
                'VpcId': params['vpc_id']
            }

            if 'health_check_path' in params:
                tg_config['HealthCheckPath'] = params['health_check_path']

            response = elbv2.create_target_group(**tg_config)

            return {
                'success': True,
                'target_group_arn': response['TargetGroups'][0]['TargetGroupArn'],
                'target_group_name': response['TargetGroups'][0]['TargetGroupName'],
                'protocol': response['TargetGroups'][0]['Protocol'],
                'port': response['TargetGroups'][0]['Port']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_target_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina un target group

        Args:
            params: Parámetros de eliminación
                - target_group_arn (str): ARN del target group a eliminar

        Returns:
            Dict con resultado de la eliminación
        """
        try:
            required_params = ['target_group_arn']
            for param in required_params:
                if param not in params:
                    return {
                        'success': False,
                        'error': f'Parámetro requerido faltante: {param}'
                    }

            elbv2 = self._get_client()
            elbv2.delete_target_group(TargetGroupArn=params['target_group_arn'])

            return {
                'success': True,
                'message': f'Target Group {params["target_group_arn"]} eliminado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }