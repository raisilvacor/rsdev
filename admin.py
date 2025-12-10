"""
Módulo do painel administrativo
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from functools import wraps
from db_connection import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Configurações
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico'}
DB_PATH = 'site_content.db'


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _execute_insert_replace(conn, table_name, columns, values, unique_columns):
    """
    Executa INSERT OR REPLACE adaptado para PostgreSQL ou SQLite.
    
    Args:
        conn: Conexão do banco
        table_name: Nome da tabela
        columns: Lista de colunas (ex: ['section', 'field', 'content'])
        values: Tupla com valores
        unique_columns: Lista de colunas que formam a chave única (ex: ['section', 'field'])
    """
    is_postgres = hasattr(conn, '_conn')
    
    if is_postgres:
        # PostgreSQL: usar ON CONFLICT
        cols_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        unique_cols_str = ', '.join(unique_columns)
        update_cols = [col for col in columns if col not in unique_columns]
        update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])
        
        query = f'''INSERT INTO {table_name} ({cols_str})
                   VALUES ({placeholders})
                   ON CONFLICT ({unique_cols_str}) DO UPDATE
                   SET {update_set}, updated_at = CURRENT_TIMESTAMP'''
        conn.execute(query, values)
    else:
        # SQLite: usar INSERT OR REPLACE
        cols_str = ', '.join(columns)
        placeholders = ', '.join(['?'] * len(columns))
        query = f'''INSERT OR REPLACE INTO {table_name} ({cols_str}, updated_at)
                   VALUES ({placeholders}, CURRENT_TIMESTAMP)'''
        conn.execute(query, values)


def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de conteúdo do site
    c.execute('''CREATE TABLE IF NOT EXISTS site_content
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  section TEXT NOT NULL,
                  field TEXT NOT NULL,
                  content TEXT,
                  image_path TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(section, field))''')
    
    # Tabela de projetos
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  image_path TEXT,
                  link_url TEXT,
                  filter_type TEXT,
                  order_index INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Adicionar coluna link_url se não existir (para bancos já existentes)
    try:
        c.execute('ALTER TABLE projects ADD COLUMN link_url TEXT')
    except:
        pass  # Coluna já existe
    
    # Tabela de serviços
    c.execute('''CREATE TABLE IF NOT EXISTS services
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  icon_class TEXT,
                  order_index INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de preços
    c.execute('''CREATE TABLE IF NOT EXISTS pricing
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price REAL NOT NULL,
                  features TEXT,
                  is_popular INTEGER DEFAULT 0,
                  order_index INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de posts do blog
    c.execute('''CREATE TABLE IF NOT EXISTS blog_posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT,
                  image_path TEXT,
                  publish_date DATE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de configurações gerais
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  key TEXT UNIQUE NOT NULL,
                  value TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de estatísticas da empresa
    c.execute('''CREATE TABLE IF NOT EXISTS company_stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  years INTEGER DEFAULT 10,
                  title TEXT DEFAULT 'Anos de Experiência',
                  description TEXT,
                  button_text TEXT DEFAULT 'Entre em contato',
                  button_link TEXT DEFAULT '#',
                  stat1_number TEXT DEFAULT '2',
                  stat1_symbol TEXT DEFAULT 'k',
                  stat1_label TEXT DEFAULT 'aplicativos desenvolvidos',
                  stat2_number TEXT DEFAULT '40',
                  stat2_symbol TEXT DEFAULT '',
                  stat2_label TEXT DEFAULT 'Consultores',
                  stat3_number TEXT DEFAULT '12',
                  stat3_symbol TEXT DEFAULT '',
                  stat3_label TEXT DEFAULT 'Prêmios conquistados',
                  stat4_number TEXT DEFAULT '160',
                  stat4_symbol TEXT DEFAULT '',
                  stat4_label TEXT DEFAULT 'Funcionários',
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de imagens de clientes/parceiros
    c.execute('''CREATE TABLE IF NOT EXISTS client_images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  image_path TEXT NOT NULL,
                  alt_text TEXT,
                  link_url TEXT,
                  order_index INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de abas da seção "Obtenha Mais Conosco"
    c.execute('''CREATE TABLE IF NOT EXISTS feature_tabs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  content TEXT,
                  button1_text TEXT DEFAULT 'Entre em contato',
                  button1_link TEXT DEFAULT '#modalCta',
                  button2_text TEXT DEFAULT 'Saiba Mais',
                  button2_link TEXT DEFAULT '#',
                  order_index INTEGER DEFAULT 0,
                  is_active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de slides do carrossel
    c.execute('''CREATE TABLE IF NOT EXISTS carousel_slides
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  image_path TEXT NOT NULL,
                  button_text TEXT DEFAULT 'Entre em contato',
                  button_link TEXT DEFAULT '#modalCta',
                  order_index INTEGER DEFAULT 0,
                  is_active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de mensagens de contato
    c.execute('''CREATE TABLE IF NOT EXISTS contact_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  message TEXT,
                  phone TEXT,
                  subject TEXT,
                  form_type TEXT DEFAULT 'contact',
                  is_read INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de imagens armazenadas no banco (para persistência no Render Free)
    # Também funciona em SQLite local para desenvolvimento
    c.execute('''CREATE TABLE IF NOT EXISTS stored_images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  image_key TEXT UNIQUE NOT NULL,
                  image_data BLOB NOT NULL,
                  mime_type TEXT NOT NULL,
                  filename TEXT NOT NULL,
                  file_size INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Criar índice para busca rápida por image_key
    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_stored_images_key ON stored_images(image_key)')
    except:
        pass  # Índice pode já existir
    
    # Criar usuário admin padrão (senha: admin123)
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        password_hash = generate_password_hash('admin123')
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  ('admin', password_hash))
    
    # Inicializar conteúdo padrão
    default_content = [
        ('header', 'logo', None, 'images/logo-default-223x50.png'),
        ('header', 'logo_inverse', None, 'images/logo-inverse-223x50.png'),
        ('footer', 'copyright_text', 'RatherApp', None),
        ('footer', 'rights_text', 'Todos os direitos reservados.', None),
        ('footer', 'social_facebook', 'https://facebook.com', None),
        ('footer', 'social_twitter', 'https://twitter.com', None),
        ('footer', 'social_google', 'https://plus.google.com', None),
        ('footer', 'social_instagram', 'https://instagram.com', None),
        ('contact', 'phone_1', '+1 323-913-4688', None),
        ('contact', 'phone_2', '+1 323-888-4554', None),
        ('contact', 'address', '4730 Crystal Springs Dr, Los Angeles, CA 90027', None),
        ('contact', 'email_1', 'mail@demolink.org', None),
        ('contact', 'email_2', 'info@demolink.org', None),
        ('contact', 'whatsapp_enabled', '1', None),
        ('contact', 'whatsapp_phone', 'phone_1', None),
        ('services', 'section_image', None, 'images/index-1-415x592.png'),
        ('cta', 'title', 'Vamos Desenvolver Seu Próximo Grande Aplicativo!', None),
        ('cta', 'description', 'Você precisa de uma solução de software única para sua empresa? Sabemos como ajudá-lo!', None),
        ('cta', 'background_image', None, 'images/parallax-1.jpg'),
        ('cta', 'button1_text', 'Entre em Contato', None),
        ('cta', 'button1_link', '#modalCta', None),
        ('cta', 'button2_text', 'Saiba Mais', None),
        ('cta', 'button2_link', '#', None),
    ]
    
    for section, field, content, image_path in default_content:
        c.execute('''INSERT OR IGNORE INTO site_content (section, field, content, image_path)
                     VALUES (?, ?, ?, ?)''', (section, field, content, image_path))
    
    # Inicializar slides padrão do carrossel
    c.execute('SELECT COUNT(*) FROM carousel_slides')
    if c.fetchone()[0] == 0:
        default_slides = [
            ('Desenvolvimento de Aplicativos Mobile', 
             'Desde nossa fundação, temos entregado soluções de software de alta qualidade e sustentáveis para propósitos corporativos de empresas em todo o mundo.',
             'images/slider-1-slide-2-1770x742.jpg', 0),
            ('Equipe Experiente', 
             'Somos uma equipe de desenvolvedores de software qualificados, com o objetivo de criar ferramentas únicas e poderosas para seu negócio e vida cotidiana.',
             'images/slider-1-slide-4-1770x742.jpg', 1),
            ('Software Premiado', 
             'As soluções de software desenvolvidas por nossa empresa foram numerosamente premiadas por usabilidade e recursos inovadores.',
             'images/slider-1-slide-6-1770x742.jpg', 2),
        ]
        for title, description, image_path, order in default_slides:
            c.execute('''INSERT INTO carousel_slides (title, description, image_path, order_index)
                         VALUES (?, ?, ?, ?)''', (title, description, image_path, order))
    
    # Inicializar serviços padrão
    c.execute('SELECT COUNT(*) FROM services')
    if c.fetchone()[0] == 0:
        default_services = [
            ('SOLUÇÕES CORPORATIVAS',
             'Precisa de software específico para sua empresa? Estamos prontos para desenvolvê-lo!',
             'linearicons-phone-in-out',
             0),
            ('SOLUÇÕES PARA CALL CENTER',
             'Nossos especialistas fornecem produtos personalizados de qualquer complexidade para call centers.',
             'linearicons-headset',
             1),
            ('DESENVOLVIMENTO NA NUVEM',
             'Também podemos oferecer soluções confiáveis de desenvolvimento na nuvem.',
             'linearicons-outbox',
             2),
        ]
        for title, description, icon_class, order in default_services:
            c.execute('''INSERT INTO services (title, description, icon_class, order_index)
                         VALUES (?, ?, ?, ?)''', (title, description, icon_class, order))
    
    # Inicializar estatísticas da empresa
    c.execute('SELECT COUNT(*) FROM company_stats')
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO company_stats 
                    (years, title, description, button_text, button_link,
                     stat1_number, stat1_symbol, stat1_label,
                     stat2_number, stat2_symbol, stat2_label,
                     stat3_number, stat3_symbol, stat3_label,
                     stat4_number, stat4_symbol, stat4_label)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (10, 'Anos de Experiência', 
                 'RatherApp é uma equipe de designers e desenvolvedores de aplicativos altamente experientes criando software único para você.',
                 'Entre em contato', '#',
                 '2', 'k', 'aplicativos desenvolvidos',
                 '40', '', 'Consultores',
                 '12', '', 'Prêmios conquistados',
                 '160', '', 'Funcionários'))
    
    # Inicializar imagens de clientes padrão
    c.execute('SELECT COUNT(*) FROM client_images')
    if c.fetchone()[0] == 0:
        default_client_images = [
            ('images/clients-9-270x117.png', 'Cliente 1', '#', 0),
            ('images/clients-10-270x117.png', 'Cliente 2', '#', 1),
            ('images/clients-3-270x117.png', 'Cliente 3', '#', 2),
            ('images/clients-11-270x117.png', 'Cliente 4', '#', 3),
        ]
        for image_path, alt_text, link_url, order in default_client_images:
            c.execute('''INSERT INTO client_images (image_path, alt_text, link_url, order_index)
                         VALUES (?, ?, ?, ?)''', (image_path, alt_text, link_url, order))
    
    # Inicializar abas "Obtenha Mais Conosco"
    c.execute('SELECT COUNT(*) FROM feature_tabs')
    if c.fetchone()[0] == 0:
        default_tabs = [
            ('APLICATIVOS GRATUITOS',
             'Regularmente fazemos upload de novos aplicativos gratuitos em nosso site, que é totalmente acessível para nossos clientes e assinantes. Você também pode saber mais sobre aplicativos gratuitos em nosso blog.',
             0),
            ('FIQUE CONECTADO',
             'Cada aplicativo que desenvolvemos tem suporte social integrado que permite que você permaneça conectado às suas contas no Facebook, Instagram, Twitter e outras redes.',
             1),
            ('ATENDIMENTO AO CLIENTE',
             'Cada cliente da RatherApp pode ter acesso ao nosso suporte amigável e qualificado 24/7 via chat ou telefone. Sinta-se à vontade para nos fazer qualquer pergunta!',
             2),
            ('ÓTIMA USABILIDADE',
             'Todos os nossos aplicativos são projetados para ter ótima usabilidade, a fim de operar facilmente nossas aplicações. É por isso que nosso software tem altas avaliações e muitos prêmios.',
             3),
        ]
        for title, content, order in default_tabs:
            c.execute('''INSERT INTO feature_tabs (title, content, order_index)
                         VALUES (?, ?, ?)''', (title, content, order))
    
    # Inicializar planos de preço padrão
    c.execute('SELECT COUNT(*) FROM pricing')
    if c.fetchone()[0] == 0:
        default_pricing = [
            ('básico', 500.00, 'Desenvolvimento de conceito\nDesign de interface', 0, 0),
            ('Otimizado', 800.00, 'Desenvolvimento de conceito\nDesign de interface\nGerenciamento de configuração\nGarantia de qualidade de software', 1, 1),
            ('Ultimate', 1200.00, 'Desenvolvimento de conceito\nDesign de interface\nGerenciamento de configuração\nGarantia de qualidade de software\nIntegração de aplicativo', 0, 2),
        ]
        for name, price, features, is_popular, order in default_pricing:
            c.execute('''INSERT INTO pricing (name, price, features, is_popular, order_index)
                         VALUES (?, ?, ?, ?, ?)''', (name, price, features, is_popular, order))
    
    # Inicializar conteúdo da seção de projetos
    c.execute("SELECT COUNT(*) FROM site_content WHERE section='projects' AND field='title'")
    if c.fetchone()[0] == 0:
        default_projects_section = [
            ('projects', 'title', 'Projetos Recentes', None),
            ('projects', 'description', 'Em nosso portfólio, você pode navegar pelos produtos mais recentes desenvolvidos para nossos clientes para diferentes propósitos corporativos. Nossa equipe qualificada de designers de interface e desenvolvedores de software está sempre pronta para criar algo único para você.', None),
        ]
        for section, field, content, image_path in default_projects_section:
            c.execute('''INSERT OR REPLACE INTO site_content (section, field, content, image_path, updated_at)
                         VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                     (section, field, content, image_path))
    
    # Inicializar filtros de projetos
    c.execute('SELECT COUNT(*) FROM site_content WHERE section="projects" AND field LIKE "filter_%"')
    if c.fetchone()[0] == 0:
        default_filters = [
            ('projects', 'filter_all', 'Todos', None),
            ('projects', 'filter_type1', 'Aplicativos Mobile', None),
            ('projects', 'filter_type2', 'Sites', None),
        ]
        for section, field, content, image_path in default_filters:
            c.execute('''INSERT OR REPLACE INTO site_content (section, field, content, image_path, updated_at)
                         VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                     (section, field, content, image_path))
    
    # Inicializar projetos padrão
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        default_projects = [
            ('FinStep', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-1-420x350.jpg', '#', 'Type 1', 0),
            ('Mobile Finance', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-2-420x350.jpg', '#', 'Type 1', 1),
            ('Q-Manage', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-3-420x350.jpg', '#', 'Type 2', 2),
            ('WeatherCast', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-4-420x350.jpg', '#', 'Type 1', 3),
            ('Home Calendar', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-5-420x350.jpg', '#', 'Type 1', 4),
            ('MPlanner', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-6-420x350.jpg', '#', 'Type 1', 5),
            ('Alice Messenger', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-7-420x350.jpg', '#', 'Type 2', 6),
            ('WiseMoney', 'Trabalhamos duro em cada aplicativo para entregar recursos de primeira linha com uma excelente interface que você não encontrará em nenhum outro lugar.', 'images/fullwidth-gallery-8-420x350.jpg', '#', 'Type 1', 7),
        ]
        for title, description, image_path, link_url, filter_type, order in default_projects:
            c.execute('''INSERT INTO projects (title, description, image_path, link_url, filter_type, order_index)
                         VALUES (?, ?, ?, ?, ?, ?)''', (title, description, image_path, link_url, filter_type, order))
    
    conn.commit()
    conn.close()


def login_required(f):
    """Decorator para rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


# get_db() agora é importado de db_connection.py


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_user_id'] = user['id']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    """Logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal"""
    conn = get_db()
    
    # Estatísticas
    projects_count = conn.execute('SELECT COUNT(*) as count FROM projects').fetchone()[0]
    services_count = conn.execute('SELECT COUNT(*) as count FROM services').fetchone()[0]
    posts_count = conn.execute('SELECT COUNT(*) as count FROM blog_posts').fetchone()[0]
    pricing_count = conn.execute('SELECT COUNT(*) as count FROM pricing').fetchone()[0]
    
    conn.close()
    
    return render_template('admin/dashboard.html',
                         projects_count=projects_count,
                         services_count=services_count,
                         posts_count=posts_count,
                         pricing_count=pricing_count)


@admin_bp.route('/content', methods=['GET', 'POST'])
@login_required
def content():
    """Gerenciar conteúdo geral do site"""
    conn = get_db()
    
    if request.method == 'POST':
        try:
            # Primeiro, processar todos os campos de conteúdo e imagens juntos
            # para evitar conflitos de atualização
            updates = {}  # {(section, field): {'content': ..., 'image_path': ...}}
            
            # Processar campos de conteúdo (formato: content_section_field)
            for key, value in request.form.items():
                if key.startswith('content_'):
                    parts = key.replace('content_', '').split('_', 1)
                    if len(parts) == 2:
                        section = parts[0]
                        field = parts[1]
                        key_tuple = (section, field)
                        
                        if key_tuple not in updates:
                            updates[key_tuple] = {'content': None, 'image_path': None}
                        # Preservar o valor mesmo se for string vazia (permite limpar campos)
                        updates[key_tuple]['content'] = value.strip() if value else ''
            
            # Processar checkbox do WhatsApp (se não foi enviado no form, significa desativado)
            if 'content_contact_whatsapp_enabled' not in request.form:
                key_tuple = ('contact', 'whatsapp_enabled')
                if key_tuple not in updates:
                    updates[key_tuple] = {'content': None, 'image_path': None}
                updates[key_tuple]['content'] = '0'
            
            # Processar uploads de imagens (formato: image_section_field)
            # Debug: verificar todos os arquivos recebidos
            files_received = list(request.files.keys())
            
            for key, image_file in request.files.items():
                # Verificar se é um campo de imagem
                if key.startswith('image_'):
                    # Verificar se realmente tem um arquivo selecionado
                    # image_file.filename pode ser string vazia se nenhum arquivo foi selecionado
                    if image_file and hasattr(image_file, 'filename'):
                        filename_value = image_file.filename
                        if filename_value and filename_value.strip():
                            if allowed_file(filename_value):
                                parts = key.replace('image_', '').split('_', 1)
                                if len(parts) == 2:
                                    section = parts[0]
                                    field = parts[1]
                                    key_tuple = (section, field)
                                    
                                    filename = secure_filename(filename_value)
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    filename = f"{timestamp}_{filename}"
                                    
                                    # Usar app.config['UPLOAD_FOLDER'] em vez de static/uploads
                                    upload_base = current_app.config['UPLOAD_FOLDER']
                                    
                                    if section == 'header' and 'logo' in field:
                                        upload_dir = os.path.join(upload_base, 'logos')
                                    elif section == 'banner':
                                        upload_dir = os.path.join(upload_base, 'banners')
                                    elif section == 'services':
                                        upload_dir = os.path.join(upload_base, 'images')
                                    else:
                                        upload_dir = os.path.join(upload_base, 'images')
                                    
                                    # Garantir que o diretório existe
                                    os.makedirs(upload_dir, exist_ok=True)
                                    
                                    upload_path = os.path.join(upload_dir, filename)
                                    
                                    try:
                                        # Determinar categoria para o banco de dados
                                        if section == 'header' and 'logo' in field:
                                            category = 'logos'
                                        elif section == 'banner':
                                            category = 'banners'
                                        else:
                                            category = 'images'
                                        
                                        # Usar helper para salvar de forma persistente (banco primeiro, depois arquivo)
                                        from upload_helper import save_image_persistent
                                        image_path = save_image_persistent(image_file, category=category, upload_base=upload_base)
                                        
                                        if image_path:
                                            if key_tuple not in updates:
                                                updates[key_tuple] = {'content': None, 'image_path': None}
                                            updates[key_tuple]['image_path'] = image_path
                                        else:
                                            flash(f'Erro: Arquivo {filename} não foi salvo corretamente.', 'error')
                                    except Exception as e:
                                        flash(f'Erro ao salvar imagem {filename}: {str(e)}', 'error')
                                        import traceback
                                        traceback.print_exc()
                                else:
                                    flash(f'Formato de campo inválido: {key}', 'error')
                            else:
                                flash(f'Tipo de arquivo não permitido: {filename_value}', 'error')
            
            # Agora aplicar todas as atualizações, buscando valores existentes quando necessário
            for (section, field), data in updates.items():
                # Buscar valores existentes
                existing = conn.execute('''SELECT content, image_path FROM site_content 
                                          WHERE section=? AND field=?''',
                                      (section, field)).fetchone()
                
                # Usar novos valores ou manter existentes
                # Se content foi definido (mesmo que seja string vazia), usar o novo valor
                if data['content'] is not None:
                    content_value = data['content']
                else:
                    content_value = existing['content'] if existing and existing['content'] else None
                
                # Se image_path foi definido, usar o novo valor
                if data['image_path'] is not None:
                    image_path_value = data['image_path']
                else:
                    image_path_value = existing['image_path'] if existing and existing['image_path'] else None
                
                # Inserir ou atualizar - adaptar para PostgreSQL ou SQLite
                _execute_insert_replace(conn, 'site_content', 
                                       ['section', 'field', 'content', 'image_path'],
                                       (section, field, content_value, image_path_value),
                                       ['section', 'field'])
            
            if updates:
                conn.commit()
                # Contar quantos campos foram atualizados
                updated_count = len(updates)
                flash(f'Conteúdo salvo com sucesso! ({updated_count} campo(s) atualizado(s))', 'success')
            else:
                flash('Nenhuma alteração foi feita. Verifique se preencheu algum campo.', 'info')
        except Exception as e:
            conn.rollback()
            import traceback
            error_msg = f'Erro ao salvar conteúdo: {str(e)}'
            flash(error_msg, 'error')
            print(f"Erro detalhado: {traceback.format_exc()}")
    
    # Buscar todo o conteúdo
    content_data = {}
    rows = conn.execute('SELECT section, field, content, image_path FROM site_content').fetchall()
    for row in rows:
        if row['section'] not in content_data:
            content_data[row['section']] = {}
        content_data[row['section']][row['field']] = {
            'content': row['content'],
            'image_path': row['image_path']
        }
    
    conn.close()
    return render_template('admin/content.html', content_data=content_data)


@admin_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    """Gerenciar projetos"""
    conn = get_db()
    
    if request.method == 'POST':
        if 'save_section_config' in request.form:
            # Salvar configurações da seção
            section_title = request.form.get('section_title', 'Projetos Recentes')
            section_description = request.form.get('section_description', '')
            filter_all = request.form.get('filter_all', 'Todos')
            filter_type1 = request.form.get('filter_type1', 'Aplicativos Mobile')
            filter_type2 = request.form.get('filter_type2', 'Sites')
            
            _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                                   ('projects', 'title', section_title), ['section', 'field'])
            _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                                   ('projects', 'description', section_description), ['section', 'field'])
            _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                                   ('projects', 'filter_all', filter_all), ['section', 'field'])
            _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                                   ('projects', 'filter_type1', filter_type1), ['section', 'field'])
            _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                                   ('projects', 'filter_type2', filter_type2), ['section', 'field'])
            conn.commit()
            flash('Configurações da seção salvas com sucesso!', 'success')
        elif 'delete' in request.form:
            project_id = request.form.get('delete')
            conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            flash('Projeto removido com sucesso!', 'success')
        else:
            title = request.form.get('title')
            description = request.form.get('description', '')
            link_url = request.form.get('link_url', '#')
            filter_type = request.form.get('filter_type', 'Type 1')
            order_index = int(request.form.get('order_index', 0))
            image_file = request.files.get('image')
            
            image_path = None
            if image_file and image_file.filename and allowed_file(image_file.filename):
                # Usar helper para salvar de forma persistente (banco primeiro, depois arquivo)
                from upload_helper import save_image_persistent
                image_path = save_image_persistent(image_file, category='images', upload_base=current_app.config['UPLOAD_FOLDER'])
            
            project_id = request.form.get('id')
            if project_id:
                if image_path:
                    conn.execute('''UPDATE projects SET title=?, description=?, image_path=?, 
                                  link_url=?, filter_type=?, order_index=?, updated_at=CURRENT_TIMESTAMP
                                  WHERE id=?''',
                               (title, description, image_path, link_url, filter_type, order_index, project_id))
                else:
                    conn.execute('''UPDATE projects SET title=?, description=?, link_url=?,
                                  filter_type=?, order_index=?, updated_at=CURRENT_TIMESTAMP
                                  WHERE id=?''',
                               (title, description, link_url, filter_type, order_index, project_id))
            else:
                conn.execute('''INSERT INTO projects (title, description, image_path, link_url, filter_type, order_index)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                           (title, description, image_path, link_url, filter_type, order_index))
            conn.commit()
            flash('Projeto salvo com sucesso!', 'success')
    
    projects_list = conn.execute('SELECT * FROM projects ORDER BY order_index, id').fetchall()
    
    # Buscar configurações da seção
    projects_section = {}
    rows = conn.execute("SELECT field, content FROM site_content WHERE section='projects'").fetchall()
    for row in rows:
        projects_section[row['field']] = {'content': row['content']}
    
    conn.close()
    
    return render_template('admin/projects.html', projects=projects_list, projects_section=projects_section)


@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    """Gerenciar serviços"""
    conn = get_db()
    
    if request.method == 'POST':
        # Verificar se é atualização da imagem da seção
        if request.form.get('update_section_image') == '1':
            image_file = request.files.get('services_section_image')
            if image_file and image_file.filename and allowed_file(image_file.filename):
                # Tentar salvar no banco de dados primeiro (persistência no Render Free)
                try:
                    from image_storage import save_image_to_db
                    image_path = save_image_to_db(image_file, category='images')
                except Exception as e:
                    print(f"Erro ao salvar no banco, usando fallback: {e}")
                    image_path = None
                
                # Fallback para arquivo local se não conseguiu salvar no banco
                if not image_path:
                    from upload_helper import save_image_persistent
                    image_path = save_image_persistent(image_file, category='images', upload_base=current_app.config['UPLOAD_FOLDER'])
                
                if image_path:
                    _execute_insert_replace(conn, 'site_content', 
                                           ['section', 'field', 'content', 'image_path'],
                                           ('services', 'section_image', None, image_path),
                                           ['section', 'field'])
                conn.commit()
                flash('Imagem da seção salva com sucesso!', 'success')
            else:
                flash('Por favor, selecione uma imagem válida.', 'error')
        
        elif 'delete' in request.form:
            service_id = request.form.get('delete')
            conn.execute('DELETE FROM services WHERE id = ?', (service_id,))
            conn.commit()
            flash('Serviço removido com sucesso!', 'success')
        else:
            title = request.form.get('title')
            description = request.form.get('description', '')
            icon_class = request.form.get('icon_class', '')
            order_index = int(request.form.get('order_index', 0))
            
            service_id = request.form.get('id')
            if service_id:
                conn.execute('''UPDATE services SET title=?, description=?, icon_class=?, 
                              order_index=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                           (title, description, icon_class, order_index, service_id))
            else:
                conn.execute('''INSERT INTO services (title, description, icon_class, order_index)
                               VALUES (?, ?, ?, ?)''',
                           (title, description, icon_class, order_index))
            conn.commit()
            flash('Serviço salvo com sucesso!', 'success')
    
    services_list = conn.execute('SELECT * FROM services ORDER BY order_index, id').fetchall()
    
    # Buscar imagem da seção de serviços
    services_image = conn.execute('''SELECT image_path FROM site_content 
                                    WHERE section=? AND field=?''',
                                ('services', 'section_image')).fetchone()
    services_section_image = services_image['image_path'] if services_image and services_image['image_path'] else None
    
    conn.close()
    
    return render_template('admin/services.html', 
                         services=services_list,
                         services_section_image=services_section_image)


@admin_bp.route('/pricing', methods=['GET', 'POST'])
@login_required
def pricing():
    """Gerenciar preços"""
    conn = get_db()
    
    if request.method == 'POST':
        if 'delete' in request.form:
            pricing_id = request.form.get('delete')
            conn.execute('DELETE FROM pricing WHERE id = ?', (pricing_id,))
            conn.commit()
            flash('Plano removido com sucesso!', 'success')
        else:
            name = request.form.get('name')
            price = float(request.form.get('price', 0))
            features = request.form.get('features', '')
            is_popular = 1 if request.form.get('is_popular') == 'on' else 0
            order_index = int(request.form.get('order_index', 0))
            
            pricing_id = request.form.get('id')
            if pricing_id:
                conn.execute('''UPDATE pricing SET name=?, price=?, features=?, is_popular=?, 
                              order_index=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                           (name, price, features, is_popular, order_index, pricing_id))
            else:
                conn.execute('''INSERT INTO pricing (name, price, features, is_popular, order_index)
                               VALUES (?, ?, ?, ?, ?)''',
                           (name, price, features, is_popular, order_index))
            conn.commit()
            flash('Plano salvo com sucesso!', 'success')
    
    pricing_list = conn.execute('SELECT * FROM pricing ORDER BY order_index, id').fetchall()
    conn.close()
    
    return render_template('admin/pricing.html', pricing_list=pricing_list)


@admin_bp.route('/footer', methods=['GET', 'POST'])
@login_required
def footer():
    """Gerenciar rodapé"""
    conn = get_db()
    
    if request.method == 'POST':
        # Links do rodapé
        links = request.form.getlist('footer_link[]')
        link_texts = request.form.getlist('footer_link_text[]')
        
        # Remover links antigos
        conn.execute("DELETE FROM site_content WHERE section='footer' AND field LIKE 'link_%'")
        
        # Inserir novos links
        for i, (link, text) in enumerate(zip(links, link_texts)):
            if link and text:
                conn.execute('''INSERT INTO site_content (section, field, content)
                               VALUES (?, ?, ?)''',
                           ('footer', f'link_{i}', f'{text}|{link}'))
        
        # Links de redes sociais
        social_facebook = request.form.get('social_facebook', '').strip()
        social_twitter = request.form.get('social_twitter', '').strip()
        social_google = request.form.get('social_google', '').strip()
        social_instagram = request.form.get('social_instagram', '').strip()
        
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'social_facebook', social_facebook), ['section', 'field'])
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'social_twitter', social_twitter), ['section', 'field'])
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'social_google', social_google), ['section', 'field'])
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'social_instagram', social_instagram), ['section', 'field'])
        
        # Outros campos do rodapé
        copyright_text = request.form.get('copyright_text', '')
        rights_text = request.form.get('rights_text', '')
        
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'copyright_text', copyright_text), ['section', 'field'])
        _execute_insert_replace(conn, 'site_content', ['section', 'field', 'content'],
                               ('footer', 'rights_text', rights_text), ['section', 'field'])
        
        conn.commit()
        flash('Rodapé atualizado com sucesso!', 'success')
    
    # Buscar dados do rodapé
    footer_data = {}
    rows = conn.execute("SELECT field, content FROM site_content WHERE section='footer'").fetchall()
    for row in rows:
        footer_data[row['field']] = row['content']
    
    # Separar links
    footer_links = []
    for key, value in footer_data.items():
        if key.startswith('link_'):
            if '|' in value:
                text, url = value.split('|', 1)
                footer_links.append({'text': text, 'url': url})
    
    conn.close()
    return render_template('admin/footer.html', footer_data=footer_data, footer_links=footer_links)


@admin_bp.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    """Gerenciar mensagens de contato"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    
    if request.method == 'POST':
        if 'mark_read' in request.form:
            message_id = request.form.get('mark_read')
            conn.execute('UPDATE contact_messages SET is_read = 1 WHERE id = ?', (message_id,))
            conn.commit()
            flash('Mensagem marcada como lida!', 'success')
        elif 'mark_unread' in request.form:
            message_id = request.form.get('mark_unread')
            conn.execute('UPDATE contact_messages SET is_read = 0 WHERE id = ?', (message_id,))
            conn.commit()
            flash('Mensagem marcada como não lida!', 'success')
        elif 'delete' in request.form:
            message_id = request.form.get('delete')
            conn.execute('DELETE FROM contact_messages WHERE id = ?', (message_id,))
            conn.commit()
            flash('Mensagem removida com sucesso!', 'success')
    
    # Buscar todas as mensagens, ordenadas por data (mais recentes primeiro)
    messages = conn.execute('''SELECT * FROM contact_messages 
                              ORDER BY created_at DESC''').fetchall()
    
    conn.close()
    return render_template('admin/contacts.html', messages=messages)


@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """Gerenciar usuários do admin"""
    conn = get_db()
    
    if request.method == 'POST':
        if 'delete' in request.form:
            # Excluir usuário
            user_id = request.form.get('delete')
            # Verificar se não é o próprio usuário logado
            if int(user_id) != session.get('admin_user_id'):
                try:
                    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    conn.commit()
                    flash('Usuário excluído com sucesso!', 'success')
                except Exception as e:
                    conn.rollback()
                    flash(f'Erro ao excluir usuário: {str(e)}', 'error')
            else:
                flash('Você não pode excluir seu próprio usuário!', 'error')
        else:
            # Criar ou editar usuário
            user_id = request.form.get('user_id')
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username:
                flash('O nome de usuário é obrigatório!', 'error')
            else:
                try:
                    if user_id:
                        # Editar usuário existente
                        existing_user = conn.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
                        if not existing_user:
                            flash('Usuário não encontrado!', 'error')
                        else:
                            # Verificar se o username já existe em outro usuário
                            check_user = conn.execute('SELECT id FROM users WHERE username = ? AND id != ?', (username, user_id)).fetchone()
                            if check_user:
                                flash('Este nome de usuário já está em uso!', 'error')
                            else:
                                if password:
                                    # Atualizar senha
                                    if len(password) < 6:
                                        flash('A senha deve ter no mínimo 6 caracteres!', 'error')
                                    else:
                                        password_hash = generate_password_hash(password)
                                        conn.execute('UPDATE users SET username = ?, password = ? WHERE id = ?',
                                                   (username, password_hash, user_id))
                                        conn.commit()
                                        flash('Usuário atualizado com sucesso!', 'success')
                                else:
                                    # Apenas atualizar username
                                    conn.execute('UPDATE users SET username = ? WHERE id = ?',
                                               (username, user_id))
                                    conn.commit()
                                    flash('Usuário atualizado com sucesso!', 'success')
                    else:
                        # Criar novo usuário
                        # Verificar se o username já existe
                        existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
                        if existing:
                            flash('Este nome de usuário já está em uso!', 'error')
                        else:
                            if not password or len(password) < 6:
                                flash('A senha é obrigatória e deve ter no mínimo 6 caracteres!', 'error')
                            else:
                                password_confirm = request.form.get('password_confirm', '').strip()
                                if password != password_confirm:
                                    flash('As senhas não coincidem!', 'error')
                                else:
                                    password_hash = generate_password_hash(password)
                                    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                                               (username, password_hash))
                                    conn.commit()
                                    flash('Usuário criado com sucesso!', 'success')
                except Exception as e:
                    conn.rollback()
                    import traceback
                    flash(f'Erro ao salvar usuário: {str(e)}', 'error')
                    print(f"Erro detalhado: {traceback.format_exc()}")
    
    # Buscar todos os usuários
    users_list = conn.execute('SELECT id, username, created_at FROM users ORDER BY created_at DESC').fetchall()
    
    # Obter ID do usuário logado
    current_user = conn.execute('SELECT id FROM users WHERE username = ?', (session.get('admin_username'),)).fetchone()
    current_user_id = current_user['id'] if current_user else None
    
    conn.close()
    return render_template('admin/users.html', users=users_list, current_user_id=current_user_id)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configurações gerais"""
    conn = get_db()
    
    if request.method == 'POST':
        for key, value in request.form.items():
            if key != 'submit':
                _execute_insert_replace(conn, 'settings', ['key', 'value'],
                                       (key, value), ['key'])
        conn.commit()
        flash('Configurações salvas com sucesso!', 'success')
    
    settings_data = {}
    rows = conn.execute('SELECT key, value FROM settings').fetchall()
    for row in rows:
        settings_data[row['key']] = row['value']
    
    conn.close()
    return render_template('admin/settings.html', settings=settings_data)


@admin_bp.route('/carousel', methods=['GET', 'POST'])
@login_required
def carousel():
    """Gerenciar slides do carrossel"""
    conn = get_db()
    
    if request.method == 'POST':
        if 'delete' in request.form:
            slide_id = request.form.get('delete')
            conn.execute('DELETE FROM carousel_slides WHERE id = ?', (slide_id,))
            conn.commit()
            flash('Slide removido com sucesso!', 'success')
        else:
            title = request.form.get('title')
            description = request.form.get('description', '')
            button_text = request.form.get('button_text', 'Entre em contato')
            button_link = request.form.get('button_link', '#modalCta')
            order_index = int(request.form.get('order_index', 0))
            is_active = 1 if request.form.get('is_active') == 'on' else 0
            image_file = request.files.get('image')
            
            slide_id = request.form.get('id')
            
            image_path = None
            if image_file and image_file.filename and allowed_file(image_file.filename):
                # Usar helper para salvar de forma persistente (banco primeiro, depois arquivo)
                from upload_helper import save_image_persistent
                image_path = save_image_persistent(image_file, category='banners', upload_base=current_app.config['UPLOAD_FOLDER'])
            elif slide_id:
                # Buscar image_path atual se não foi enviada nova imagem
                existing = conn.execute('SELECT image_path FROM carousel_slides WHERE id = ?', (slide_id,)).fetchone()
                if existing:
                    image_path = existing['image_path']
            
            if slide_id:
                if image_path:
                    conn.execute('''UPDATE carousel_slides SET title=?, description=?, image_path=?, 
                                  button_text=?, button_link=?, order_index=?, is_active=?, 
                                  updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                               (title, description, image_path, button_text, button_link, order_index, is_active, slide_id))
                else:
                    conn.execute('''UPDATE carousel_slides SET title=?, description=?, 
                                  button_text=?, button_link=?, order_index=?, is_active=?, 
                                  updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                               (title, description, button_text, button_link, order_index, is_active, slide_id))
            else:
                if not image_path:
                    flash('Por favor, selecione uma imagem para o slide.', 'error')
                else:
                    conn.execute('''INSERT INTO carousel_slides (title, description, image_path, 
                                  button_text, button_link, order_index, is_active)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (title, description, image_path, button_text, button_link, order_index, is_active))
            conn.commit()
            flash('Slide salvo com sucesso!', 'success')
    
    slides = conn.execute('SELECT * FROM carousel_slides ORDER BY order_index, id').fetchall()
    conn.close()
    
    return render_template('admin/carousel.html', slides=slides)


@admin_bp.route('/company-stats', methods=['GET', 'POST'])
@login_required
def company_stats():
    """Gerenciar estatísticas da empresa e anos de experiência"""
    conn = get_db()
    
    if request.method == 'POST':
        # Processar imagem de cliente
        if 'delete_client_image' in request.form:
            image_id = request.form.get('delete_client_image')
            conn.execute('DELETE FROM client_images WHERE id = ?', (image_id,))
            conn.commit()
            flash('Imagem removida com sucesso!', 'success')
        elif 'client_image_id' in request.form or request.files.get('client_image_file'):
            # Adicionar ou editar imagem de cliente
            image_id = request.form.get('client_image_id')
            image_file = request.files.get('client_image_file')
            alt_text = request.form.get('client_image_alt', '')
            link_url = request.form.get('client_image_link', '#')
            order_index = int(request.form.get('client_image_order', 0))
            
            if image_file and image_file.filename and allowed_file(image_file.filename):
                # Usar helper para salvar de forma persistente (banco primeiro, depois arquivo)
                from upload_helper import save_image_persistent
                image_path = save_image_persistent(image_file, category='images', upload_base=current_app.config['UPLOAD_FOLDER'])
                
                if image_path and image_id:
                    conn.execute('''UPDATE client_images SET image_path=?, alt_text=?, link_url=?, 
                                  order_index=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                               (image_path, alt_text, link_url, order_index, image_id))
                else:
                    conn.execute('''INSERT INTO client_images (image_path, alt_text, link_url, order_index)
                                   VALUES (?, ?, ?, ?)''',
                               (image_path, alt_text, link_url, order_index))
                conn.commit()
                flash('Imagem salva com sucesso!', 'success')
        else:
            # Atualizar estatísticas
            years = int(request.form.get('years', 10))
            title = request.form.get('title', 'Anos de Experiência')
            description = request.form.get('description', '')
            button_text = request.form.get('button_text', 'Entre em contato')
            button_link = request.form.get('button_link', '#')
            
            stat1_number = request.form.get('stat1_number', '2')
            stat1_symbol = request.form.get('stat1_symbol', 'k')
            stat1_label = request.form.get('stat1_label', 'aplicativos desenvolvidos')
            stat2_number = request.form.get('stat2_number', '40')
            stat2_symbol = request.form.get('stat2_symbol', '')
            stat2_label = request.form.get('stat2_label', 'Consultores')
            stat3_number = request.form.get('stat3_number', '12')
            stat3_symbol = request.form.get('stat3_symbol', '')
            stat3_label = request.form.get('stat3_label', 'Prêmios conquistados')
            stat4_number = request.form.get('stat4_number', '160')
            stat4_symbol = request.form.get('stat4_symbol', '')
            stat4_label = request.form.get('stat4_label', 'Funcionários')
            
            conn.execute('''UPDATE company_stats SET years=?, title=?, description=?, button_text=?, 
                          button_link=?, stat1_number=?, stat1_symbol=?, stat1_label=?,
                          stat2_number=?, stat2_symbol=?, stat2_label=?,
                          stat3_number=?, stat3_symbol=?, stat3_label=?,
                          stat4_number=?, stat4_symbol=?, stat4_label=?,
                          updated_at=CURRENT_TIMESTAMP WHERE id=1''',
                       (years, title, description, button_text, button_link,
                        stat1_number, stat1_symbol, stat1_label,
                        stat2_number, stat2_symbol, stat2_label,
                        stat3_number, stat3_symbol, stat3_label,
                        stat4_number, stat4_symbol, stat4_label))
            conn.commit()
            flash('Estatísticas salvas com sucesso!', 'success')
    
    # Buscar estatísticas
    stats = conn.execute('SELECT * FROM company_stats WHERE id=1').fetchone()
    if not stats:
        # Criar registro padrão se não existir
        conn.execute('''INSERT INTO company_stats (id, years, title) VALUES (1, 10, 'Anos de Experiência')''')
        conn.commit()
        stats = conn.execute('SELECT * FROM company_stats WHERE id=1').fetchone()
    
    # Buscar imagens de clientes
    client_images = conn.execute('SELECT * FROM client_images ORDER BY order_index, id').fetchall()
    
    conn.close()
    return render_template('admin/company_stats.html', stats=stats, client_images=client_images)


@admin_bp.route('/feature-tabs', methods=['GET', 'POST'])
@login_required
def feature_tabs():
    """Gerenciar abas da seção 'Obtenha Mais Conosco'"""
    conn = get_db()
    
    if request.method == 'POST':
        if 'delete' in request.form:
            tab_id = request.form.get('delete')
            conn.execute('DELETE FROM feature_tabs WHERE id = ?', (tab_id,))
            conn.commit()
            flash('Aba removida com sucesso!', 'success')
        elif 'delete_feature_image' in request.form:
            # Remover imagem do carrossel lateral
            image_path = request.form.get('delete_feature_image')
            # Buscar se existe no site_content
            conn.execute("DELETE FROM site_content WHERE section='feature_tabs' AND image_path=?", (image_path,))
            conn.commit()
            flash('Imagem removida com sucesso!', 'success')
        elif 'upload_feature_images' in request.form:
            # Upload de múltiplas imagens
            image_files = request.files.getlist('feature_images[]')
            uploaded = 0
            for image_file in image_files:
                if image_file.filename and allowed_file(image_file.filename):
                    # Usar helper para salvar de forma persistente (banco primeiro, depois arquivo)
                    from upload_helper import save_image_persistent
                    image_path = save_image_persistent(image_file, category='images', upload_base=current_app.config['UPLOAD_FOLDER'])
                    
                    if image_path:
                        conn.execute('''INSERT INTO site_content (section, field, image_path, updated_at)
                                       VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                                   ('feature_tabs', f'carousel_image_{uploaded}', image_path))
                        uploaded += 1
            if uploaded > 0:
                conn.commit()
                flash(f'{uploaded} imagem(ns) carregada(s) com sucesso!', 'success')
        else:
            title = request.form.get('title')
            content = request.form.get('content', '')
            button1_text = request.form.get('button1_text', 'Entre em contato')
            button1_link = request.form.get('button1_link', '#modalCta')
            button2_text = request.form.get('button2_text', 'Saiba Mais')
            button2_link = request.form.get('button2_link', '#')
            order_index = int(request.form.get('order_index', 0))
            is_active = 1 if request.form.get('is_active') == 'on' else 0
            
            tab_id = request.form.get('id')
            if tab_id:
                conn.execute('''UPDATE feature_tabs SET title=?, content=?, button1_text=?, 
                              button1_link=?, button2_text=?, button2_link=?, order_index=?, 
                              is_active=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                           (title, content, button1_text, button1_link, button2_text, button2_link, 
                            order_index, is_active, tab_id))
            else:
                conn.execute('''INSERT INTO feature_tabs (title, content, button1_text, button1_link, 
                              button2_text, button2_link, order_index, is_active)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (title, content, button1_text, button1_link, button2_text, button2_link, 
                            order_index, is_active))
            conn.commit()
            flash('Aba salva com sucesso!', 'success')
    
    tabs = conn.execute('SELECT * FROM feature_tabs ORDER BY order_index, id').fetchall()
    
    # Buscar imagens do carrossel
    feature_images_rows = conn.execute("SELECT image_path FROM site_content WHERE section='feature_tabs' AND field LIKE 'carousel_image_%' ORDER BY field").fetchall()
    feature_images = [row['image_path'] for row in feature_images_rows]
    
    conn.close()
    return render_template('admin/feature_tabs.html', tabs=tabs, feature_images=feature_images)


# Inicializar banco de dados quando o módulo for importado
init_db()

