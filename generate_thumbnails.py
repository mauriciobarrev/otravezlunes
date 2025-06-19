#!/usr/bin/env python
"""
Script para generar thumbnails de fotos del blog.

Uso:
python generate_thumbnails.py  # Generar faltantes
python generate_thumbnails.py --force  # Regenerar todos
python generate_thumbnails.py --entry 8  # Solo una entrada
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Genera thumbnails para las fotos del blog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

1. Generar solo los thumbnails faltantes:
   python generate_thumbnails.py

2. Regenerar todos los thumbnails:
   python generate_thumbnails.py --force

3. Procesar solo una entrada específica:
   python generate_thumbnails.py --entry 8

4. Cambiar tamaño de thumbnails:
   python generate_thumbnails.py --size 200x200
        """
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Regenerar todos los thumbnails, incluso los existentes'
    )
    
    parser.add_argument(
        '--entry', '-e',
        type=int,
        help='Solo procesar fotos de una entrada específica (por ID)'
    )
    
    parser.add_argument(
        '--size', '-s',
        default='300x300',
        help='Tamaño del thumbnail en formato "WIDTHxHEIGHT" (default: 300x300)'
    )
    
    args = parser.parse_args()
    
    # Construir comando Django
    backend_dir = Path(__file__).parent / 'backend'
    manage_py = backend_dir / 'manage.py'
    
    if not manage_py.exists():
        print(f"❌ Error: No se encuentra manage.py en {manage_py}")
        sys.exit(1)
    
    cmd = [
        sys.executable, str(manage_py),
        'generate_missing_thumbnails',
        '--size', args.size
    ]
    
    # Agregar opciones
    if args.force:
        cmd.append('--force')
    
    if args.entry:
        cmd.extend(['--entrada-id', str(args.entry)])
    
    # Información previa
    print("🖼️  Generando thumbnails...")
    if args.entry:
        print(f"📝 Solo entrada ID: {args.entry}")
    else:
        print("📝 Todas las entradas")
    
    print(f"📏 Tamaño: {args.size}")
    
    if args.force:
        print("🔄 Regenerando todos (incluso existentes)")
    else:
        print("⚡ Solo generando faltantes")
    
    print("\n" + "="*50)
    
    # Ejecutar comando
    try:
        os.chdir(backend_dir)
        result = subprocess.run(cmd, check=True)
        print("\n🎉 ¡Generación completada!")
        print("🔗 Revisa el admin: http://localhost:8000/admin/travel_api/fotografia/")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la generación: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Generación cancelada por el usuario")
        sys.exit(1)

if __name__ == '__main__':
    main() 