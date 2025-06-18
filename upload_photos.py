#!/usr/bin/env python
"""
Script para cargar fotos de manera fácil al blog de viajes.

Uso:
python upload_photos.py /ruta/a/fotos --blog "Mi Viaje a Madrid"
python upload_photos.py ~/Pictures/Viaje_Barcelona --blog "Barcelona 2024" --new
python upload_photos.py ./fotos_amsterdam --blog "Amsterdam Experience" --new --place "Amsterdam" --coords "52.3676,4.9041"
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Carga fotos al blog de viajes de manera fácil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

1. Cargar fotos a entrada existente (o crear automáticamente si no existe):
   python upload_photos.py ~/Pictures/Santiago_Chile --blog "Mi Aventura en Santiago"

2. Crear nueva entrada con lugar específico:
   python upload_photos.py ./fotos_madrid --blog "Descubriendo Madrid" --place "Madrid"

3. Crear entrada con coordenadas específicas:
   python upload_photos.py ~/fotos/amsterdam --blog "Amsterdam Experience" --new --place "Amsterdam" --coords "52.3676,4.9041"

4. Cargar a entrada existente por ID:
   python upload_photos.py ~/fotos/barcelona --id 5

5. Forzar sobreescribir fotos existentes:
   python upload_photos.py ~/fotos/roma --blog "Roma Eterna" --force
        """
    )
    
    # Argumentos principales
    parser.add_argument(
        'folder',
        help='Carpeta que contiene las fotos a cargar'
    )
    
    # Opciones de entrada de blog
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--blog', '-b',
        help='Título de la entrada de blog (busca existente o crea nueva con --new)'
    )
    group.add_argument(
        '--id', '-i',
        type=int,
        help='ID de entrada de blog existente'
    )
    
    # Opciones para crear nueva entrada
    parser.add_argument(
        '--new', '-n',
        action='store_true',
        help='Crear nueva entrada de blog si no existe'
    )
    
    parser.add_argument(
        '--place', '-p',
        help='Nombre del lugar (requerido para nuevas entradas)'
    )
    
    parser.add_argument(
        '--coords', '-c',
        help='Coordenadas del lugar en formato "lat,lng" (ej: "40.4168,-3.7038")'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Descripción para la entrada de blog'
    )
    
    # Opciones de procesamiento
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Sobrescribir fotos existentes'
    )
    
    parser.add_argument(
        '--extensions', '-e',
        default='jpg,jpeg,png,tiff,raw',
        help='Extensiones de archivo soportadas (separadas por comas)'
    )
    
    args = parser.parse_args()
    
    # Validaciones
    folder_path = Path(args.folder).expanduser().resolve()
    if not folder_path.exists():
        print(f"❌ Error: La carpeta '{folder_path}' no existe")
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"❌ Error: '{folder_path}' no es una carpeta")
        sys.exit(1)
    
    if args.new and args.blog and not args.place:
        print("❌ Error: Se requiere --place para crear una nueva entrada de blog")
        sys.exit(1)
    
    # Construir comando Django
    backend_dir = Path(__file__).parent / 'backend'
    manage_py = backend_dir / 'manage.py'
    
    if not manage_py.exists():
        print(f"❌ Error: No se encuentra manage.py en {manage_py}")
        sys.exit(1)
    
    cmd = [
        sys.executable, str(manage_py),
        'upload_blog_photos',
        '--source-folder', str(folder_path),
        '--supported-extensions', args.extensions
    ]
    
    # Agregar opciones de entrada de blog
    if args.id:
        cmd.extend(['--blog-entry-id', str(args.id)])
    elif args.blog:
        cmd.extend(['--blog-title', args.blog])
        # Siempre permitir creación si no existe
        if args.new:
            cmd.append('--create-blog')
    
    # Agregar opciones de lugar
    if args.place:
        cmd.extend(['--place-name', args.place])
    
    if args.coords:
        cmd.extend(['--place-coords', args.coords])
    
    if args.description:
        cmd.extend(['--description', args.description])
    
    # Agregar opciones de procesamiento
    if args.force:
        cmd.append('--force-overwrite')
    
    # Información previa
    print("🚀 Iniciando carga de fotos...")
    print(f"📁 Carpeta: {folder_path}")
    if args.blog:
        print(f"📝 Blog: {args.blog}")
        if args.new:
            print("✨ Se creará nueva entrada si no existe")
    elif args.id:
        print(f"📝 ID de entrada: {args.id}")
    
    print("\n" + "="*50)
    
    # Ejecutar comando
    try:
        os.chdir(backend_dir)
        result = subprocess.run(cmd, check=True)
        print("\n🎉 ¡Carga completada exitosamente!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la carga: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Carga cancelada por el usuario")
        sys.exit(1)

if __name__ == '__main__':
    main() 