# Deploy no Render.com

## Configuração Rápida

### 1. Conectar Repositório
- Acesse [render.com](https://render.com)
- Conecte seu repositório GitHub
- Selecione o repositório `rsdev`

### 2. Criar Novo Web Service
- **Nome:** rsdev (ou seu nome preferido)
- **Ambiente:** Python 3
- **Branch:** main (ou master)
- **Root Directory:** (deixe em branco)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 app:app`

### 3. Variáveis de Ambiente
Adicione as seguintes variáveis de ambiente no painel do Render:

```
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-muito-forte-aqui-aleatoria
PORT=10000
```

**Opcionais (para email):**
```
MAIL_USE_SMTP=True
MAIL_HOST=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
MAIL_RECIPIENT=destinatario@gmail.com
```

**Opcionais (para reCaptcha):**
```
RECAPTCHA_SITE_KEY=sua-chave-site
RECAPTCHA_SECRET_KEY=sua-chave-secreta
```

### 4. Configurações Adicionais
- **Instance Type:** Free (ou plano pago se necessário)
- **Health Check Path:** `/` (padrão)

### 5. Deploy
- Clique em "Create Web Service"
- Aguarde o build e deploy
- Seu site estará disponível em `https://seu-app.onrender.com`

## Importante

⚠️ **Altere a SECRET_KEY** para uma chave forte e aleatória em produção!

⚠️ **Altere as credenciais padrão do admin** após o primeiro acesso:
- URL: `https://seu-app.onrender.com/admin`
- Usuário padrão: `admin`
- Senha padrão: `admin123`

## Notas

- O Render define automaticamente a variável `PORT`, então a aplicação detecta automaticamente o ambiente de produção
- O banco de dados SQLite será criado automaticamente na primeira execução
- Para persistência do banco de dados, considere usar Render Disk ou PostgreSQL (para produção)

