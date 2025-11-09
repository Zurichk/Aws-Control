import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Crear cliente EC2
ec2 = boto3.client(
    'ec2',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

print(f'Región configurada: {os.environ.get("AWS_DEFAULT_REGION", "us-east-1")}')
print(f'Región del cliente: {ec2.meta.region_name}')

# Verificar permisos básicos
try:
    # Intentar listar instancias
    instances = ec2.describe_instances()
    total_instances = sum(len(reservation['Instances']) for reservation in instances.get('Reservations', []))
    print(f'✅ Permiso describe_instances: OK ({total_instances} instancias encontradas)')

    # Verificar si hay instancias sin tag Environment
    active_instances = []
    for reservation in instances.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            if instance.get('State', {}).get('Name') != 'terminated':
                active_instances.append(instance.get('InstanceId'))

    print(f'Instancias activas: {len(active_instances)}')

    # Buscar instancias con tag Environment
    tagged_response = ec2.describe_instances(
        Filters=[{'Name': 'tag-key', 'Values': ['Environment']}]
    )
    tagged_instances = []
    for reservation in tagged_response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            if instance.get('State', {}).get('Name') != 'terminated':
                tagged_instances.append(instance.get('InstanceId'))

    print(f'Instancias con tag Environment: {len(tagged_instances)}')

    # Calcular instancias sin tag
    untagged = [iid for iid in active_instances if iid not in tagged_instances]
    print(f'Instancias sin tag Environment: {len(untagged)}')

    if untagged:
        print(f'IDs sin tag: {untagged[:3]}...')  # Mostrar primeros 3

        # Intentar terminar UNA instancia para probar permisos
        test_instance = untagged[0]
        print(f'🔄 Probando terminación de instancia: {test_instance}')

        try:
            response = ec2.terminate_instances(InstanceIds=[test_instance])
            print('✅ Permiso terminate_instances: OK')
            print(f'Respuesta: {response.get("TerminatingInstances", [])}')
        except Exception as e:
            print(f'❌ Error al terminar instancia: {str(e)}')
            if 'UnauthorizedOperation' in str(e):
                print('🔒 Problema de permisos IAM - falta ec2:TerminateInstances')
            elif 'InvalidInstanceId' in str(e):
                print('🔍 Instancia no encontrada o ya terminada')
            else:
                print(f'Error desconocido: {e}')
    else:
        print('ℹ️ No hay instancias sin tag Environment para probar terminación')

except Exception as e:
    print(f'❌ Error general: {str(e)}')
    if 'InvalidAccessKeyId' in str(e):
        print('🔑 Access Key inválida')
    elif 'SignatureDoesNotMatch' in str(e):
        print('🔑 Secret Key inválida')
    elif 'UnauthorizedOperation' in str(e):
        print('🔒 Problemas de permisos IAM')
    else:
        print(f'Error desconocido: {e}')