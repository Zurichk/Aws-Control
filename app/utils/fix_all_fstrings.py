#!/usr/bin/env python3
"""
Corrige todos los f-strings con kwargs.get() en archivos MCP
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Corrige f-strings en un archivo"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Encontrar y corregir f-strings con kwargs.get('xxx')
    # Usar regex más simple: buscar cualquier f' string que contenga kwargs.get('...') 
    # y reemplazar las comillas simples internas por dobles
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Si la línea es un f-string con kwargs.get()
        if line.strip().startswith("'message':") and "f'" in line and "kwargs.get(" in line:
            # Reemplazar kwargs.get('xxx') por kwargs.get("xxx")
            line = re.sub(r"kwargs\.get\('([^']+)'\)", r'kwargs.get("\1")', line)
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = [
        'app/mcp_server/Seguridad/iam_mcp_tools.py',
        'app/mcp_server/Redes/api_gateway_mcp_tools.py',
        'app/mcp_server/Integracion/cloudformation_mcp_tools.py',
        'app/mcp_server/Gestion/cloudwatch_mcp_tools.py',
    ]
    
    print("🔧 Corrigiendo f-strings...")
    
    for file in files:
        path = Path(file)
        if path.exists():
            if fix_file(path):
                print(f"✅ {file}")
            else:
                print(f"⏭️  {file} - Sin cambios")
        else:
            print(f"❌ No existe: {file}")
    
    print("\n✨ Completado")

if __name__ == '__main__':
    main()
