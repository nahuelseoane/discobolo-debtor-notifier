"""Monthly WhatsApp reminders through the club's linked device (discobolo-messaging).

Replaces Chrome + WhatsApp Web (whatsapp_notifier.py): no browser, no QR every
time, and it sends by phone number instead of searching contact names.
The duplicate guard (whatsapp_history.sqlite3) and the Excel log stay the same.

Setup, once: python -m pip install -e "../discobolo-messaging[whatsapp]"
"""

import logging
import random
import time
from datetime import datetime
from pathlib import Path

from data_handler import get_debtor_data
from whatsapp_history import SendHistory, normalize_phone
from whatsapp_notifier import save_monthly_log

TEMPLATE = Path(__file__).with_name("content_whatsapp.txt")
PAUSE_SECONDS = (3, 5)  # Between messages, so it doesn't look like bulk sending.


def whatsapp_number(digits: str) -> str | None:
    """The number WhatsApp needs (549 + area + number), or None if unsure.

    '5491112345678' stays; '1112345678' (Buenos Aires mobile written without
    the country code) becomes '5491112345678'. The old '15' mobile prefix
    written instead of the area code ('5491512345678', '1512345678') becomes
    Buenos Aires '5491112345678': WhatsApp can't send to the '15' form, and
    lookups showed both forms are the same account. Anything else is not guessed.
    """
    if len(digits) == 13 and digits.startswith("54915"):
        return "54911" + digits[5:]
    if len(digits) == 13 and digits.startswith("549"):
        return digits
    if len(digits) == 10 and digits.startswith("15"):
        return "54911" + digits[2:]
    if len(digits) == 10 and digits.startswith("11"):
        return "549" + digits
    return None


def send_whatsapp_reminders(legacy_month=None, client=None):
    history = SendHistory()
    try:
        history.import_legacy(month=legacy_month)
        _send_whatsapp_reminders(history, client)
    finally:
        history.close()


def _send_whatsapp_reminders(history, client=None):
    if client is None:
        from discobolo_messaging.whatsapp import WhatsAppClient

        client = WhatsAppClient()
    debtors = get_debtor_data()
    template = TEMPLATE.read_text(encoding="utf-8")
    month = datetime.now().strftime("%Y-%m")
    log = []

    def work(wa):
        for _, row in debtors.iterrows():
            name, amount = row["CLIENTE"], row["SALDO"]
            phone = normalize_phone(row.get("Celular", ""))  # History key, as before.
            number = whatsapp_number(phone)
            if not number:
                status = "Skipped - missing phone" if not phone else "Skipped - invalid phone"
                print(f"⚠️ {name}: {status}")
                log.append({"Name": name, "Phone": phone, "Amount": amount, "Status": status})
                continue
            if not history.claim(phone, name, month):
                print(f"⏭️ Skipping {name}: already sent or awaiting review for {month}")
                continue
            message = template.format(first_name=row["First Name"], amount=amount)
            try:
                wa.send_to_phone(number, message)
                sent = True
                print(f"✅ WhatsApp sent to {name} (+{number})")
            except Exception as error:
                sent = False
                print(f"❌ Failed to send to {name} (+{number}): {error}")
            history.finish(phone, month, sent)
            log.append({"Name": name, "Phone": phone, "Amount": amount,
                        "Status": "Sent" if sent else "Not sent"})
            time.sleep(random.uniform(*PAUSE_SECONDS))

    try:
        client.run(work)
    finally:
        # Save what was done even if the connection failed halfway.
        if log:
            save_monthly_log(log, month)
            print(f"💾 Log saved, tab {month}")


if __name__ == "__main__":
    import argparse

    # whatsmeow floods the terminal with harmless warnings; keep errors only.
    for logger in ("whatsmeow", "Whatsmeow"):
        logging.getLogger(logger).setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-month", help="Month for undated Excel sends: YYYY-MM, or ignore")
    args = parser.parse_args()
    send_whatsapp_reminders(legacy_month=None if args.legacy_month == "ignore" else args.legacy_month)
