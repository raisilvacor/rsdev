"""
Aplicação Flask principal
"""
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import os
from forms import process_contact_form, verify_recaptcha
from admin import admin_bp, init_db
from helpers import get_site_content, get_projects, get_services, get_pricing, get_footer_links, get_carousel_slides, get_company_stats, get_client_images, get_feature_tabs, get_feature_carousel_images, get_projects_section

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurar pasta de uploads persistente (fora de static/)
# Suporta variável de ambiente para Render Disk (ex: /data/uploads)
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Criar subpastas
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)

# Detectar ambiente de produção (Render.com define PORT automaticamente)
is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER') == 'true' or os.environ.get('PORT') is not None
if is_production:
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Registrar blueprint do admin
app.register_blueprint(admin_bp)

# Tornar função helper de imagens disponível nos templates
# A função get_image_url de helpers.py retorna a URL completa (uploaded_file ou static)
from helpers import get_image_url
app.jinja_env.globals['get_image_url'] = get_image_url

# Inicializar banco de dados
# Se DATABASE_URL estiver definido, usar PostgreSQL e inicializar automaticamente
# Caso contrário, inicializar SQLite local
if os.environ.get('DATABASE_URL'):
    try:
        from init_postgres import init_postgres_db
        print("Inicializando banco de dados PostgreSQL...")
        init_postgres_db()
        print("✓ PostgreSQL inicializado com sucesso!")
    except Exception as e:
        print(f"⚠️ Aviso: Erro ao inicializar PostgreSQL: {e}")
        print("A aplicação continuará, mas pode haver problemas se o banco não estiver configurado.")
else:
    init_db()
    print("✓ SQLite inicializado com sucesso!")

# Configurações de email (carregar de config.py ou variáveis de ambiente)
app.config['MAIL_CONFIG'] = {
    'use_smtp': os.environ.get('MAIL_USE_SMTP', 'False').lower() == 'true',
    'host': os.environ.get('MAIL_HOST', 'smtp.gmail.com'),
    'port': int(os.environ.get('MAIL_PORT', 465)),
    'username': os.environ.get('MAIL_USERNAME', 'demo@gmail.com'),
    'password': os.environ.get('MAIL_PASSWORD', 'demopassword'),
    'recipient_email': os.environ.get('MAIL_RECIPIENT', 'demo@gmail.com')
}

# Configurações do reCaptcha
app.config['RECAPTCHA'] = {
    'site_key': os.environ.get('RECAPTCHA_SITE_KEY', '6LfZlSETAAAAAC5VW4R4tQP8Am_to4bM3dddxkEt'),
    'secret_key': os.environ.get('RECAPTCHA_SECRET_KEY', '6LfZlSETAAAAAOi4lh7GHcSOO0pbXnAMJRhnsr7O')
}


@app.route('/')
def index():
    """Página principal"""
    # Carregar conteúdo dinâmico do banco de dados
    site_content = get_site_content()
    projects = get_projects()
    services = get_services()
    pricing = get_pricing()
    footer_links = get_footer_links()
    carousel_slides = get_carousel_slides()
    company_stats = get_company_stats()
    client_images = get_client_images()
    feature_tabs = get_feature_tabs()
    feature_carousel_images = get_feature_carousel_images()
    projects_section = get_projects_section()
    
    return render_template('index.html',
                         site_content=site_content,
                         projects=projects,
                         services=services,
                         pricing=pricing,
                         footer_links=footer_links,
                         carousel_slides=carousel_slides,
                         company_stats=company_stats,
                         client_images=client_images,
                         feature_tabs=feature_tabs,
                         feature_carousel_images=feature_carousel_images,
                         projects_section=projects_section)


@app.route('/bat/rd-mailform.php', methods=['POST'])
def handle_contact_form():
    """
    Processa formulários de contato
    Compatível com a API original do PHP
    """
    try:
        result = process_contact_form(request, app.config['MAIL_CONFIG'])
        # Garante que o resultado é uma string de exatamente 5 caracteres
        result = str(result).strip()
        print(f"✓ Formulário processado, retornando: '{result}' (tamanho: {len(result)})")
        print(f"  Bytes da resposta: {result.encode('utf-8')}")
        # Retorna texto simples sem BOM e sem espaços extras
        # Usa make_response para garantir formato correto
        from flask import make_response
        response = make_response(result)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.status_code = 200
        return response
    except Exception as e:
        print(f"✗ Erro ao processar formulário: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response('MF255', mimetype='text/plain', status=500)


@app.route('/bat/reCaptcha.php', methods=['POST'])
def handle_recaptcha():
    """
    Verifica reCaptcha
    Compatível com a API original do PHP
    """
    try:
        recaptcha_response = request.form.get('g-recaptcha-response', '')
        remote_ip = request.remote_addr
        
        result = verify_recaptcha(
            recaptcha_response,
            remote_ip,
            app.config['RECAPTCHA']['secret_key']
        )
        return result, 200
    except Exception as e:
        return 'CPT002', 500


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Rota para servir arquivos da pasta de uploads persistente (fallback para desenvolvimento local)"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/image/<path:image_key>')
def serve_image_from_db(image_key):
    """Rota para servir imagens diretamente do banco de dados PostgreSQL"""
    from image_storage import get_image_from_db
    from flask import Response
    
    image_data, mime_type, filename = get_image_from_db(image_key)
    
    if image_data:
        return Response(image_data, mimetype=mime_type or 'image/png')
    else:
        # Fallback: tentar servir do sistema de arquivos local (desenvolvimento)
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], image_key)
        except:
            # Se não encontrar, retornar 404
            from flask import abort
            abort(404)


if __name__ == '__main__':
    # Usar porta definida pela variável de ambiente PORT (para Render.com) ou padrão 5000
    port = int(os.environ.get('PORT', 5000))
    debug_mode = not is_production
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

