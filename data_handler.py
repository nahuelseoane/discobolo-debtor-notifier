from datetime import datetime
import pandas as pd
from config import DB_FILE, DEBTOR_FILE

MONTHS_ES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

def name_key(name):
    return " ".join(str(name).replace(",", " ").upper().split())


def get_debtor_data(sheet_name=None):
    if sheet_name is None:
        current_month_index = datetime.now().month - 1
        sheet_name = MONTHS_ES[current_month_index]

    df_debtors = pd.read_excel(DEBTOR_FILE, sheet_name=sheet_name, skiprows=1)
    df_db = pd.read_excel(DB_FILE, sheet_name="Socios")

    df_debtors = df_debtors[df_debtors["CLIENTE"].str.upper() != "TOTAL"]
    df_debtors = df_debtors.dropna(subset=["CLIENTE"])

    df_db = df_db.dropna(subset=["Nombre Completo"])
    df_db["First Name"] = df_db["Nombre Completo"]
    # "Perez, Juan" in socios.xlsx matches "PEREZ JUAN" in the debtor list.
    df_debtors["key"] = df_debtors["CLIENTE"].map(name_key)
    df_db["key"] = df_db["Nombre Completo"].map(name_key)
    # Same name twice (e.g. an ex-member): keep the active member's row.
    df_db = (df_db.assign(active=df_db["Estado"].eq("Socio"))
             .sort_values("active", ascending=False)
             .drop_duplicates("key")
             .drop(columns="active"))

    merged_df = pd.merge(df_debtors, df_db, on="key", how="left").drop(columns="key")
    merged_df["WhatsApp Name"] = merged_df["First Name"].apply(
        lambda n: " ".join([p.strip().title() for p in n.split(",")[::-1]]) if isinstance(n, str) and "," in n else str(n).title()
    )
    merged_df["First Name"] =  merged_df["First Name"].str.split(", ").str[1].str.split().str[0].str.lower().str.capitalize()
    merged_df = merged_df.drop(columns=["Nombre Completo", "DNI", "Jefe de Grupo I", "Tipo de Pago"])
    # print(merged_df.head())

    # 💵 Filter only real debtors
    merged_df = merged_df[merged_df["SALDO"] > 11000]

    return merged_df
