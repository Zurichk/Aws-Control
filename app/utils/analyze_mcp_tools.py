#!/usr/bin/env python3
"""
Script para analizar todos los archivos MCP tools y detectar problemas
de inconsistencia en el paso de parámetros
"""

import os
import re
from pathlib import Path

def analyze_mcp_file(file_path):
    """Analiza un archivo MCP para detectar problemas de parámetros"""
    problems = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar funciones execute_tool
    execute_tool_matches = re.finditer(
        r'def execute_tool\(self[^)]*\):[^}]+?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    for match in execute_tool_matches:
        execute_block = match.group(0)
        
        # Buscar llamadas a funciones internas
        # Patrón: return self._function_name(parameters) o self._function_name(params)
        calls_with_dict = re.findall(
            r'return self\.(_\w+)\((parameters|params)\)',
            execute_block
        )
        
        # Buscar llamadas correctas con **
        calls_with_unpack = re.findall(
            r'return self\.(_\w+)\(\*\*(parameters|params)\)',
            execute_block
        )
        
        if calls_with_dict:
            # Verificar si las funciones llamadas esperan **kwargs o params
            for func_name, _ in calls_with_dict:
                # Buscar la definición de la función
                func_pattern = rf'def {func_name}\(self,\s*([^)]+)\)'
                func_match = re.search(func_pattern, content)
                
                if func_match:
                    params_def = func_match.group(1)
                    
                    # Si la función usa **kwargs o parámetros individuales, hay problema
                    if '**kwargs' in params_def or ('=' in params_def and 'params' not in params_def):
                        problems.append({
                            'type': 'parameter_mismatch',
                            'function': func_name,
                            'issue': f'Función {func_name} se llama con dict pero espera **kwargs',
                            'params': params_def
                        })
                    # Si la función espera params: Dict pero no se usa, también es problema
                    elif 'params: Dict' in params_def or 'params:Dict' in params_def:
                        # Esto está OK, pero verificamos que sea consistente
                        pass
    
    # Buscar funciones que usan params: Dict[str, Any]
    params_dict_funcs = re.findall(
        r'def (_\w+)\(self,\s*params:\s*Dict\[str,\s*Any\]\)',
        content
    )
    
    if params_dict_funcs:
        problems.append({
            'type': 'uses_params_dict',
            'functions': params_dict_funcs,
            'count': len(params_dict_funcs)
        })
    
    return problems

def main():
    """Analiza todos los archivos MCP del proyecto"""
    mcp_dir = Path('app/mcp_server')
    
    all_files = list(mcp_dir.rglob('*_mcp_tools.py'))
    
    print(f"🔍 Analizando {len(all_files)} archivos MCP tools...\n")
    print("=" * 80)
    
    files_with_problems = []
    total_problems = 0
    
    for file_path in sorted(all_files):
        problems = analyze_mcp_file(file_path)
        
        if problems:
            files_with_problems.append((file_path, problems))
            total_problems += len(problems)
            
            rel_path = file_path.relative_to('app/mcp_server')
            print(f"\n⚠️  {rel_path}")
            print("-" * 80)
            
            for problem in problems:
                if problem['type'] == 'parameter_mismatch':
                    print(f"  ❌ {problem['function']}")
                    print(f"     {problem['issue']}")
                    print(f"     Parámetros: {problem['params']}")
                elif problem['type'] == 'uses_params_dict':
                    print(f"  ⚠️  {problem['count']} funciones usan 'params: Dict[str, Any]':")
                    for func in problem['functions'][:5]:  # Mostrar solo las primeras 5
                        print(f"     - {func}")
                    if len(problem['functions']) > 5:
                        print(f"     ... y {len(problem['functions']) - 5} más")
    
    print("\n" + "=" * 80)
    print(f"\n📊 Resumen:")
    print(f"  - Archivos analizados: {len(all_files)}")
    print(f"  - Archivos con problemas: {len(files_with_problems)}")
    print(f"  - Problemas encontrados: {total_problems}")
    
    if files_with_problems:
        print(f"\n❌ Se encontraron problemas en:")
        for file_path, _ in files_with_problems:
            rel_path = file_path.relative_to('app/mcp_server')
            print(f"  - {rel_path}")
    else:
        print("\n✅ ¡No se encontraron problemas!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
