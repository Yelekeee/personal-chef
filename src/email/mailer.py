import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
APP_URL = os.getenv("APP_URL", "http://localhost:8501")


async def send_reset_email(to: str, token: str) -> None:
    reset_url = f"{APP_URL}?token={token}&view=reset_password"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Эмоционалды Интеллект — Құпиясөзді қалпына келтіру"
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    text_body = (
        f"Сәлем!\n\n"
        f"Құпиясөзді қалпына келтіру үшін төмендегі сілтемені басыңыз:\n{reset_url}\n\n"
        f"Сілтеме 1 сағат ішінде жарамды.\n\n"
        f"Егер сіз сұрамаған болсаңыз — бұл хатты елемеңіз.\n\nЭмоционалды Интеллект командасы"
    )
    html_body = f"""
    <html><body style="font-family:sans-serif;color:#1A1A2E;max-width:480px;margin:auto;">
      <div style="text-align:center;padding:2rem 0 1rem;">
        <span style="font-size:1.8rem;font-weight:700;color:#E8614F;">✦ Эмоционалды Интеллект</span>
      </div>
      <h2 style="font-size:1.3rem;font-weight:600;">Құпиясөзді қалпына келтіру</h2>
      <p>Аккаунтыңыздың құпиясөзін қалпына келтіру үшін төмендегі батырманы басыңыз:</p>
      <div style="text-align:center;margin:2rem 0;">
        <a href="{reset_url}"
           style="background:linear-gradient(135deg,#E8614F,#F4845F);color:white;
                  text-decoration:none;padding:0.75rem 2rem;border-radius:9999px;
                  font-weight:600;display:inline-block;">
          Құпиясөзді қалпына келтіру
        </a>
      </div>
      <p style="color:#6B7280;font-size:0.85rem;">
        Сілтеме 1 сағат ішінде жарамды.<br>
        Егер сіз сұрамаған болсаңыз — бұл хатты елемеңіз.
      </p>
    </body></html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
