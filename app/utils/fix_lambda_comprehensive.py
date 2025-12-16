#!/usr/bin/env python3
"""
Script robusto para corregir errores de sintaxis en lambda_mcp_tools.py
"""

import re

def fix_lambda_file():
    filepath = 'app/mcp_server/Computo/lambda_mcp_tools.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Cambiar lambda_kwargs.get('key') = value a lambda_kwargs['key'] = value
    content = re.sub(
        r"(\s+)lambda_kwargs\.get\((['\"])([^'\"]+)\2\)\s*=",
        r"\1lambda_kwargs[\2\3\2] =",
        content
    )
    
    # 2. Cambiar kwargs.get('key') a kwargs.get("key") SOLO en f-strings
    # Encuentra f'...{kwargs.get('key')}...' y cambia a f'...{kwargs.get("key")}...'
    def fix_fstring(match):
        fstring = match.group(0)
        # Reemplazar kwargs.get('xxx') por kwargs.get("xxx")
        fixed = re.sub(r"kwargs\.get\('([^']+)'\)", r'kwargs.get("\1")', fstring)
        return fixed
    
    # Buscar f-strings y aplicar el fix
    content = re.sub(
        r"f'[^']*\{[^}]*kwargs\.get\('[^']+'\)[^}]*\}[^']*'",
        fix_fstring,
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ lambda_mcp_tools.py corregido")

if __name__ == '__main__':
    fix_lambda_file()
