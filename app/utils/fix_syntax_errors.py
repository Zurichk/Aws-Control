#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en archivos MCP
Reemplaza xxx_kwargs.get('key') = value por xxx_kwargs['key'] = value
"""

import re
from pathlib import Path

def fix_file(file_path):
    """Corrige asignaciones inválidas usando .get()"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Patrón: xxx_kwargs.get('key') = value
    # Reemplazar por: xxx_kwargs['key'] = value
    content = re.sub(
        r'(\w+_kwargs)\.get\(([^)]+)\)\s*=',
        r'\1[\2] =',
        content
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files_to_fix = [
        'app/mcp_server/Computo/lambda_mcp_tools.py',
        'app/mcp_server/Seguridad/iam_mcp_tools.py',
        'app/mcp_server/Redes/api_gateway_mcp_tools.py',
        'app/mcp_server/Integracion/cloudformation_mcp_tools.py',
        'app/mcp_server/Gestion/cloudwatch_mcp_tools.py',
        'app/mcp_server/Gestion/systems_manager_mcp_tools.py',
    ]
    
    print("🔧 Corrigiendo errores de sintaxis...\n")
    
    fixed_count = 0
    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  No existe: {file_path}")
            continue
        
        if fix_file(path):
            print(f"✅ {file_path}")
            fixed_count += 1
        else:
            print(f"⏭️  {file_path} - Sin cambios")
    
    print(f"\n✨ Corrección completada: {fixed_count} archivos modificados")

if __name__ == '__main__':
    main()
