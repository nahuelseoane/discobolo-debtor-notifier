import os

from dotenv import load_dotenv

load_dotenv()

EMAIL_CLUB = os.getenv("EMAIL_CLUB")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

BASE_PATH = os.getenv("BASE_PATH")
DEBTOR_FILE = os.path.join(BASE_PATH, "Morosos","Morosos 2025.xlsx")
DB_BASE = os.path.join(BASE_PATH, "Transferencias-bancarias", "2025")
DB_FILE = os.path.join(DB_BASE, "socios_database.xlsx")
DB_FILE_2 = os.path.join(DB_BASE, "db.xlsx")