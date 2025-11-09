"""Test rápido de get_aws_client con session token"""
import sys
sys.path.insert(0, 'e:\\Proyectos\\EntornosPython\\AWS-control')

from dotenv import load_dotenv
load_dotenv()

from app.utils.aws_client import get_aws_client

print("🔄 Probando get_aws_client con session token...")

try:
    # Probar con EC2
    ec2 = get_aws_client('ec2')
    print(f"✅ Cliente EC2 creado")
    
    # Intentar listar instancias
    response = ec2.describe_instances()
    total = sum(len(r['Instances']) for r in response['Reservations'])
    print(f"✅ describe_instances funcionó - {total} instancias encontradas")
    
    # Probar con STS para verificar identidad
    sts = get_aws_client('sts')
    identity = sts.get_caller_identity()
    print(f"✅ Identidad verificada: {identity['Arn']}")
    
    print("\n🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
    print("   Ahora la aplicación Flask puede acceder a AWS con las credenciales del laboratorio")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
