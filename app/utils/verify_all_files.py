#!/usr/bin/env python3
"""
Script para verificar la sintaxis de todos los archivos Python del proyecto.
"""

import py_compile
from pathlib import Path
import sys

def check_file(file_path):
    """Verifica un archivo Python."""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    # Buscar todos los archivos .py en app/
    base_path = Path('app')
    python_files = list(base_path.rglob('*.py'))
    
    print(f"🔍 Verificando {len(python_files)} archivos Python...\n")
    
    errors = []
    success_count = 0
    
    for py_file in sorted(python_files):
        is_valid, error = check_file(py_file)
        if is_valid:
            success_count += 1
            print(f"✅ {py_file}")
        else:
            errors.append((py_file, error))
            print(f"❌ {py_file}")
    
    print(f"\n{'='*70}")
    print(f"✅ Archivos correctos: {success_count}/{len(python_files)}")
    print(f"❌ Archivos con errores: {len(errors)}/{len(python_files)}")
    print(f"{'='*70}\n")
    
    if errors:
        print("⚠️  ERRORES ENCONTRADOS:\n")
        for file_path, error in errors:
            print(f"\n📁 {file_path}")
            print(f"   {error}\n")
        sys.exit(1)
    else:
        print("🎉 ¡Todos los archivos compilan correctamente!")
        sys.exit(0)

if __name__ == '__main__':
    main()
