import smtplib
from email.mime.text import MIMEText
from .settings import settings

def send_summary_email(to_email: str, subject: str, summary_body: str):
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        raise RuntimeError("SMTP credentials missing. Set SMTP_USER and SMTP_PASS.")

    msg = MIMEText(summary_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    if settings.SMTP_USE_TLS == "true":
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)

    try:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg)
    finally:
        server.quit()
