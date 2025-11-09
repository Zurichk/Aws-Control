"""
Script para verificar credenciales AWS del laboratorio
"""
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("VERIFICACIÓN DE CREDENCIALES AWS")
print("=" * 60)

# Mostrar configuración (parcialmente oculta por seguridad)
access_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
session_token = os.environ.get('AWS_SESSION_TOKEN', '')
region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

print(f"\n✓ Access Key ID: {access_key[:10]}...{access_key[-4:] if len(access_key) > 14 else ''}")
print(f"✓ Secret Key: {'*' * 20}{secret_key[-4:] if len(secret_key) > 4 else ''}")
print(f"✓ Session Token: {'Configurado' if session_token else 'NO CONFIGURADO ❌'} ({len(session_token)} chars)")
print(f"✓ Región: {region}")

print("\n" + "=" * 60)
print("PRUEBA DE CONEXIÓN")
print("=" * 60)

# Intentar conectar con STS para verificar identidad
try:
    sts = boto3.client(
        'sts',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name=region
    )
    
    print("\n🔄 Verificando identidad con STS...")
    identity = sts.get_caller_identity()
    
    print("\n✅ CREDENCIALES VÁLIDAS")
    print(f"   Account: {identity['Account']}")
    print(f"   User ARN: {identity['Arn']}")
    print(f"   User ID: {identity['UserId']}")
    
except Exception as e:
    print(f"\n❌ ERROR DE AUTENTICACIÓN")
    print(f"   {str(e)}")
    print("\n🔍 POSIBLES CAUSAS:")
    print("   1. Las credenciales del laboratorio expiraron")
    print("   2. El session token es incorrecto o falta")
    print("   3. Hay espacios o saltos de línea extras en .env")
    print("   4. La región no es correcta para el laboratorio")
    print("\n💡 SOLUCIÓN:")
    print("   Ve a tu laboratorio AWS y copia nuevamente las credenciales")
    print("   Asegúrate de incluir las 3 líneas completas (access key, secret key, session token)")
    exit(1)

# Si llegamos aquí, las credenciales son válidas
print("\n" + "=" * 60)
print("PRUEBA DE EC2")
print("=" * 60)

try:
    ec2 = boto3.client(
        'ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name=region
    )
    
    print(f"\n🔄 Listando instancias en {region}...")
    response = ec2.describe_instances()
    
    total_instances = 0
    for reservation in response['Reservations']:
        total_instances += len(reservation['Instances'])
    
    print(f"\n✅ CONEXIÓN EC2 EXITOSA")
    print(f"   Instancias encontradas: {total_instances}")
    
    if total_instances > 0:
        print("\n📋 INSTANCIAS:")
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                state = instance['State']['Name']
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                print(f"   • {instance_id} ({instance_type}) - Estado: {state}")
    
except Exception as e:
    print(f"\n❌ ERROR AL LISTAR INSTANCIAS EC2")
    print(f"   {str(e)}")

print("\n" + "=" * 60)
