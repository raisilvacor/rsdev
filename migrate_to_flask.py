"""
Script para migrar o projeto para Flask
Cria a estrutura de pastas e move os arquivos necessários
"""
import os
import shutil
from pathlib import Path

def create_flask_structure():
    """Cria a estrutura de pastas Flask"""
    base_dir = Path('.')
    
    # Criar pastas
    folders = [
        'templates',
        'static',
        'static/css',
        'static/js',
        'static/images',
        'static/fonts',
        'static/video'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Criada pasta: {folder}")
    
    # Mover arquivos estáticos
    print("\nMovendo arquivos estáticos...")
    
    # CSS
    if os.path.exists('css'):
        for file in os.listdir('css'):
            src = os.path.join('css', file)
            dst = os.path.join('static/css', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"  ✓ {src} -> {dst}")
    
    # JS
    if os.path.exists('js'):
        for file in os.listdir('js'):
            src = os.path.join('js', file)
            dst = os.path.join('static/js', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"  ✓ {src} -> {dst}")
    
    # Images
    if os.path.exists('images'):
        for root, dirs, files in os.walk('images'):
            for file in files:
                src = os.path.join(root, file)
                rel_path = os.path.relpath(root, 'images')
                if rel_path == '.':
                    dst = os.path.join('static/images', file)
                else:
                    dst_dir = os.path.join('static/images', rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, file)
                shutil.copy2(src, dst)
                print(f"  ✓ {src} -> {dst}")
    
    # Fonts
    if os.path.exists('fonts'):
        for file in os.listdir('fonts'):
            src = os.path.join('fonts', file)
            dst = os.path.join('static/fonts', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"  ✓ {src} -> {dst}")
    
    # Video
    if os.path.exists('video'):
        for file in os.listdir('video'):
            src = os.path.join('video', file)
            dst = os.path.join('static/video', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"  ✓ {src} -> {dst}")
    
    # Copiar index.html para templates
    if os.path.exists('index.html'):
        shutil.copy2('index.html', 'templates/index.html')
        print(f"\n✓ index.html copiado para templates/")
    
    print("\n✓ Migração concluída!")
    print("\nPróximos passos:")
    print("1. Os arquivos originais foram mantidos")
    print("2. Execute: python app.py")
    print("3. Acesse: http://localhost:5000")

if __name__ == '__main__':
    create_flask_structure()

