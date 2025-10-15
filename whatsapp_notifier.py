import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from data_handler import get_debtor_data

def send_whatsapp_reminders():
    merged_df = get_debtor_data()
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com")

    input("📲 Scan the QR code and press Enter to continue...")

    for _, row in merged_df.iterrows():
        name = row["CLIENTE"]
        first_name = row["First Name"]
        amount = row["SALDO"]
        phone = str(row.get("Phone", "")strip().replace(" ", ""))

        if not phone or phone == "nan":
            print(f" Skipping {name} - no valid phone number.")
            continue

        message = (
            f"Hola {first_name}, te recordamos que tenés un saldo pendiente de ${amount}."
            "Por favor, comuniquese con administración si ya realizó el pago. "
            "💚 Discóbolo"
        )
        
        send_message(driver, name, phone, message)
        time.sleep(2)
    
def send_message(driver, name, phone, message):
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.clear()
    search_box.send_keys(phone)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(1)

    msg_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
    msg_box.send_keys(message)
    msg_box.send_keys(Keys.ENTER)
    print(f"✅ Whatsapp sent to {name} ({phone})")