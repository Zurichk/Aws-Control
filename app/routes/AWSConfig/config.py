"""
Rutas web para AWS Config
Gestión de configuración, compliance y remediation
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
from app.utils.aws_client import get_aws_client

config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def index():
    """Página principal de AWS Config"""
    return render_template('Config/index.html')


@config_bp.route('/configuration-items')
def configuration_items():
    """Lista los elementos de configuración"""
    try:
        config = get_aws_client('config')

        # Primero verificar si Config está habilitado
        try:
            recorder_response = config.describe_configuration_recorders()
            if not recorder_response.get('ConfigurationRecorders'):
                return render_template('Config/configuration_items.html',
                                     configuration_items=[],
                                     error="AWS Config no está habilitado en esta cuenta/región")
        except Exception as recorder_error:
            return render_template('Config/configuration_items.html',
                                 configuration_items=[],
                                 error=f"AWS Config no está disponible: {str(recorder_error)}")

        # Intentar obtener elementos de configuración usando una API más confiable
        try:
            # Usar get_discovered_resource_counts para verificar si hay datos
            counts_response = config.get_discovered_resource_counts()
            total_resources = sum(count.get('count', 0) for count in counts_response.get('resourceCounts', []))

            if total_resources == 0:
                return render_template('Config/configuration_items.html',
                                     configuration_items=[],
                                     error="No se encontraron recursos configurados en AWS Config")

            # Obtener algunos elementos de configuración de ejemplo
            items = []
            resource_types = ['AWS::EC2::Instance', 'AWS::S3::Bucket', 'AWS::IAM::Role']

            for resource_type in resource_types:
                try:
                    response = config.list_discovered_resources(
                        resourceType=resource_type,
                        limit=10
                    )

                    for item in response.get('resourceIdentifiers', []):
                        items.append({
                            'resourceType': item.get('resourceType'),
                            'resourceId': item.get('resourceId'),
                            'resourceName': item.get('resourceName', 'N/A'),
                            'awsRegion': item.get('resourceRegion', 'N/A'),
                            'configurationStateId': 'active',  # Simulado
                            'configurationItemCaptureTime': 'N/A'  # Simulado
                        })

                        if len(items) >= 50:  # Limitar a 50 elementos
                            break

                    if len(items) >= 50:
                        break

                except Exception as type_error:
                    # Continuar con otros tipos si uno falla
                    continue

            return render_template('Config/configuration_items.html', configuration_items=items)

        except Exception as e:
            # Si falla, intentar método alternativo o mostrar mensaje informativo
            return render_template('Config/configuration_items.html',
                                 configuration_items=[],
                                 error=f"Error obteniendo elementos de configuración: {str(e)}")

    except Exception as e:
        return render_template('Config/configuration_items.html',
                             configuration_items=[],
                             error=f"Error general: {str(e)}")


@config_bp.route('/compliance-rules')
def compliance_rules():
    """Lista las reglas de compliance"""
    try:
        config = get_aws_client('config')

        # Obtener reglas de Config
        rules_response = config.describe_config_rules()
        rules = rules_response.get('ConfigRules', [])

        # Obtener estado de compliance para cada regla
        compliance_details = []
        for rule in rules:
            try:
                compliance_response = config.describe_compliance_by_config_rule(
                    ConfigRuleNames=[rule['ConfigRuleName']]
                )

                rule_info = {
                    'name': rule['ConfigRuleName'],
                    'description': rule.get('Description', 'N/A'),
                    'state': rule.get('ConfigRuleState', 'N/A'),
                    'compliance_type': 'N/A',
                    'evaluation_period': 'N/A'
                }

                if compliance_response.get('ComplianceByConfigRules'):
                    compliance = compliance_response['ComplianceByConfigRules'][0]
                    rule_info['compliance_type'] = compliance.get('Compliance', {}).get('ComplianceType', 'N/A')

                compliance_details.append(rule_info)
            except Exception as e:
                compliance_details.append({
                    'name': rule['ConfigRuleName'],
                    'description': rule.get('Description', 'N/A'),
                    'state': rule.get('ConfigRuleState', 'N/A'),
                    'compliance_type': 'Error',
                    'evaluation_period': 'N/A'
                })

        return render_template('Config/compliance_rules.html', rules=compliance_details)
    except Exception as e:
        flash(f'Error obteniendo reglas de compliance: {str(e)}', 'error')
        return render_template('Config/compliance_rules.html', rules=[])


@config_bp.route('/remediation-actions')
def remediation_actions():
    """Lista las acciones de remediation"""
    try:
        config = get_aws_client('config')

        # Obtener acciones de remediation
        response = config.describe_remediation_configurations()

        actions = []
        for action in response.get('RemediationConfigurations', []):
            actions.append({
                'name': action.get('ConfigRuleName'),
                'target_type': action.get('TargetType', 'N/A'),
                'target_id': action.get('TargetId', 'N/A'),
                'parameters': action.get('Parameters', {}),
                'automatic': action.get('Automatic', False)
            })

        return render_template('Config/remediation_actions.html', actions=actions)
    except Exception as e:
        flash(f'Error obteniendo acciones de remediation: {str(e)}', 'error')
        return render_template('Config/remediation_actions.html', actions=[])


@config_bp.route('/create-rule', methods=['GET', 'POST'])
def create_rule():
    """Crea una nueva regla de Config"""
    if request.method == 'POST':
        try:
            rule_name = request.form.get('rule_name')
            description = request.form.get('description')
            resource_type = request.form.get('resource_type')
            rule_lambda_arn = request.form.get('rule_lambda_arn')

            config = get_aws_client('config')

            rule_config = {
                'ConfigRuleName': rule_name,
                'Description': description,
                'Scope': {
                    'ComplianceResourceTypes': [resource_type] if resource_type != 'ALL' else []
                }
            }

            if rule_lambda_arn:
                rule_config['Source'] = {
                    'Owner': 'CUSTOM_LAMBDA',
                    'SourceIdentifier': rule_lambda_arn,
                    'SourceDetails': [{
                        'EventSource': 'aws.config',
                        'MessageType': 'ConfigurationItemChangeNotification'
                    }]
                }
            else:
                # Regla managed
                rule_config['Source'] = {
                    'Owner': 'AWS',
                    'SourceIdentifier': request.form.get('managed_rule_id')
                }

            config.put_config_rule(ConfigRule=rule_config)

            flash(f'Regla \"{rule_name}\" creada exitosamente', 'success')
            return redirect(url_for('config.compliance_rules'))
        except Exception as e:
            flash(f'Error creando regla: {str(e)}', 'error')

    return render_template('Config/create_rule.html')


@config_bp.route('/rule/<rule_name>')
def rule_detail(rule_name):
    """Detalles de una regla específica"""
    try:
        config = get_aws_client('config')

        # Obtener detalles de la regla
        rule_response = config.describe_config_rules(ConfigRuleNames=[rule_name])
        rule = rule_response.get('ConfigRules', [{}])[0]

        # Obtener compliance
        compliance_response = config.describe_compliance_by_config_rule(
            ConfigRuleNames=[rule_name]
        )
        compliance = compliance_response.get('ComplianceByConfigRules', [{}])[0]

        # Obtener evaluaciones recientes
        evaluations_response = config.get_compliance_details_by_config_rule(
            ConfigRuleName=rule_name,
            Limit=20
        )

        rule_detail = {
            'name': rule.get('ConfigRuleName'),
            'description': rule.get('Description', 'N/A'),
            'state': rule.get('ConfigRuleState', 'N/A'),
            'compliance_type': compliance.get('Compliance', {}).get('ComplianceType', 'N/A'),
            'evaluations': evaluations_response.get('EvaluationResults', [])
        }

        return render_template('Config/rule_detail.html', rule=rule_detail)
    except Exception as e:
        flash(f'Error obteniendo detalles de la regla: {str(e)}', 'error')
        return redirect(url_for('config.compliance_rules'))


@config_bp.route('/configuration-recorder')
def configuration_recorder():
    """Estado del Configuration Recorder"""
    try:
        config = get_aws_client('config')

        # Obtener recorders
        recorders_response = config.describe_configuration_recorders()
        recorders = recorders_response.get('ConfigurationRecorders', [])

        # Obtener estado
        status_response = config.describe_configuration_recorder_status()
        status = status_response.get('ConfigurationRecordersStatus', [])

        recorder_info = {
            'recorders': recorders,
            'status': status
        }

        return render_template('Config/configuration_recorder.html', recorder=recorder_info)
    except Exception as e:
        flash(f'Error obteniendo estado del recorder: {str(e)}', 'error')
        return render_template('Config/configuration_recorder.html', recorder={'recorders': [], 'status': []})
