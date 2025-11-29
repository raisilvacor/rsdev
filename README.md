# Projeto Flask - Site RatherApp

Este projeto foi convertido de PHP para Python Flask, mantendo todo o HTML5 e layout original.

## Estrutura do Projeto

```
.
├── app.py                 # Aplicação Flask principal
├── forms.py               # Processamento de formulários
├── config.py              # Configurações
├── requirements.txt       # Dependências Python
├── templates/            # Templates HTML
│   └── index.html
├── static/               # Arquivos estáticos
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── fonts/
│   └── video/
└── README.md
```

## Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Execute o script de migração (se ainda não executou):**
```bash
python migrate_to_flask.py
```

3. **Configure as variáveis de ambiente (opcional):**
```bash
# Email
export MAIL_USE_SMTP=True
export MAIL_HOST=smtp.gmail.com
export MAIL_PORT=465
export MAIL_USERNAME=seu-email@gmail.com
export MAIL_PASSWORD=sua-senha
export MAIL_RECIPIENT=destinatario@gmail.com

# reCaptcha
export RECAPTCHA_SITE_KEY=sua-chave-site
export RECAPTCHA_SECRET_KEY=sua-chave-secreta
```

4. **Execute a aplicação:**
```bash
python app.py
```

5. **Acesse no navegador:**
```
http://localhost:5000
```

## Funcionalidades

- ✅ HTML5 mantido exatamente como estava
- ✅ Layout e design preservados
- ✅ Formulários de contato funcionando
- ✅ Validação de formulários
- ✅ Suporte a reCaptcha
- ✅ Envio de emails via SMTP
- ✅ Compatível com a API PHP original

## Endpoints

- `GET /` - Página principal
- `POST /bat/rd-mailform.php` - Processa formulários de contato
- `POST /bat/reCaptcha.php` - Verifica reCaptcha

## Notas

- Os arquivos originais (PHP, CSS, JS, etc.) foram mantidos na raiz
- Os arquivos foram copiados para a estrutura Flask
- O layout e design não foram alterados
- Compatível com o JavaScript original

## Desenvolvimento

Para desenvolvimento com auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## Produção

Para produção, use um servidor WSGI como Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

