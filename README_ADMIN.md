# Painel Administrativo

Sistema completo de gerenciamento de conteúdo para o site.

## Acesso

**URL:** `http://localhost:5000/admin`

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

⚠️ **IMPORTANTE:** Altere a senha padrão em produção!

## Funcionalidades

### 1. Dashboard
- Visão geral com estatísticas
- Acesso rápido a todas as seções

### 2. Conteúdo Geral
- Upload e gerenciamento de logos
- Informações de contato (telefones, emails, endereço)

### 3. Projetos
- Adicionar, editar e remover projetos
- Upload de imagens
- Definir tipo/filtro (Aplicativos Mobile, Sites)
- Ordenação personalizada

### 4. Serviços
- Gerenciar serviços oferecidos
- Definir ícones e descrições
- Ordenação personalizada

### 5. Preços
- Criar e editar planos de preço
- Definir recursos (um por linha)
- Marcar plano como popular
- Ordenação personalizada

### 6. Rodapé
- Gerenciar links do rodapé
- Personalizar textos de copyright e direitos

### 7. Configurações
- Configurações de email (SMTP)
- Configurações do reCaptcha

## Estrutura do Banco de Dados

O sistema usa SQLite (`site_content.db`) com as seguintes tabelas:

- `users` - Usuários do painel admin
- `site_content` - Conteúdo geral (logos, textos, etc.)
- `projects` - Projetos do portfólio
- `services` - Serviços oferecidos
- `pricing` - Planos de preço
- `blog_posts` - Posts do blog (futuro)
- `settings` - Configurações gerais

## Upload de Imagens

As imagens são salvas em uma pasta persistente fora de `static/`:
- `uploads/logos/` - Logos (ou `/data/uploads/logos/` no Render com Render Disk)
- `uploads/banners/` - Banners (ou `/data/uploads/banners/` no Render com Render Disk)
- `uploads/images/` - Outras imagens (ou `/data/uploads/images/` no Render com Render Disk)

**Importante:** A pasta `uploads/` é persistente e não é apagada quando o Render reinicia. Configure a variável de ambiente `UPLOAD_FOLDER` no Render para usar um diretório persistente como `/data/uploads` (Render Disk).

## Segurança

- Senhas são hasheadas com Werkzeug
- Sessões protegidas com decorator `@login_required`
- Validação de tipos de arquivo permitidos
- Sanitização de nomes de arquivo

## Próximos Passos

Para integrar completamente o conteúdo dinâmico no template principal, você precisará:

1. Atualizar `templates/index.html` para usar as variáveis passadas:
   - `site_content` - Conteúdo geral
   - `projects` - Lista de projetos
   - `services` - Lista de serviços
   - `pricing` - Planos de preço
   - `footer_links` - Links do rodapé

2. Exemplo de uso no template:
```jinja2
{% if site_content.header.logo.image_path %}
<img src="{{ url_for('static', filename=site_content.header.logo.image_path) }}">
{% endif %}
```

