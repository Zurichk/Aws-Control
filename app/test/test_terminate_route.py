"""Script de prueba para verificar la función terminate_untagged"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importar la app Flask
from app.app import create_app

print("✅ Creando aplicación Flask...")
app = create_app()

print("✅ Configurando contexto de aplicación...")
with app.test_request_context():
    from flask import url_for
    print(f"URL de terminate_untagged: {url_for('ec2.terminate_untagged')}")
    
print("\n✅ Simulando petición POST a terminate_untagged...")
with app.test_client() as client:
    # Simular POST al endpoint
    response = client.post('/ec2/terminate-untagged', follow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Location: {response.headers.get('Location', 'N/A')}")
    print(f"Response: {response.data.decode('utf-8')[:200]}")
    
    if response.status_code == 302:
        print("✅ La función redirige correctamente")
        # Seguir el redirect para ver los mensajes flash
        response2 = client.get(response.headers.get('Location'))
        print(f"Contenido después del redirect (primeros 500 chars): {response2.data.decode('utf-8')[:500]}")
