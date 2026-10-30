import random
from datetime import datetime
from whatsapp_history import LEGACY_PATH, SendHistory, normalize_phone
from openpyxl import Workbook, load_workbook
import time
import pyperclip
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data_handler import get_debtor_data
from config import USERNAME_LINUX, USERNAME_WINDOWS

def get_driver():
    linux_user = USERNAME_LINUX
    options = webdriver.ChromeOptions()

    options.add_argument(f"--user-data-dir=/home/{linux_user}/.config/google-chrome/whatsapp-profile")
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
    win_user = USERNAME_WINDOWS
    profile_path = fr"C:\Users\{win_user}\AppData\Local\Google\Chrome\User Data\whatsapp-bot-profile"
    options.add_argument(fr"--user-data-dir={profile_path}")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    return driver


def clear_and_focus_search_box(driver):
    """Focuses the WhatsApp search box and clears any existing text."""
    wait = WebDriverWait(driver, 25)

    search_xpaths = [
        "//input[@role='textbox' and @aria-label='Buscar un chat o iniciar uno nuevo']",
        "//input[@placeholder='Buscar un chat o iniciar uno nuevo']",
        "//input[@role='textbox' and contains(@aria-label, 'Buscar')]",
        "//input[@type='text' and contains(@placeholder, 'Buscar')]",
        "//div[@id='side']//div[@contenteditable='true' and @role='textbox']",
    ]

    last_error = None

    for xpath in search_xpaths:
        try:
            search_box = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            search_box.click()
            time.sleep(0.3)

            search_box.send_keys(Keys.CONTROL, "a")
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)

            return search_box

        except Exception as e:
            last_error = e

    raise TimeoutException(f"Could not find WhatsApp search box. Last error: {last_error}")


def get_message_box(driver):
    """Returns the WhatsApp message input box."""
    wait = WebDriverWait(driver, 20)

    message_xpaths = [
        "//footer//div[@contenteditable='true' and @role='textbox']",
        "//footer//div[@contenteditable='true']",
    ]

    last_error = None

    for xpath in message_xpaths:
        try:
            return wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except Exception as e:
            last_error = e

    raise TimeoutException(f"Could not find WhatsApp message box. Last error: {last_error}")


def verify_chat_opened(driver, expected_name, phone, searched_by_phone=False):
    """
    Unified chat verification:
    - Retrieves the real chat title using debug_chat_title()
    - Compares it with the expected name
    - If searching by phone, name mismatch does NOT matter
    """
    chat_title = debug_chat_title(driver)

    # If searching by phone, only phone matching matters
    if searched_by_phone:
        # Always accept phone-based chat opening for verification 
        # (message sending can still be restricted)
        return True

    # Normalize
    expected = expected_name.lower().strip()
    title = chat_title.lower().strip()

    # Partial name match
    if expected in title:
        print(f"✅ Chat verified by exact name: {chat_title}")
        return True

    # Word-by-word partial match
    for part in expected.split():
        if len(part) > 2 and part in title:
            print(f"✅ Chat verified by partial name: {chat_title}")
            return True

    print(f"🚫 Chat mismatch — Expected {expected_name} but got: '{chat_title}'")
    return False


def debug_chat_title(driver):
    """
    Captures the real WhatsApp chat title.
    Works with the new obfuscated class WhatsApp UI.
    """

    for attempt in range(12):  # ~12 seconds of retries
        
        try:
            # ALL spans inside header with dir="auto"
            spans = driver.find_elements(
                By.XPATH,
                "//header//span[@dir='auto']"
            )

            for sp in spans:
                title = sp.text.strip()

                # skip empty
                if not title:
                    continue

                # skip placeholder numbers (badge unread counter)
                if title.isdigit():
                    continue

                # skip too-short placeholders ("1", "15")
                if len(title) <= 2:
                    continue

                # THIS is the real name
                return title

        except:
            pass

        # wait and try again
        time.sleep(1)

    return "<no real title loaded>"

def try_open_chat_by_phone(driver, phone):
    """
    Returns:
        new_title: str
        changed: bool  → True if WhatsApp opened a NEW chat
    """

    # 1. Read OLD chat title BEFORE doing anything else
    old_title = debug_chat_title(driver)

    # 2. Move to search bar
    search_box = clear_and_focus_search_box(driver)

    # Small pause to avoid race condition
    time.sleep(0.3)

    # 3. Search by phone
    search_box.send_keys(phone)
    time.sleep(0.5)
    search_box.send_keys(Keys.ENTER)

    # 4. Wait for UI to finish switching
    time.sleep(1.5)

    # 5. Read NEW chat title
    new_title = debug_chat_title(driver)

    # 6. Determine if chat changed
    changed = (new_title != old_title)

    return new_title, changed


def send_message(driver, name, phone, message):
    try:
        search_box = clear_and_focus_search_box(driver)
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
            time.sleep(1.5)

            if not verify_chat_opened(driver, name, phone, searched_by_phone=False):
                return False
            print(f"💬 Chat found by name: {name}")

        except Exception:
            print(f"⚠️ Not chat found for '{name}' -- trying by phone: {phone}")
            time.sleep(2)
            # 2nd option - by phone
            if not phone or phone == "nan":
                print(f" Skipping {name} - no valid phone number.")
                return False
            search_box = clear_and_focus_search_box(driver)

            # Now type the phone number
            search_box.send_keys(phone)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            # Fallback verification only for debugging, no sending
            chat_title, opened_new = try_open_chat_by_phone(driver, phone)

            # If WhatsApp did NOT open a new chat → number is invalid or not found
            if not opened_new:
                print(f"❌ No chat found for number '{phone}'. WhatsApp stayed on the previous chat.")
                print(f"   Previous chat title was: '{chat_title}'")
                return False   # <-- IMPORTANT

            # If WhatsApp DID open a chat → show the real title (debug only)
            print(f"⚠️ Fallback search by phone opened a chat titled: '{chat_title}'")
            print("   (Not sending message as a safety measure)")
            return False    

        msg_box = get_message_box(driver)

        pyperclip.copy(message)
        msg_box.send_keys(Keys.CONTROL, 'v')
        msg_box.send_keys(Keys.ENTER)

        print(f"✅ WhatsApp sent to {name} ({phone})")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send to {name} ({phone}): {type(e).__name__} - {repr(e)}")
        return False


def save_monthly_log(rows, month, path=LEGACY_PATH):
    """Append run results without overwriting earlier runs or months."""
    if not rows:
        return
    if path.exists():
        workbook = load_workbook(path)
    else:
        workbook = Workbook()
        workbook.remove(workbook.active)
    try:
        columns = ['Name', 'Phone', 'Amount', 'Status']
        if month in workbook.sheetnames:
            sheet = workbook[month]
        else:
            sheet = workbook.create_sheet(month)
            sheet.append(columns)
        for row in rows:
            sheet.append([row[column] for column in columns])
        workbook.save(path)
    finally:
        workbook.close()


def send_whatsapp_reminders(legacy_month=None):
    history = SendHistory()
    try:
        history.import_legacy(month=legacy_month)
        _send_whatsapp_reminders(history)
    finally:
        history.close()


def _send_whatsapp_reminders(history):
    merged_df = get_debtor_data()
    driver = get_driver()
    driver.get("https://web.whatsapp.com")
    time.sleep(10)
    try:
        driver.find_element("css selector", "canvas[aria-label='Scan me!']")
        input("📲 Scan the QR code and press Enter to continue...")
        time.sleep(60)
    except NoSuchElementException:
        # already logged in
        print("✅ WhatsApp already logged in, skipping QR step.")
        time.sleep(20)
    
    sent_log = []
    month = datetime.now().strftime("%Y-%m")
    for _, row in merged_df.iterrows():
        try:
            name = row["CLIENTE"]
            first_name = row["First Name"]
            amount = row["SALDO"]
            raw_phone = row.get("Celular", "")
            whatsapp_name = row["WhatsApp Name"]
            phone = normalize_phone(raw_phone)

            if not phone:
                print(f"⚠️ Skipping {name}: missing phone number")
                sent_log.append({
                    "Name": name,
                    "Phone": "",
                    "Amount": amount,
                    "Status": "Skipped - missing phone"
                })
                continue

            with open("content_whatsapp.txt", "r", encoding="utf-8") as f:
                message_template = f.read()

            message = message_template.format(first_name=first_name, amount=amount)
            if not history.claim(phone, name, month):
                print(f"⏭️ Skipping {name}: already sent or awaiting review for {month}")
                continue
            sent = send_message(driver, whatsapp_name, phone, message)
            history.finish(phone, month, sent)
            sent_log.append({
                "Name": name,
                "Phone": phone,
                "Amount": amount,
                "Status": "Sent" if sent else "Not sent"
            })
            time.sleep(3 + random.random() * 2)
        except Exception as e:
            print(f"❌ Failed running script -> {name} ({phone}): {e}")

    if sent_log:
        save_monthly_log(sent_log, month)
        print(f"💾 Log saved to {LEGACY_PATH}, tab {month}")
    driver.quit()
    print("👋 WhatsApp automation finished, browser closed.")
    

if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-month", help="Month for undated Excel sends: YYYY-MM, or ignore")
    args = parser.parse_args()
    if args.legacy_month and args.legacy_month != "ignore":
        try:
            parsed = datetime.strptime(args.legacy_month, "%Y-%m")
            if parsed.strftime("%Y-%m") != args.legacy_month:
                raise ValueError()
        except ValueError:
            parser.error("--legacy-month must be YYYY-MM or ignore")
    send_whatsapp_reminders(legacy_month=args.legacy_month)
    
