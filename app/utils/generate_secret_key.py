#!/usr/bin/env python3
"""
Script para generar un SECRET_KEY seguro para Flask

Uso:
    python generate_secret_key.py

Este script genera una clave aleatoria de 64 caracteres hexadecimales
(256 bits de entropía) para usar como SECRET_KEY en Flask.

¿Para qué sirve el SECRET_KEY?
- Firma las cookies de sesión de Flask
- Impide que usuarios maliciosos falsifiquen cookies
- Si cambias el SECRET_KEY, todas las sesiones se invalidan

Importante:
- Guarda el SECRET_KEY generado en un lugar seguro
- NO lo compartas en repositorios públicos
- Usa el MISMO valor en todas las instancias de tu aplicación
"""

import secrets

def generate_secret_key():
    """Genera un SECRET_KEY seguro de 64 caracteres hexadecimales"""
    return secrets.token_hex(32)

if __name__ == '__main__':
    secret_key = generate_secret_key()
    
    print("=" * 70)
    print("🔑 SECRET_KEY generado para Flask")
    print("=" * 70)
    print()
    print("Tu SECRET_KEY seguro es:")
    print()
    print(f"    {secret_key}")
    print()
    print("=" * 70)
    print()
    print("📋 Instrucciones:")
    print()
    print("1. Copia el SECRET_KEY de arriba")
    print("2. En Coolify, ve a tu aplicación → Environment Variables")
    print("3. Agrega una variable:")
    print(f"   - Nombre: SECRET_KEY")
    print(f"   - Valor: {secret_key}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - NO cambies este valor después del despliegue")
    print("   - Guárdalo en un lugar seguro")
    print("   - NO lo compartas en repositorios públicos")
    print()
    print("=" * 70)
