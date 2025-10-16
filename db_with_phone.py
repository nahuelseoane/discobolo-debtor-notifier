import os
import pandas as pd
from config import DB_FILE, DB_FILE_2, DB_BASE

def clean_phone(phone):
    if pd.isna(phone):
        return None

    # Convert to string and remove common symbols
    phone = (
        str(phone)
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # Ensure it starts with +54
    if not phone.startswith("+54"):
        phone = "+54" + phone.lstrip("0")  # strip leading 0s if any

    # Insert '9' after +54 only if it's not already there
    if phone.startswith("+54") and not phone.startswith("+549"):
        phone = "+549" + phone[3:]

    return phone

def get_db_with_phones(sheet_name="Octubre"):
    df_1 = pd.read_excel(DB_FILE, sheet_name=sheet_name)
    df_2 = pd.read_excel(DB_FILE_2)

    df_2["Nombre Completo"] = (
        df_2["APELLIDO/RAZON"].astype(str).str.strip()
        + ", "
        + df_2["NOMBRE"].astype(str).str.strip()
    )

    df_1 = df_1.drop_duplicates(subset=["Nombre Completo"], keep="first")
    df_2 = df_2.drop_duplicates(subset=["Nombre Completo"], keep="first")


    merged_df = pd.merge(
        df_1,
        df_2[["Nombre Completo", "CELULAR"]],
        on="Nombre Completo",
        how="left"
    )

    # merged_df = merged_df.drop(columns=["Unnamed: 5"])
    merged_df["CELULAR"] = merged_df["CELULAR"].apply(clean_phone)


    output_path = os.path.join(DB_BASE, "db_socios.xlsx")
    merged_df.to_excel(output_path, index=False)
    print(f"💾 Merged file saved successfully: {output_path}")

    return merged_df

if '__main__' == __name__:
    get_db_with_phones()