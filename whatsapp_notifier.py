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

    options.add_argument("--user-data-dir=/home/jotaene/.config/google-chrome/whatsapp-profile")
    options.add_argument("--profile-directory=Default")
    # options.add_argument("--headless=new")

    # Optional: keep browser open after script ends
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    return driver

def get_driver_chrome_windows():
    from selenium.webdriver.chrome.options import Options
    import os
    options = Options()
    # Use Windows Chrome binary
    options.binary_location = r"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"

    # Persistent WhatsApp profile (Windows side)
    win_user = os.getenv("USERNAME") or "jnahu"
    profile_path = fr"C:\Users\{win_user}\AppData\Local\Google\Chrome\User Data\whatsapp-bot-profile"
    options.add_argument(fr"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    return driver

def send_whatsapp_reminders():
    merged_df = get_debtor_data()
    driver = get_driver_chrome_windows()
    driver.get("https://web.whatsapp.com")

    try:
        driver.find_element("css selector", "canvas[aria-label='Scan me!']")
        input("📲 Scan the QR code and press Enter to continue...")
    except NoSuchElementException:
        # already logged in
        print("✅ WhatsApp already logged in, skipping QR step.")
        time.sleep(20)
    
    sent_log = []
    for _, row in merged_df.iterrows():
        try:
            name = row["CLIENTE"]
            first_name = row["First Name"]
            amount = row["SALDO"]
            raw_phone = row.get("Celular", "")
            whatsapp_name = row["WhatsApp Name"]
            if pd.isna(raw_phone):
                phone = ""
            else:
                phone = str(raw_phone.strip().replace(" ", ""))

            if not phone or phone == "nan":
                print(f" Skipping {name} - no valid phone number.")
                continue

            with open("content_whatsapp.txt", "r", encoding="utf-8") as f:
                message_template = f.read()

            message = message_template.format(first_name=first_name, amount=amount)
            send_message(driver, whatsapp_name, phone, message)
            sent_log.append({
                "Name": name,
                "Phone": phone,
                "Amount": amount,
                "Status": "Sent"
            })
            time.sleep(3 + random.random() * 2)
        except Exception as e:
            print(f"❌ Failed running script -> {name} ({phone}): {e}")

    if sent_log:
        pd.DataFrame(sent_log).to_excel("whatsapp_sent_log.xlsx", index=False)
        print("💾 Log saved as whatsapp_sent_log.xlsx")
    driver.quit()
    print("👋 WhatsApp automation finished, browser closed.")
    
def send_message(driver, name, phone, message):
    try:
        search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
        search_box.clear()
        search_box.send_keys(name)
        time.sleep(3)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)

        # try clicking first result if exists
        try:
            first_result = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@role='gridcell' or starts-with(@class, '_ak73') or starts-with(@class, '_ak72')]"
                ))
            )
            first_result.click()
            print(f"💬 Chat found by name: {name}")

        except Exception:
            print(f"⚠️ Not chat found for '{name}' -- trying by phone: {phone}")
            time.sleep(2)
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
        print(f"✅ WhatsApp sent to {name} ({phone})")
    except Exception as e:
        print(f"❌ Failed to send to {name} ({phone}): {e}")


if '__main__' == __name__:
    send_whatsapp_reminders()
    