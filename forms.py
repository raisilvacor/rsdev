"""
Módulo para processamento de formulários
"""
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from datetime import datetime


def get_remote_ip(request):
    """Obtém o IP remoto do cliente"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-Ip'):
        return request.headers.get('X-Real-Ip')
    return request.remote_addr


def validate_email(email):
    """Valida formato de email"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def extract_emails(text):
    """Extrai emails de um texto"""
    pattern = r"([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)"
    matches = re.findall(pattern, text)
    return [f"{match[0]}@{match[1]}.{match[2]}" for match in matches]


def get_email_template():
    """Retorna o template de email"""
    return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head> 
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="initial-scale=1.0" />
    <meta name="format-detection" content="telephone=no" />
    <title>{subject}</title>
    <style type="text/css">  
    #outlook a { padding: 0; }
    body { width: 100% !important; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; margin: 0; padding: 0; }
    .ExternalClass { width: 100%; }
    .ExternalClass, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div { line-height: 100%; }
    .ExternalClass p { line-height: inherit; }
    #body-layout { margin: 0; padding: 0; width: 100% !important; line-height: 100% !important; }
    img { display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a img { border: none; }
    table td { border-collapse: collapse; }
    table { border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    a { color: orange; outline: none; }
    </style>
  </head>
  <body id="body-layout" style="background: #406c8d;">
    <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td align="center" valign="top" style="padding: 0 15px;background: #406c8d;">
          <table align="center" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td height="15" style="height: 15px; line-height:15px;"></td>
            </tr>
            <tr>
              <td width="600" align="center" valign="top" style="border-radius: 4px; overflow: hidden; box-shadow: 3px 3px 6px 0 rgba(0,0,0,0.2);background: #dde1e6;">
                <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td align="center" valign="top" style="border-top-left-radius: 4px; border-top-right-radius: 4px; overflow: hidden; padding: 0 20px;background: #302f35;">
                      <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td height="30" style="height: 30px; line-height:30px;"></td>
                        </tr>
                        <tr>
                          <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 32px; mso-line-height-rule: exactly; line-height: 32px; font-weight: 400; letter-spacing: 1px;color: #ffffff;">Notificação</td>
                        </tr>
                        <tr>
                          <td height="30" style="height: 30px; line-height:30px;"></td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  <tr>
                    <td align="center" valign="top" style="padding: 0 20px;">
                      <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td height="30" style="height: 30px; line-height:30px;"></td>
                        </tr> 
                        <tr> 
                          <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 22px; font-weight: 400;color: #302f35;">Olá, alguém deixou uma mensagem para você em {site_name}</td> 
                        </tr>
                        <tr> 
                          <td height="20" style="height: 20px; line-height:20px;"></td>
                        </tr>
                        <tr>
                          <td align="center" valign="top">
                            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                              <tr>
                                <td align="center" valign="top" style="background: #d1d5da;">
                                  <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                      <td height="1" style="height: 1px; line-height:1px;"></td>
                                    </tr>
                                  </table>
                                </td>
                              </tr>
                              <tr>
                                <td align="center" valign="top" style="background: #e4e6e9;">
                                  <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                      <td height="2" style="height: 2px; line-height:2px;"></td>
                                    </tr>
                                  </table>
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                        <tr>
                          <td height="20" style="height: 20px; line-height:20px;"></td>
                        </tr>
                        <tr>
                          <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 24px; mso-line-height-rule: exactly; line-height: 30px; font-weight: 700;color: #302f35;">
                            {subject}
                          </td>
                        </tr>
                        <tr>
                          <td height="20" style="height: 20px; line-height:20px;"></td>
                        </tr>
                        <tr>
                          <td align="center" valign="top">
                            <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                              <tr>
                                <td align="center" valign="top">
                                  <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                      <td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Email:</td>
                                      <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{from_email}</td> 
                                    </tr> 
                                    {info_fields}
                                  </table>
                                </td>
                              </tr>
                              <tr>
                                <td height="12" style="height: 12px; line-height:12px;"></td>
                              </tr>
                              <tr>
                                <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">Mensagem:</td>
                              </tr>
                              <tr>
                                <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">
                                  {message}
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                        <tr>
                          <td height="40" style="height: 40px; line-height:40px;"></td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td height="20" style="height: 20px; line-height:20px;"></td>
            </tr>
            <tr>
              <td width="600" align="center" valign="top">
                <table width="100%" align="center" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td align="center" valign="top" style="font-family: Arial, sans-serif; font-size: 12px; mso-line-height-rule: exactly; line-height: 18px; font-weight: 400;color: #a1b4c4;">Este é um email gerado automaticamente, por favor não responda.</td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td height="20" style="height: 20px; line-height:20px;"></td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def process_contact_form(request, mail_config):
    """
    Processa formulário de contato
    Retorna código de status compatível com a API PHP original
    """
    import sqlite3
    
    # Obtém tipo de formulário
    form_type = request.form.get('form-type', 'contact')
    
    if not form_type:
        return 'MF004'
    
    # Obtém dados do formulário
    from_email = request.form.get('email', '')
    from_name = request.form.get('name', 'Sem nome')
    message = request.form.get('message', '')
    phone = request.form.get('phone', '')
    
    if not from_email or not validate_email(from_email):
        return 'MF003'
    
    # Define assunto baseado no tipo
    subject_map = {
        'contact': 'Uma mensagem do visitante do seu site',
        'subscribe': 'Solicitação de inscrição',
        'order': 'Solicitação de pedido',
        'contact-modal': 'Uma mensagem do visitante do seu site'
    }
    subject = subject_map.get(form_type, 'Uma mensagem do visitante do seu site')
    
    # SALVA MENSAGEM NO BANCO DE DADOS PRIMEIRO (sempre salva)
    try:
        conn = sqlite3.connect('site_content.db')
        c = conn.cursor()
        c.execute('''INSERT INTO contact_messages (name, email, message, phone, subject, form_type)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (from_name, from_email, message, phone, subject, form_type))
        conn.commit()
        conn.close()
        print(f"✓ Mensagem salva no banco: {from_name} <{from_email}>")
    except Exception as e:
        print(f"✗ Erro ao salvar mensagem no banco: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continua mesmo se falhar ao salvar
    
    # Verifica se há destinatários configurados para envio de email (opcional)
    recipient_email = mail_config.get('recipient_email', '')
    if not recipient_email or not validate_email(recipient_email):
        # Mensagem já foi salva no banco, então retorna sucesso mesmo sem email configurado
        return 'MF000'
    
    # Prepara campos adicionais para o email
    info_fields = ''
    for key, value in request.form.items():
        if key not in ['counter', 'email', 'message', 'form-type', 'g-recaptcha-response', 'phone'] and value:
            field_name = key.capitalize().replace('_', ' ')
            info_fields += f"""
                                    <tr> 
                                      <td width="110" align="left" valign="top" style="padding: 0 10px 0 0;font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;font-weight: 700;">{field_name}:</td>
                                      <td align="left" valign="top" style="font-family: Arial, sans-serif; font-size: 14px; mso-line-height-rule: exactly; line-height: 20px; font-weight: 400;color: #302f35;">{value}</td>
                                    </tr>"""
    
    # Prepara template de email
    site_name = request.host or 'seu site'
    email_body = get_email_template().format(
        subject=subject,
        site_name=site_name,
        from_email=from_email,
        info_fields=info_fields,
        message=message
    )
    
    # Tenta enviar email (se configurado)
    try:
        if mail_config.get('use_smtp', False):
            send_email_smtp(mail_config, recipient_email, subject, email_body, from_email, from_name)
            print(f"✓ Email enviado para: {recipient_email}")
        else:
            # Modo desenvolvimento - apenas loga
            print(f"📧 Email seria enviado para: {recipient_email}")
            print(f"   Assunto: {subject}")
            print(f"   De: {from_name} <{from_email}>")
        
        return 'MF000'
    except Exception as e:
        print(f"✗ Erro ao enviar email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # SEMPRE retorna sucesso se chegou até aqui (mensagem foi salva no banco)
    return 'MF000'


def send_email_smtp(mail_config, recipient, subject, body, from_email, from_name):
    """Envia email via SMTP"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = recipient
    
    # Adiciona corpo HTML
    html_part = MIMEText(body, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Conecta e envia
    if mail_config.get('port') == 465:
        server = smtplib.SMTP_SSL(mail_config['host'], mail_config['port'])
    else:
        server = smtplib.SMTP(mail_config['host'], mail_config['port'])
        server.starttls()
    
    server.login(mail_config['username'], mail_config['password'])
    server.send_message(msg)
    server.quit()


def verify_recaptcha(recaptcha_response, remote_ip, secret_key):
    """
    Verifica reCaptcha
    Retorna código de status compatível com a API PHP original
    """
    if not secret_key or secret_key == '':
        return 'CPT001'
    
    if not recaptcha_response:
        return 'CPT002'
    
    # Verifica com Google
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': secret_key,
        'response': recaptcha_response,
        'remoteip': remote_ip
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get('success', False):
            return 'CPT000'
        else:
            return 'CPT002'
    except Exception as e:
        print(f"Erro ao verificar reCaptcha: {str(e)}")
        return 'CPT002'
