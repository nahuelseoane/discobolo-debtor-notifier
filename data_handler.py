import pandas as pd
from config import DB_FILE, DEBTOR_FILE

def get_debtor_data(sheet_name="Octubre"):
    df_debtors = pd.read_excel(DEBTOR_FILE, sheet_name=sheet_name, skiprows=1)
    df_db = pd.read_excel(DB_FILE, sheet_name=sheet_name)

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
    merged_df["WhatsApp Name"] = merged_df["First Name"].apply(
        lambda n: " ".join([p.strip().title() for p in n.split(",")[::-1]]) if isinstance(n, str) and "," in n else str(n).title()
    )
    merged_df["First Name"] =  merged_df["First Name"].str.split(", ").str[1].str.split().str[0].str.lower().str.capitalize()
    merged_df = merged_df.drop(columns=["Nombre Completo", "DNI", "Jefe de Grupo I", "Tipo de Pago"])
    print(merged_df.head())

    # 💵 Filter only real debtors
    merged_df = merged_df[merged_df["SALDO"] > 10000]

    return merged_df
