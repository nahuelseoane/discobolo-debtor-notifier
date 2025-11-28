import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_CLUB, SMTP_PORT, SMTP_SERVER, EMAIL_USER, EMAIL_PASSWORD
from content import content_email
from data_handler import get_debtor_data

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip()

    # skip pandas NaN/None/"nan"
    if email.lower() == "nan":
        return False

    # very simple validity check
    return "@" in email and "." in email

def send_email_notifier():
    merged_df = get_debtor_data()

    for _, row in merged_df.iterrows():
        name, amount, email, first_name= row["CLIENTE"], row["SALDO"], str(row["Emails"]).strip().replace(";",","), row["First Name"]

        print("🔃", name, amount, email)

        # Split multiple emails if they come comma-separated
        email_list = [e.strip() for e in email.split(",") if is_valid_email(e)]

        if not email_list:
            print(f"⚠️ Not valird email for {name}. Skipping...")
            continue

        # Joining valid emails
        recipient_emails = ", ".join(email_list)

        msg = MIMEMultipart('related')
        msg['From'], msg['To'], msg['Subject'] = EMAIL_CLUB, recipient_emails, 'Recordatorio de saldo pendiente'

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

        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
    
            print(f"✅ Email sent to debtor {first_name} - {recipient_emails}: ${amount}")
        except Exception as e"
            print(f"❌ Error sending email to {name}: {e}")
            continue
        
            
if '__main__' == __name__:
    send_email_notifier()
    