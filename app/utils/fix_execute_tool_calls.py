#!/usr/bin/env python3
"""
Script mejorado para corregir las llamadas en execute_tool
"""

import re
from pathlib import Path

def fix_execute_tool_block(content):
    """Corrige un bloque completo de execute_tool"""
    
    # Patrón para encontrar el método execute_tool completo
    pattern = r'(def execute_tool\(self, tool_name: str, parameters: Dict\[str, Any\]\) -> Dict\[str, Any\]:.*?(?=\n    def [^_]|\nclass |\Z))'
    
    def fix_calls(match):
        block = match.group(0)
        # Reemplazar todas las llamadas que NO tengan **
        # return self._nombre(parameters) -> return self._nombre(**parameters)
        fixed = re.sub(
            r'return self\.(_\w+)\((parameters|params)\)(?!\*)',
            r'return self.\1(**\2)',
            block
        )
        return fixed
    
    return re.sub(pattern, fix_calls, content, flags=re.DOTALL)

def main():
    files_to_fix = [
        'app/mcp_server/Almacenamiento/s3_mcp_tools.py',
        'app/mcp_server/Base_de_Datos/dynamodb_mcp_tools.py',
        'app/mcp_server/Base_de_Datos/rds_mcp_tools.py',
        'app/mcp_server/Computo/lambda_mcp_tools.py',
        'app/mcp_server/Gestion/cloudwatch_mcp_tools.py',
        'app/mcp_server/Gestion/systems_manager_mcp_tools.py',
        'app/mcp_server/Integracion/cloudformation_mcp_tools.py',
        'app/mcp_server/Redes/api_gateway_mcp_tools.py',
        'app/mcp_server/Seguridad/iam_mcp_tools.py',
    ]
    
    print("🔧 Corrigiendo llamadas en execute_tool...\n")
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        content = fix_execute_tool_block(content)
        
        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Contar cambios
            changes = len(re.findall(r'\*\*parameters\)', content)) - len(re.findall(r'\*\*parameters\)', original))
            if changes > 0:
                rel_path = path.relative_to('app/mcp_server')
                print(f"✅ {rel_path} - {changes} llamadas corregidas")
    
    print("\n✨ ¡Corrección de llamadas completada!")

if __name__ == '__main__':
    main()
