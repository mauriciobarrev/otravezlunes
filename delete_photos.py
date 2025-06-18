#!/usr/bin/env python
"""
Script para eliminar fotos de una entrada de blog.

Uso:
python delete_photos.py --blog "Mi Viaje a Madrid"
python delete_photos.py --id 6 --delete-files
python delete_photos.py --blog "Tayrona" --force
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Elimina todas las fotos de una entrada de blog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

1. Eliminar fotos de la base de datos (mantener archivos):
   python delete_photos.py --blog "Parque Nacional Natural Tayrona: El paraíso en la Tierra."

2. Eliminar fotos y archivos físicos:
   python delete_photos.py --id 6 --delete-files

3. Eliminar sin confirmación:
   python delete_photos.py --blog "Mi Viaje" --force

4. Eliminar todo sin preguntar:
   python delete_photos.py --id 6 --delete-files --force
        """
    )
    
    # Opciones para identificar la entrada
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--blog', '-b',
        help='Título de la entrada de blog'
    )
    group.add_argument(
        '--id', '-i',
        type=int,
        help='ID de entrada de blog'
    )
    
    # Opciones de eliminación
    parser.add_argument(
        '--delete-files', '-d',
        action='store_true',
        help='Eliminar también los archivos físicos'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='No pedir confirmación'
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
        'delete_blog_photos'
    ]
    
    # Agregar opciones de identificación
    if args.id:
        cmd.extend(['--blog-entry-id', str(args.id)])
    elif args.blog:
        cmd.extend(['--blog-title', args.blog])
    
    # Agregar opciones de eliminación
    if args.delete_files:
        cmd.append('--delete-files')
    
    if args.force:
        cmd.append('--force')
    
    # Información previa
    print("🗑️  Iniciando eliminación de fotos...")
    if args.blog:
        print(f"📝 Blog: {args.blog}")
    elif args.id:
        print(f"📝 ID de entrada: {args.id}")
    
    if args.delete_files:
        print("🗂️  Se eliminarán también los archivos físicos")
    else:
        print("🗂️  Solo se eliminarán de la base de datos")
    
    print("\n" + "="*50)
    
    # Ejecutar comando
    try:
        os.chdir(backend_dir)
        result = subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la eliminación: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Eliminación cancelada por el usuario")
        sys.exit(1)

if __name__ == '__main__':
    main() 