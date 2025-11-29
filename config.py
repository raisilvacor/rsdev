"""
Arquivo de configuração
As configurações podem ser sobrescritas por variáveis de ambiente
"""
import os

class Config:
    """Configurações da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurações de Email
    MAIL_USE_SMTP = os.environ.get('MAIL_USE_SMTP', 'False').lower() == 'true'
    MAIL_HOST = os.environ.get('MAIL_HOST', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'demo@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'demopassword')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', 'demo@gmail.com')
    
    # Configurações do reCaptcha
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY', '6LfZlSETAAAAAC5VW4R4tQP8Am_to4bM3dddxkEt')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', '6LfZlSETAAAAAOi4lh7GHcSOO0pbXnAMJRhnsr7O')

