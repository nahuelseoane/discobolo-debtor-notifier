from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pandas as pd
from config import DB_FILE, DEBTOR_FILE, EMAIL_CLUB, SMTP_PORT, SMTP_SERVER, EMAIL_USER, EMAIL_PASSWORD
from content import content_email

def main():
    df_debtors = pd.read_excel(DEBTOR_FILE, sheet_name="Octubre", skiprows=1)
    df_db = pd.read_excel(DB_FILE, sheet_name="Octubre")

    df_debtors = df_debtors[df_debtors["CLIENTE"].str.upper() != "TOTAL"]
    df_debtors = df_debtors.dropna(subset=["CLIENTE"])

    df_db["First Name"] = df_db["Nombre Completo"]
    df_db["Nombre Completo"] = df_db["Nombre Completo"].str.replace(",", "")

    merged_df = pd.merge(
        df_debtors,
        df_db,
        left_on="CLIENTE",
        right_on="Nombre Completo",
        how="left"
    )
    merged_df["First Name"] =  merged_df["First Name"].str.split(", ").str[1].str.split().str[0].str.lower().str.capitalize()
    merged_df = merged_df.drop(columns=["Nombre Completo", "DNI", "Jefe de Grupo I", "Tipo de Pago", "Unnamed: 5"])


    for index, row in merged_df.iterrows():
        name, amount, email, first_name= row["CLIENTE"], row["SALDO"], str(row["Emails"]).strip().replace(";",","), row["First Name"]

        if amount > 10000: 
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
    main()
    