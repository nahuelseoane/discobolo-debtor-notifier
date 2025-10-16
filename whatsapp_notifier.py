import random
import time
import pyperclip
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_handler import get_debtor_data

def get_driver():
    options = webdriver.ChromeOptions()

    # 👇 choose a permanent folder to save your WhatsApp login
    options.add_argument("--user-data-dir=/home/jotaene/.config/google-chrome/whatsapp-profile")
    options.add_argument("--profile-directory=Default")
    # options.add_argument("--headless=new")

    # Optional: keep browser open after script ends
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    return driver

def send_whatsapp_reminders():
    merged_df = get_debtor_data()
    driver = get_driver()
    driver.get("https://web.whatsapp.com")

    try:
        driver.find_element("css selector", "canvas[aria-label='Scan me!']")
        input("📲 Scan the QR code and press Enter to continue...")
    except NoSuchElementException:
        # already logged in
        print("✅ WhatsApp already logged in, skipping QR step.")
        time.sleep(20)

    for _, row in merged_df.iterrows():
        try:
            name = row["CLIENTE"]
            first_name = row["First Name"]
            amount = row["SALDO"]
            raw_phone = row.get("Celular", "")
            if pd.isna(raw_phone):
                phone = ""
            else:
                phone = str(raw_phone.strip().replace(" ", ""))
            print(phone)
            if not phone or phone == "nan":
                print(f" Skipping {name} - no valid phone number.")
                continue

            with open("content_whatsapp.txt", "r", encoding="utf-8") as f:
                message_template = f.read()

            message = message_template.format(first_name=first_name, amount=amount)
            send_message(driver, name, phone, message)
            time.sleep(3 + random.random() * 2)
        except Exception as e:
            print(f"❌ Failed to send to {name} ({phone}): {e}")


    driver.quit()
    print("👋 WhatsApp automation finished, browser closed.")
    
def send_message(driver, name, phone, message):
    search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
    search_box.clear()
    search_box.send_keys(phone)
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    msg_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )

    pyperclip.copy(message)
    msg_box.send_keys(Keys.CONTROL, 'v')
    msg_box.send_keys(Keys.ENTER)
    print(f"✅ Whatsapp sent to {name} ({phone})")


if '__main__' == __name__:
    send_whatsapp_reminders()
    