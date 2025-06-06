import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException, status
from app.core.config import settings
import logging


def send_email(to_email: str, subject: str, body: str):
    # Construir el mensaje
    msg = MIMEMultipart()
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Enviar el correo
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()  # Iniciar TLS
        server.login(settings.FROM_EMAIL, settings.APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logging.info(
            f"Correo enviado a {to_email} con éxito. Asunto: {subject}. Cuerpo: {body}"
        )
    except Exception as e:
        logging.error(f"Error al enviar el correo a {to_email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el correo",
        )
