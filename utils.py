from flask_mail import Message
from flask import url_for, current_app
from extensions import mail
from werkzeug.security import generate_password_hash
from extensions import db
import secrets

# EMAIL CADASTRO BOAS VINDAS

def enviar_email_boas_vindas(user, senha_temporaria):
    token = user.get_reset_token()
    
    msg = Message(
        subject='Bem-vindo ao Sentinel360',
        sender=current_app.config.get('MAIL_USERNAME', 'sentinel3601@gmail.com'),
        recipients=[user.email]
    )

    msg.body = f'''
Olá {user.nome},

Sua conta no Sentinel360 foi criada com sucesso!

📧 E-mail: {user.email}
🔑 Senha Temporária: {senha_temporaria}

Por favor, redefina sua senha imediatamente usando o link abaixo:
{url_for('reset_token', token=token, _external=True)}

Se você não reconhece este cadastro, ignore este e-mail ou entre em contato conosco.

Atenciosamente,  
Equipe Sentinel360
'''

    mail.send(msg)


# EMAIL ESQUECI A SENHA
def enviar_email_recuperacao(user, senha_temporaria): # <-- AQUI: Certifique-se de que 'senha_temporaria' está como um argumento
    token = user.get_reset_token()

    msg = Message(
        subject='Redefinição de Senha - Sentinel360',
        sender=current_app.config.get('MAIL_USERNAME', 'sentinel3601@gmail.com'),
        recipients=[user.email]
    )

    msg.body = f'''
Olá {user.nome},

Recebemos uma solicitação para redefinir sua senha no Sentinel360.

🔑 Sua nova senha temporária é:
{senha_temporaria}

Para redefinir sua senha, clique no link abaixo:
{url_for('reset_token', token=token, _external=True)}

⚠️ Por motivos de segurança, essa senha é válida por tempo limitado.

Se você não solicitou essa alteração, apenas ignore este e-mail.

Atenciosamente,  
Equipe Sentinel360
'''
# DEBUG: Mostrar conteúdo que será enviado no terminal
    print("=" * 50)
    print("DEBUG - Conteúdo do e-mail que será enviado:")
    print(msg.body)
    print("=" * 50)

    mail.send(msg)

