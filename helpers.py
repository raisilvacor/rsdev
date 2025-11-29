"""
Funções auxiliares para carregar conteúdo do banco de dados
"""
import sqlite3

DB_PATH = 'site_content.db'

def get_site_content():
    """Retorna todo o conteúdo do site do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        content = {}
        rows = c.execute('SELECT section, field, content, image_path FROM site_content').fetchall()
        for row in rows:
            if row['section'] not in content:
                content[row['section']] = {}
            content[row['section']][row['field']] = {
                'content': row['content'],
                'image_path': row['image_path']
            }
        
        conn.close()
        return content
    except:
        return {}

def get_projects():
    """Retorna todos os projetos do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        projects = c.execute('SELECT * FROM projects ORDER BY order_index, id').fetchall()
        conn.close()
        return projects
    except:
        return []

def get_services():
    """Retorna todos os serviços do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        services = c.execute('SELECT * FROM services ORDER BY order_index, id').fetchall()
        conn.close()
        return services
    except:
        return []

def get_pricing():
    """Retorna todos os planos de preço do banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        pricing = c.execute('SELECT * FROM pricing ORDER BY order_index, id').fetchall()
        conn.close()
        return pricing
    except:
        return []

def get_footer_links():
    """Retorna os links do rodapé"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        links = []
        rows = c.execute("SELECT field, content FROM site_content WHERE section='footer' AND field LIKE 'link_%'").fetchall()
        for row in rows:
            if row['content'] and '|' in row['content']:
                text, url = row['content'].split('|', 1)
                links.append({'text': text, 'url': url})
        
        conn.close()
        return links
    except:
        return []

def get_carousel_slides():
    """Retorna todos os slides do carrossel ativos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        slides = c.execute('SELECT * FROM carousel_slides WHERE is_active=1 ORDER BY order_index, id').fetchall()
        conn.close()
        return slides
    except:
        return []

def get_company_stats():
    """Retorna as estatísticas da empresa"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        stats = c.execute('SELECT * FROM company_stats WHERE id=1').fetchone()
        conn.close()
        return stats
    except:
        return None

def get_client_images():
    """Retorna todas as imagens de clientes/parceiros"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        images = c.execute('SELECT * FROM client_images ORDER BY order_index, id').fetchall()
        conn.close()
        return images
    except:
        return []

def get_feature_tabs():
    """Retorna todas as abas da seção 'Obtenha Mais Conosco' ativas"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        tabs = c.execute('SELECT * FROM feature_tabs WHERE is_active=1 ORDER BY order_index, id').fetchall()
        conn.close()
        return tabs
    except:
        return []

def get_feature_carousel_images():
    """Retorna as imagens do carrossel lateral da seção 'Obtenha Mais Conosco'"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        rows = c.execute("SELECT image_path FROM site_content WHERE section='feature_tabs' AND field LIKE 'carousel_image_%' ORDER BY field").fetchall()
        images = [row['image_path'] for row in rows]
        conn.close()
        return images if images else ['images/index-4-313x580.png', 'images/index-5-313x580.png']
    except:
        return ['images/index-4-313x580.png', 'images/index-5-313x580.png']

def get_projects_section():
    """Retorna as configurações da seção de projetos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        section = {}
        rows = c.execute("SELECT field, content FROM site_content WHERE section='projects'").fetchall()
        for row in rows:
            section[row['field']] = {'content': row['content']}
        conn.close()
        return section
    except:
        return {}

