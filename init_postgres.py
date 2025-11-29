"""
Script para inicializar o banco de dados PostgreSQL no Render
Cria todas as tabelas necessárias e insere dados padrão
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

# URL do banco de dados PostgreSQL
# Usa a variável de ambiente ou a URL padrão fornecida
DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://raisilva:mKvWcbLKL78ODmfIQRauoC1RDrbb3M3W@dpg-d4l4rtk9c44c73fadkpg-a.oregon-postgres.render.com/rsdb_a8ag'

# Converter postgres:// para postgresql:// se necessário
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def check_postgres_initialized():
    """Verifica se o banco PostgreSQL já foi inicializado (verifica se a tabela users existe)"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # Usar URL padrão se não estiver na variável de ambiente
            database_url = 'postgresql://raisilva:mKvWcbLKL78ODmfIQRauoC1RDrbb3M3W@dpg-d4l4rtk9c44c73fadkpg-a.oregon-postgres.render.com/rsdb_a8ag'
        
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url, sslmode='require')
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'users'
            );
        """)
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"⚠️ Erro ao verificar inicialização do PostgreSQL: {e}")
        return False

def init_postgres_db():
    """Inicializa o banco de dados PostgreSQL com todas as tabelas e dados padrão"""
    
    database_url = os.environ.get('DATABASE_URL') or DATABASE_URL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Verificar se já foi inicializado
    try:
        if check_postgres_initialized():
            print("✓ Banco PostgreSQL já inicializado, pulando criação de tabelas...")
            return
    except Exception as e:
        print(f"⚠️ Aviso ao verificar inicialização: {e}")
        print("Continuando com inicialização...")
    
    print("Conectando ao banco de dados PostgreSQL...")
    conn = psycopg2.connect(database_url, sslmode='require')
    cursor = conn.cursor()
    
    try:
        print("Criando tabelas...")
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de conteúdo do site
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_content (
                id SERIAL PRIMARY KEY,
                section VARCHAR(255) NOT NULL,
                field VARCHAR(255) NOT NULL,
                content TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(section, field)
            )
        ''')
        
        # Tabela de projetos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                image_path TEXT,
                link_url TEXT,
                filter_type VARCHAR(255),
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de serviços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                icon_class VARCHAR(255),
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de preços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                features TEXT,
                is_popular INTEGER DEFAULT 0,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de posts do blog
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                image_path TEXT,
                publish_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de configurações gerais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de estatísticas da empresa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_stats (
                id SERIAL PRIMARY KEY,
                years INTEGER DEFAULT 10,
                title VARCHAR(255) DEFAULT 'Anos de Experiência',
                description TEXT,
                button_text VARCHAR(255) DEFAULT 'Entre em contato',
                button_link VARCHAR(255) DEFAULT '#',
                stat1_number VARCHAR(50) DEFAULT '2',
                stat1_symbol VARCHAR(10) DEFAULT 'k',
                stat1_label VARCHAR(255) DEFAULT 'aplicativos desenvolvidos',
                stat2_number VARCHAR(50) DEFAULT '40',
                stat2_symbol VARCHAR(10) DEFAULT '',
                stat2_label VARCHAR(255) DEFAULT 'Consultores',
                stat3_number VARCHAR(50) DEFAULT '12',
                stat3_symbol VARCHAR(10) DEFAULT '',
                stat3_label VARCHAR(255) DEFAULT 'Prêmios conquistados',
                stat4_number VARCHAR(50) DEFAULT '160',
                stat4_symbol VARCHAR(10) DEFAULT '',
                stat4_label VARCHAR(255) DEFAULT 'Funcionários',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de imagens de clientes/parceiros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_images (
                id SERIAL PRIMARY KEY,
                image_path TEXT NOT NULL,
                alt_text VARCHAR(255),
                link_url TEXT,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de abas da seção "Obtenha Mais Conosco"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_tabs (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                button1_text VARCHAR(255) DEFAULT 'Entre em contato',
                button1_link VARCHAR(255) DEFAULT '#modalCta',
                button2_text VARCHAR(255) DEFAULT 'Saiba Mais',
                button2_link VARCHAR(255) DEFAULT '#',
                order_index INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de slides do carrossel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousel_slides (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                image_path TEXT NOT NULL,
                button_text VARCHAR(255) DEFAULT 'Entre em contato',
                button_link VARCHAR(255) DEFAULT '#modalCta',
                order_index INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de mensagens de contato
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_messages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                message TEXT,
                phone VARCHAR(255),
                subject VARCHAR(255),
                form_type VARCHAR(255) DEFAULT 'contact',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("✓ Tabelas criadas com sucesso!")
        
        # Verificar se já existe usuário admin
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("Criando usuário admin padrão...")
            password_hash = generate_password_hash('admin123')
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                          ('admin', password_hash))
            conn.commit()
            print("✓ Usuário admin criado (usuário: admin, senha: admin123)")
        else:
            print("✓ Usuário admin já existe")
        
        # Inicializar conteúdo padrão
        print("Inicializando conteúdo padrão...")
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
            cursor.execute('''
                INSERT INTO site_content (section, field, content, image_path)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (section, field) DO NOTHING
            ''', (section, field, content, image_path))
        
        conn.commit()
        print("✓ Conteúdo padrão inicializado")
        
        # Inicializar slides padrão do carrossel
        cursor.execute('SELECT COUNT(*) FROM carousel_slides')
        slide_count = cursor.fetchone()[0]
        
        if slide_count == 0:
            print("Inicializando slides do carrossel...")
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
                cursor.execute('''
                    INSERT INTO carousel_slides (title, description, image_path, order_index)
                    VALUES (%s, %s, %s, %s)
                ''', (title, description, image_path, order))
            conn.commit()
            print("✓ Slides do carrossel inicializados")
        
        # Inicializar serviços padrão
        cursor.execute('SELECT COUNT(*) FROM services')
        service_count = cursor.fetchone()[0]
        
        if service_count == 0:
            print("Inicializando serviços padrão...")
            default_services = [
                ('SOLUÇÕES CORPORATIVAS',
                 'Precisa de software específico para sua empresa? Estamos prontos para desenvolvê-lo!',
                 'linearicons-phone-in-out', 0),
                ('SOLUÇÕES PARA CALL CENTER',
                 'Nossos especialistas fornecem produtos personalizados de qualquer complexidade para call centers.',
                 'linearicons-headset', 1),
                ('DESENVOLVIMENTO NA NUVEM',
                 'Também podemos oferecer soluções confiáveis de desenvolvimento na nuvem.',
                 'linearicons-outbox', 2),
            ]
            for title, description, icon_class, order in default_services:
                cursor.execute('''
                    INSERT INTO services (title, description, icon_class, order_index)
                    VALUES (%s, %s, %s, %s)
                ''', (title, description, icon_class, order))
            conn.commit()
            print("✓ Serviços padrão inicializados")
        
        # Inicializar estatísticas da empresa
        cursor.execute('SELECT COUNT(*) FROM company_stats')
        stats_count = cursor.fetchone()[0]
        
        if stats_count == 0:
            print("Inicializando estatísticas da empresa...")
            cursor.execute('''
                INSERT INTO company_stats 
                (years, title, description, button_text, button_link,
                 stat1_number, stat1_symbol, stat1_label,
                 stat2_number, stat2_symbol, stat2_label,
                 stat3_number, stat3_symbol, stat3_label,
                 stat4_number, stat4_symbol, stat4_label)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (10, 'Anos de Experiência', 
                  'RatherApp é uma equipe de designers e desenvolvedores de aplicativos altamente experientes criando software único para você.',
                  'Entre em contato', '#',
                  '2', 'k', 'aplicativos desenvolvidos',
                  '40', '', 'Consultores',
                  '12', '', 'Prêmios conquistados',
                  '160', '', 'Funcionários'))
            conn.commit()
            print("✓ Estatísticas da empresa inicializadas")
        
        # Inicializar imagens de clientes padrão
        cursor.execute('SELECT COUNT(*) FROM client_images')
        client_images_count = cursor.fetchone()[0]
        
        if client_images_count == 0:
            print("Inicializando imagens de clientes...")
            default_client_images = [
                ('images/clients-9-270x117.png', 'Cliente 1', '#', 0),
                ('images/clients-10-270x117.png', 'Cliente 2', '#', 1),
                ('images/clients-3-270x117.png', 'Cliente 3', '#', 2),
                ('images/clients-11-270x117.png', 'Cliente 4', '#', 3),
            ]
            for image_path, alt_text, link_url, order in default_client_images:
                cursor.execute('''
                    INSERT INTO client_images (image_path, alt_text, link_url, order_index)
                    VALUES (%s, %s, %s, %s)
                ''', (image_path, alt_text, link_url, order))
            conn.commit()
            print("✓ Imagens de clientes inicializadas")
        
        # Inicializar abas "Obtenha Mais Conosco"
        cursor.execute('SELECT COUNT(*) FROM feature_tabs')
        tabs_count = cursor.fetchone()[0]
        
        if tabs_count == 0:
            print("Inicializando abas 'Obtenha Mais Conosco'...")
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
                cursor.execute('''
                    INSERT INTO feature_tabs (title, content, order_index)
                    VALUES (%s, %s, %s)
                ''', (title, content, order))
            conn.commit()
            print("✓ Abas 'Obtenha Mais Conosco' inicializadas")
        
        # Inicializar planos de preço padrão
        cursor.execute('SELECT COUNT(*) FROM pricing')
        pricing_count = cursor.fetchone()[0]
        
        if pricing_count == 0:
            print("Inicializando planos de preço...")
            default_pricing = [
                ('básico', 500.00, 'Desenvolvimento de conceito\nDesign de interface', 0, 0),
                ('Otimizado', 800.00, 'Desenvolvimento de conceito\nDesign de interface\nGerenciamento de configuração\nGarantia de qualidade de software', 1, 1),
                ('Ultimate', 1200.00, 'Desenvolvimento de conceito\nDesign de interface\nGerenciamento de configuração\nGarantia de qualidade de software\nIntegração de aplicativo', 0, 2),
            ]
            for name, price, features, is_popular, order in default_pricing:
                cursor.execute('''
                    INSERT INTO pricing (name, price, features, is_popular, order_index)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (name, price, features, is_popular, order))
            conn.commit()
            print("✓ Planos de preço inicializados")
        
        # Inicializar conteúdo da seção de projetos
        cursor.execute("SELECT COUNT(*) FROM site_content WHERE section='projects' AND field='title'")
        projects_section_count = cursor.fetchone()[0]
        
        if projects_section_count == 0:
            print("Inicializando seção de projetos...")
            default_projects_section = [
                ('projects', 'title', 'Projetos Recentes', None),
                ('projects', 'description', 'Em nosso portfólio, você pode navegar pelos produtos mais recentes desenvolvidos para nossos clientes para diferentes propósitos corporativos. Nossa equipe qualificada de designers de interface e desenvolvedores de software está sempre pronta para criar algo único para você.', None),
            ]
            for section, field, content, image_path in default_projects_section:
                cursor.execute('''
                    INSERT INTO site_content (section, field, content, image_path, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (section, field) DO UPDATE
                    SET content = EXCLUDED.content, image_path = EXCLUDED.image_path, updated_at = CURRENT_TIMESTAMP
                ''', (section, field, content, image_path))
            conn.commit()
            print("✓ Seção de projetos inicializada")
        
        # Inicializar filtros de projetos
        cursor.execute("SELECT COUNT(*) FROM site_content WHERE section='projects' AND field LIKE 'filter_%'")
        filters_count = cursor.fetchone()[0]
        
        if filters_count == 0:
            print("Inicializando filtros de projetos...")
            default_filters = [
                ('projects', 'filter_all', 'Todos', None),
                ('projects', 'filter_type1', 'Aplicativos Mobile', None),
                ('projects', 'filter_type2', 'Sites', None),
            ]
            for section, field, content, image_path in default_filters:
                cursor.execute('''
                    INSERT INTO site_content (section, field, content, image_path, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (section, field) DO UPDATE
                    SET content = EXCLUDED.content, image_path = EXCLUDED.image_path, updated_at = CURRENT_TIMESTAMP
                ''', (section, field, content, image_path))
            conn.commit()
            print("✓ Filtros de projetos inicializados")
        
        # Inicializar projetos padrão
        cursor.execute('SELECT COUNT(*) FROM projects')
        projects_count = cursor.fetchone()[0]
        
        if projects_count == 0:
            print("Inicializando projetos padrão...")
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
                cursor.execute('''
                    INSERT INTO projects (title, description, image_path, link_url, filter_type, order_index)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (title, description, image_path, link_url, filter_type, order))
            conn.commit()
            print("✓ Projetos padrão inicializados")
        
        print("\n✅ Banco de dados PostgreSQL inicializado com sucesso!")
        print("📊 Todas as tabelas foram criadas e dados padrão foram inseridos.")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro ao inicializar banco de dados: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_postgres_db()

