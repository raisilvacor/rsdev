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
    
    Em produção (USE_DB_IMAGE_STORAGE=True ou DATABASE_URL definido):
    - SEMPRE salva no banco PostgreSQL, nunca usa filesystem
    - Retorna image_key ou None se falhar
    
    Em desenvolvimento (USE_DB_IMAGE_STORAGE=False e sem DATABASE_URL):
    - Tenta salvar no banco primeiro
    - Se falhar, usa fallback para arquivo local
    
    Args:
        image_file: Arquivo de imagem (Werkzeug FileStorage)
        category: Categoria (logos, banners, images)
        upload_base: Base directory para fallback de arquivo local (apenas em dev)
    
    Returns:
        image_key: Chave única da imagem salva (para uso em image_path do banco)
    """
    if not image_file or not image_file.filename:
        return None
    
    # Verificar configuração de armazenamento
    use_db_storage = os.environ.get('USE_DB_IMAGE_STORAGE', 'true').lower() == 'true'
    is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER') == 'true' or os.environ.get('PORT') is not None
    has_database_url = bool(os.environ.get('DATABASE_URL'))
    must_use_db = use_db_storage or is_production or has_database_url
    
    # Tentar salvar no banco de dados primeiro
    try:
        from image_storage import save_image_to_db
        image_key = save_image_to_db(image_file, category=category)
        if image_key:
            return image_key
    except Exception as e:
        print(f"⚠️ Erro ao salvar no banco: {e}")
        import traceback
        traceback.print_exc()
        
        # Se deve usar banco obrigatoriamente, não tentar fallback
        if must_use_db:
            print("❌ ERRO CRÍTICO: Falha ao salvar no banco em produção. Upload cancelado.")
            return None
    
    # Fallback: salvar em arquivo local (APENAS em desenvolvimento sem DATABASE_URL)
    if not must_use_db and not has_database_url:
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

