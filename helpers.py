"""
Funções auxiliares para carregar conteúdo do banco de dados
Versão completa adaptada para PostgreSQL e SQLite
"""
import os
from db_connection import get_db
from flask import url_for

def get_image_url(image_path):
    """
    Retorna a URL correta para uma imagem.
    Se for um upload (logos/, banners/, images/), usa url_for('uploaded_file').
    Caso contrário, usa url_for('static').
    """
    if not image_path:
        return None
    
    # Normalizar caminho
    path = image_path.replace('\\', '/')
    
    # Verificar se é um upload (começa com logos/, banners/, ou images/ que não são estáticas)
    # Imagens estáticas conhecidas do tema começam com images/ mas não são uploads
    static_image_prefixes = [
        'images/logo-',
        'images/slider-',
        'images/index-',
        'images/fullwidth-gallery-',
        'images/clients-',
        'images/banner/',
        'images/ie8-panel/',
        'images/grid-gallery-',
        'images/parallax-',
    ]
    
    # Se começa com logos/ ou banners/, é definitivamente um upload
    if path.startswith('logos/') or path.startswith('banners/'):
        return url_for('uploaded_file', filename=path)
    
    # Se começa com images/, verificar se é estático ou upload
    if path.startswith('images/'):
        # Verificar se é uma imagem estática conhecida
        is_static = any(path.startswith(prefix) for prefix in static_image_prefixes)
        if is_static:
            return url_for('static', filename=path)
        else:
            # É um upload em images/
            return url_for('uploaded_file', filename=path)
    
    # Se começa com uploads/, remover o prefixo (compatibilidade com dados antigos)
    if path.startswith('uploads/'):
        path = path.replace('uploads/', '', 1)
        return url_for('uploaded_file', filename=path)
    
    # Padrão: assumir que é estático
    return url_for('static', filename=path)

def _adapt_query(query):
    """Adapta query para funcionar com PostgreSQL ou SQLite"""
    if os.environ.get('DATABASE_URL') and '?' in query:
        return query.replace('?', '%s')
    return query

def _get_row_value(row, key, default=None):
    """Obtém valor de uma row de forma compatível"""
    if row is None:
        return default
    
    # Tentar acesso como dicionário
    if hasattr(row, 'get'):
        try:
            return row.get(key, default)
        except:
            pass
    
    # Tentar acesso como atributo
    if hasattr(row, key):
        return getattr(row, key, default)
    
    # Tentar acesso como índice (para sqlite3.Row)
    try:
        if key in row:
            return row[key]
    except:
        pass
    
    # Tentar acesso por índice numérico se for tupla
    if isinstance(row, (tuple, list)):
        return default
    
    return default

def get_site_content():
    """Retorna todo o conteúdo do site do banco de dados"""
    try:
        conn = get_db()
        c = conn.cursor()
        content = {}
        query = 'SELECT section, field, content, image_path FROM site_content'
        rows = c.execute(_adapt_query(query)).fetchall()
        
        if not rows:
            conn.close()
            return {}
        
        for row in rows:
            # Usar acesso direto como no teste que funciona
            if hasattr(row, 'get'):
                section = row.get('section')
                field = row.get('field')
                content_val = row.get('content')
                image_path = row.get('image_path')
            else:
                # Tentar acesso por índice para sqlite3.Row
                try:
                    section = row['section']
                    field = row['field']
                    content_val = row['content']
                    image_path = row['image_path']
                except:
                    section = _get_row_value(row, 'section')
                    field = _get_row_value(row, 'field')
                    content_val = _get_row_value(row, 'content')
                    image_path = _get_row_value(row, 'image_path')
            
            if not section or not field:
                continue  # Pular rows inválidas
            
            if section not in content:
                content[section] = {}
            
            # Normalizar caminhos de imagem antigos (compatibilidade)
            if image_path and image_path.startswith('uploads/'):
                # Remover prefixo uploads/ para compatibilidade com nova estrutura
                image_path = image_path.replace('uploads/', '', 1)
            
            content[section][field] = {
                'content': content_val,
                'image_path': image_path
            }
        conn.close()
        return content
    except Exception as e:
        print(f"Erro em get_site_content: {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_projects():
    """Retorna todos os projetos do banco de dados"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM projects ORDER BY order_index, id'
        projects = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return projects
    except Exception as e:
        print(f"Erro em get_projects: {e}")
        return []

def get_services():
    """Retorna todos os serviços do banco de dados"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM services ORDER BY order_index, id'
        services = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return services
    except Exception as e:
        print(f"Erro em get_services: {e}")
        return []

def get_pricing():
    """Retorna todos os planos de preço do banco de dados"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM pricing ORDER BY order_index, id'
        pricing = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return pricing
    except Exception as e:
        print(f"Erro em get_pricing: {e}")
        return []

def get_footer_links():
    """Retorna os links do rodapé"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = "SELECT field, content FROM site_content WHERE section='footer' AND field LIKE 'link_%'"
        rows = c.execute(_adapt_query(query)).fetchall()
        links = []
        for row in rows:
            content = _get_row_value(row, 'content')
            if content and '|' in content:
                text, url = content.split('|', 1)
                links.append({'text': text, 'url': url})
        conn.close()
        return links
    except Exception as e:
        print(f"Erro em get_footer_links: {e}")
        return []

def get_carousel_slides():
    """Retorna todos os slides do carrossel ativos"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM carousel_slides WHERE is_active=1 ORDER BY order_index, id'
        slides = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return slides
    except Exception as e:
        print(f"Erro em get_carousel_slides: {e}")
        return []

def get_company_stats():
    """Retorna as estatísticas da empresa"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM company_stats WHERE id=1'
        stats = c.execute(_adapt_query(query)).fetchone()
        conn.close()
        return stats
    except Exception as e:
        print(f"Erro em get_company_stats: {e}")
        return None

def get_client_images():
    """Retorna todas as imagens de clientes/parceiros"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM client_images ORDER BY order_index, id'
        images = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return images
    except Exception as e:
        print(f"Erro em get_client_images: {e}")
        return []

def get_feature_tabs():
    """Retorna todas as abas da seção 'Obtenha Mais Conosco' ativas"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = 'SELECT * FROM feature_tabs WHERE is_active=1 ORDER BY order_index, id'
        tabs = c.execute(_adapt_query(query)).fetchall()
        conn.close()
        return tabs
    except Exception as e:
        print(f"Erro em get_feature_tabs: {e}")
        return []

def get_feature_carousel_images():
    """Retorna as imagens do carrossel lateral da seção 'Obtenha Mais Conosco'"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = "SELECT image_path FROM site_content WHERE section='feature_tabs' AND field LIKE 'carousel_image_%' ORDER BY field"
        rows = c.execute(_adapt_query(query)).fetchall()
        images = [_get_row_value(row, 'image_path') for row in rows if _get_row_value(row, 'image_path')]
        conn.close()
        return images if images else ['images/index-4-313x580.png', 'images/index-5-313x580.png']
    except Exception as e:
        print(f"Erro em get_feature_carousel_images: {e}")
        return ['images/index-4-313x580.png', 'images/index-5-313x580.png']

def get_projects_section():
    """Retorna as configurações da seção de projetos"""
    try:
        conn = get_db()
        c = conn.cursor()
        query = "SELECT field, content FROM site_content WHERE section='projects'"
        rows = c.execute(_adapt_query(query)).fetchall()
        section = {}
        for row in rows:
            field = _get_row_value(row, 'field')
            section[field] = {'content': _get_row_value(row, 'content')}
        conn.close()
        return section
    except Exception as e:
        print(f"Erro em get_projects_section: {e}")
        return {}

