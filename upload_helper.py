"""
Helper function para salvar imagens de forma persistente
Tenta salvar no banco PostgreSQL primeiro, depois fallback para arquivo local
"""
import os
from werkzeug.utils import secure_filename
from datetime import datetime

def save_image_persistent(image_file, category='images', upload_base=None):
    """
    Salva uma imagem de forma persistente.
    Tenta salvar no banco PostgreSQL primeiro (para Render Free).
    Se falhar, salva em arquivo local (desenvolvimento).
    
    Args:
        image_file: Arquivo de imagem (Werkzeug FileStorage)
        category: Categoria (logos, banners, images)
        upload_base: Base directory para fallback de arquivo local
    
    Returns:
        image_path: Caminho da imagem salva (para uso em image_path do banco)
    """
    if not image_file or not image_file.filename:
        return None
    
    # Tentar salvar no banco de dados primeiro (persistência no Render Free)
    try:
        from image_storage import save_image_to_db
        image_path = save_image_to_db(image_file, category=category)
        if image_path:
            return image_path
    except Exception as e:
        print(f"⚠️ Erro ao salvar no banco, usando fallback para arquivo: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback: salvar em arquivo local (desenvolvimento)
    try:
        if not upload_base:
            from flask import current_app
            upload_base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        
        filename = secure_filename(image_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        upload_dir = os.path.join(upload_base, category)
        os.makedirs(upload_dir, exist_ok=True)
        
        upload_path = os.path.join(upload_dir, filename)
        image_file.seek(0)  # Reset file pointer
        image_file.save(upload_path)
        
        if os.path.exists(upload_path):
            return f"{category}/{filename}"
    except Exception as e:
        print(f"❌ Erro ao salvar em arquivo local: {e}")
        import traceback
        traceback.print_exc()
    
    return None

