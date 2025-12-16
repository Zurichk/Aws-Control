#!/usr/bin/env python3
"""
Corrige f-strings con kwargs.get() que tienen comillas mal anidadas
"""

import re
from pathlib import Path

def fix_fstrings(content):
    """Corrige f-strings con kwargs.get('key') usando comillas dobles"""
    # Patrón para encontrar f'...{kwargs.get('key')}...'
    # Y reemplazar por f'...{kwargs.get("key")}...'
    pattern = r"(f'[^']*\{kwargs\.get\()'([^']+)'(\)\}[^']*')"
    replacement = r'\1"\2"\3'
    return re.sub(pattern, replacement, content)

def main():
    file_path = Path('app/mcp_server/Computo/lambda_mcp_tools.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = fix_fstrings(content)
    
    if fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ F-strings corregidos en {file_path}")
    else:
        print(f"⏭️  Sin cambios necesarios")

if __name__ == '__main__':
    main()
