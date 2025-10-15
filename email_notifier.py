import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_CLUB, SMTP_PORT, SMTP_SERVER, EMAIL_USER, EMAIL_PASSWORD
from content import content_email
from data_handler import get_debtor_data

def send_email_notifier():
    merged_df = get_debtor_data()

    for _, row in merged_df.iterrows():
        name, amount, email, first_name= row["CLIENTE"], row["SALDO"], str(row["Emails"]).strip().replace(";",","), row["First Name"]

        print("🔃", name, amount, email)

        msg = MIMEMultipart('related')
        msg['From'], msg['To'], msg['Subject'] = EMAIL_CLUB, email, 'Recordatorio de saldo pendiente'

        plain_content, html_content = content_email(first_name, amount)

        alt_part = MIMEMultipart('alternative')
        alt_part.attach(MIMEText(plain_content, 'plain')) # fallback 
        alt_part.attach(MIMEText(html_content, 'html'))
        msg.attach(alt_part)

        with open("logo.jpg", "rb") as img:
            logo = MIMEImage(img.read())
            logo.add_header("Content-ID", "<logo>")
            logo.add_header("Content-Disposition", "inline", filename="logo.png")
            msg.attach(logo)

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
    
        print(f"✅ Email sent to debtor {first_name} - {email}: ${amount}")
        
            
if '__main__' == __name__:
    send_email_notifier()
    