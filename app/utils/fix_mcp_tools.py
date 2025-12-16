#!/usr/bin/env python3
"""
Script para corregir automáticamente los archivos MCP tools
Convierte funciones que usan 'params: Dict[str, Any]' a **kwargs
"""

import os
import re
from pathlib import Path

def fix_function_signature(content, func_name):
    """
    Convierte la firma de una función de:
      def _func(self, params: Dict[str, Any]) -> Dict[str, Any]:
    a:
      def _func(self, **kwargs) -> Dict[str, Any]:
    """
    pattern = rf"(def {func_name}\(self,\s*)params:\s*Dict\[str,\s*Any\](\s*\)\s*->\s*Dict\[str,\s*Any\]:)"
    replacement = r"\1**kwargs\2"
    return re.sub(pattern, replacement, content)

def fix_params_access(content, func_name):
    """
    Convierte accesos a params dentro de una función de:
      params['key'] o params.get('key')
    a:
      kwargs.get('key')
    """
    # Encontrar el cuerpo de la función
    func_pattern = rf"(def {func_name}\(self,\s*\*\*kwargs\s*\)\s*->\s*Dict\[str,\s*Any\]:)(.*?)(?=\n    def |\nclass |\Z)"
    
    def replace_in_func(match):
        func_def = match.group(1)
        func_body = match.group(2)
        
        # Reemplazar params['key'] por kwargs.get('key')
        func_body = re.sub(r"params\['(\w+)'\]", r"kwargs.get('\1')", func_body)
        func_body = re.sub(r'params\["(\w+)"\]', r"kwargs.get('\1')", func_body)
        
        # Reemplazar 'key' in params por 'key' in kwargs
        func_body = re.sub(r"'(\w+)'\s+in\s+params", r"kwargs.get('\1')", func_body)
        func_body = re.sub(r'"(\w+)"\s+in\s+params', r'kwargs.get("\1")', func_body)
        
        # Reemplazar params.get('key') por kwargs.get('key')
        func_body = re.sub(r"params\.get\('(\w+)'", r"kwargs.get('\1'", func_body)
        func_body = re.sub(r'params\.get\("(\w+)"', r'kwargs.get("\1"', func_body)
        
        return func_def + func_body
    
    content = re.sub(func_pattern, replace_in_func, content, flags=re.DOTALL)
    return content

def fix_execute_tool_calls(content):
    """
    Convierte llamadas en execute_tool de:
      return self._func(parameters)
    a:
      return self._func(**parameters)
    """
    # Buscar dentro de execute_tool
    pattern = r"(def execute_tool\(self[^)]*\):.*?)(return self\.(_\w+)\((parameters|params)\))"
    
    def replace_call(match):
        before = match.group(1)
        full_call = match.group(2)
        func_name = match.group(3)
        param_name = match.group(4)
        
        return before + f"return self.{func_name}(**{param_name})"
    
    # Aplicar múltiples veces para capturar todas las llamadas
    max_iterations = 50
    for _ in range(max_iterations):
        new_content = re.sub(pattern, replace_call, content, flags=re.DOTALL)
        if new_content == content:
            break
        content = new_content
    
    return content

def fix_mcp_file(file_path):
    """Corrige un archivo MCP completo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Encontrar todas las funciones que usan params: Dict
    params_dict_funcs = re.findall(
        r'def (_\w+)\(self,\s*params:\s*Dict\[str,\s*Any\]\)',
        content
    )
    
    if not params_dict_funcs:
        return False, 0
    
    # Corregir cada función
    for func_name in params_dict_funcs:
        # 1. Cambiar la firma
        content = fix_function_signature(content, func_name)
        # 2. Cambiar los accesos a params
        content = fix_params_access(content, func_name)
    
    # 3. Corregir llamadas en execute_tool
    content = fix_execute_tool_calls(content)
    
    # Guardar solo si hubo cambios
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, len(params_dict_funcs)
    
    return False, 0

def main():
    """Corrige todos los archivos MCP del proyecto"""
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
    
    print(f"🔧 Corrigiendo {len(files_to_fix)} archivos MCP tools...\n")
    print("=" * 80)
    
    total_fixed = 0
    total_functions = 0
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
        
        fixed, func_count = fix_mcp_file(path)
        
        if fixed:
            rel_path = path.relative_to('app/mcp_server')
            print(f"✅ {rel_path}")
            print(f"   Corregidas {func_count} funciones")
            total_fixed += 1
            total_functions += func_count
        else:
            rel_path = path.relative_to('app/mcp_server')
            print(f"⚠️  {rel_path} - No se realizaron cambios")
    
    print("\n" + "=" * 80)
    print(f"\n📊 Resumen:")
    print(f"  - Archivos procesados: {len(files_to_fix)}")
    print(f"  - Archivos corregidos: {total_fixed}")
    print(f"  - Funciones corregidas: {total_functions}")
    print("\n✨ ¡Corrección completada!")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
