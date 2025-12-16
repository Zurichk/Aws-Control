#!/usr/bin/env python3
"""
Script para corregir asignaciones inválidas con .get() en archivos MCP tools.
Busca patrones como: var_kwargs.get('key') = value
Y los reemplaza por: var_kwargs['key'] = value
"""

import re
from pathlib import Path

def fix_invalid_assignments(file_path):
    """Corrige asignaciones inválidas en un archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patrón: xxx_kwargs.get('key') = value
    # Reemplazar por: xxx_kwargs['key'] = value
    pattern = r"(\w+_kwargs)\.get\((['\"])([^'\"]+)\2\)\s*=\s*"
    replacement = r"\1[\2\3\2] = "
    
    content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = [
        'app/mcp_server/Almacenamiento/s3_mcp_tools.py',
        'app/mcp_server/Base_de_Datos/dynamodb_mcp_tools.py',
        'app/mcp_server/Base_de_Datos/rds_mcp_tools.py',
    ]
    
    fixed_count = 0
    for file_path in files:
        if Path(file_path).exists():
            if fix_invalid_assignments(file_path):
                print(f"✅ Corregido: {file_path}")
                fixed_count += 1
            else:
                print(f"⚪ Sin cambios: {file_path}")
        else:
            print(f"❌ No existe: {file_path}")
    
    print(f"\n🎉 Total archivos modificados: {fixed_count}")

if __name__ == '__main__':
    main()
