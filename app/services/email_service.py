from flask_mail import Message, Mail
from flask import current_app

mail = Mail()

class EmailService:
    @staticmethod
    def send_email(subject, recipients, body, html=None):
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"SMTP not configured. Email to {recipients} skipped.")
            return False
            
        try:
            msg = Message(
                subject=subject,
                recipients=recipients,
                body=body,
                html=html,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def send_welcome_email(user_email, username):
        subject = f"Welcome to {current_app.config.get('COMPANY_NAME')}!"
        body = f"Hello {username},\n\nWelcome to Rephina Software ERP. Your account has been successfully created."
        return EmailService.send_email(subject, [user_email], body)
