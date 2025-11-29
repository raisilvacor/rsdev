"""
Configuração centralizada para armazenamento de imagens
Garante consistência entre app.py e outros módulos
"""
import os

def should_use_db_storage():
    """
    Determina se deve usar armazenamento no banco de dados.
    
    Retorna True se:
    - Está em produção (FLASK_ENV=production, RENDER=true, ou PORT definido)
    - OU DATABASE_URL está definido
    - OU USE_DB_IMAGE_STORAGE env var está definida como 'true'
    
    Retorna False apenas em desenvolvimento local sem DATABASE_URL e sem flag.
    """
    # Verificar variável de ambiente explícita primeiro
    use_db_env = os.environ.get('USE_DB_IMAGE_STORAGE', '').lower()
    if use_db_env in ('true', '1', 'yes'):
        return True
    if use_db_env in ('false', '0', 'no'):
        return False
    
    # Se não especificado, calcular baseado em ambiente
    is_production = (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('RENDER') == 'true' or
        os.environ.get('PORT') is not None
    )
    has_database_url = bool(os.environ.get('DATABASE_URL'))
    
    # Em produção ou com DATABASE_URL, sempre usar banco
    return is_production or has_database_url

