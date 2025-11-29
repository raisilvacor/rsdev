"""
Aplicação Flask principal
"""
from flask import Flask, render_template, request, jsonify
import os
from forms import process_contact_form, verify_recaptcha
from admin import admin_bp, init_db
from helpers import get_site_content, get_projects, get_services, get_pricing, get_footer_links, get_carousel_slides, get_company_stats, get_client_images, get_feature_tabs, get_feature_carousel_images, get_projects_section

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Registrar blueprint do admin
app.register_blueprint(admin_bp)

# Inicializar banco de dados
init_db()

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

