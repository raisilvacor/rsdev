# Projeto Flask - Site RatherApp

Site institucional desenvolvido em Flask (Python) com painel administrativo completo para gerenciamento de conteúdo.

## 🚀 Funcionalidades

- ✅ Site institucional responsivo em português brasileiro
- ✅ Painel administrativo completo
- ✅ Gerenciamento de conteúdo dinâmico
- ✅ Upload e gerenciamento de imagens
- ✅ Gerenciamento de projetos, serviços, preços
- ✅ Gerenciamento de slides do carrossel
- ✅ Gerenciamento de usuários do admin
- ✅ Botão flutuante do WhatsApp configurável
- ✅ Links de redes sociais configuráveis
- ✅ Sistema de mensagens de contato

## 📋 Estrutura do Projeto

```
.
├── app.py                 # Aplicação Flask principal
├── admin.py               # Blueprint do painel administrativo
├── forms.py               # Processamento de formulários
├── helpers.py             # Funções auxiliares para buscar dados
├── config.py              # Configurações
├── requirements.txt       # Dependências Python
├── site_content.db        # Banco de dados SQLite (não versionado)
├── templates/             # Templates HTML
│   ├── index.html         # Página principal
│   └── admin/             # Templates do painel admin
├── static/                # Arquivos estáticos
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── fonts/
│   ├── video/
│   └── uploads/           # Uploads de imagens (não versionado)
└── README.md
```

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/raisilvacor/rsdev.git
cd rsdev
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
python app.py
```

4. **Acesse no navegador:**
```
http://localhost:5000
```

5. **Acesse o painel administrativo:**
```
http://localhost:5000/admin
```
**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

⚠️ **IMPORTANTE:** Altere a senha padrão após o primeiro acesso!

## ⚙️ Configuração

### Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```bash
# Email (opcional)
MAIL_USE_SMTP=True
MAIL_HOST=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha
MAIL_RECIPIENT=destinatario@gmail.com

# reCaptcha (opcional)
RECAPTCHA_SITE_KEY=sua-chave-site
RECAPTCHA_SECRET_KEY=sua-chave-secreta

# Secret Key (recomendado em produção)
SECRET_KEY=sua-chave-secreta-aqui
```

## 📱 Painel Administrativo

O painel administrativo permite gerenciar:

- **Conteúdo Geral:** Logos, informações de contato, CTA
- **Slides do Carrossel:** Imagens, títulos, descrições, botões
- **Projetos:** Portfólio com filtros e links
- **Serviços:** Serviços oferecidos
- **Preços:** Planos de preços
- **Estatísticas da Empresa:** Números e imagens de clientes
- **Obtenha Mais Conosco:** Abas e carrossel de imagens
- **Rodapé:** Links e redes sociais
- **Usuários:** Gerenciamento de usuários do admin
- **Mensagens de Contato:** Visualizar mensagens recebidas

## 🗄️ Banco de Dados

O projeto usa SQLite (`site_content.db`). O banco é criado automaticamente na primeira execução com dados padrão.

**⚠️ O arquivo `site_content.db` não é versionado no Git por segurança.**

## 🚀 Deploy

### Desenvolvimento
```bash
python app.py
```

### Produção (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Produção (com variáveis de ambiente)
```bash
export FLASK_ENV=production
export SECRET_KEY=sua-chave-secreta-forte
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 Tecnologias Utilizadas

- **Backend:** Flask (Python)
- **Banco de Dados:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript (jQuery)
- **Templates:** Jinja2
- **Autenticação:** Session-based

## 🔒 Segurança

- Senhas armazenadas com hash (Werkzeug)
- Proteção CSRF via Flask sessions
- Validação de uploads de arquivos
- Sanitização de nomes de arquivos
- Proteção contra exclusão do próprio usuário

## 📄 Licença

Este projeto é proprietário.

## 👤 Autor

RatherApp / RSDev
