import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# Email donde enviar el mensaje
to_email = ""
subject = "Correo de prueba con Gmail SMTP"
body = "Este es un mensaje de prueba enviado desde Python usando Gmail."

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
    print("Correo enviado con éxito.")
except Exception as e:
    print("Error al enviar el correo:", e)
