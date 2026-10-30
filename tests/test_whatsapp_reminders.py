import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import whatsapp_reminders as reminders
from whatsapp_history import SendHistory


class FakeSession:
    def __init__(self, fail_for=()):
        self.sent = []
        self.fail_for = fail_for

    def send_to_phone(self, number, text):
        if number in self.fail_for:
            raise RuntimeError("not on WhatsApp")
        self.sent.append((number, text))


class FakeClient:
    def __init__(self, session):
        self.session = session

    def run(self, work):
        return work(self.session)


def row(name, phone, amount=12000):
    return {"CLIENTE": name, "First Name": name.split()[0], "SALDO": amount, "Celular": phone}


class WhatsAppNumberTest(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(reminders.whatsapp_number("5491112345678"), "5491112345678")
        self.assertEqual(reminders.whatsapp_number("1112345678"), "5491112345678")
        self.assertEqual(reminders.whatsapp_number("5491554174538"), "5491154174538")
        self.assertEqual(reminders.whatsapp_number("1554174538"), "5491154174538")
        for unsure in ("", "54911123456", "549111234567890", "2214567890"):
            self.assertIsNone(reminders.whatsapp_number(unsure))


class SendTest(unittest.TestCase):
    def run_once(self, rows, history, session):
        with patch.object(reminders, "get_debtor_data", return_value=pd.DataFrame(rows)), \
             patch.object(reminders.time, "sleep"), \
             patch.object(reminders, "save_monthly_log") as save, \
             patch("builtins.print"):
            reminders._send_whatsapp_reminders(history, FakeClient(session))
        return save

    def test_sends_once_per_month_even_across_runs(self):
        rows = [row("Ana Pérez", "+54 9 11 1234-5678"), row("Ana Pérez", "+54 9 11 1234-5678")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "history.sqlite3"
            session = FakeSession()
            history = SendHistory(path)
            self.run_once(rows, history, session)
            history.close()
            history = SendHistory(path)
            self.run_once(rows, history, session)
            history.close()
        self.assertEqual([n for n, _ in session.sent], ["5491112345678"])
        self.assertIn("Hola Ana", session.sent[0][1])
        self.assertIn("12000", session.sent[0][1])

    def test_format_change_between_runs_does_not_resend(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "history.sqlite3"
            session = FakeSession()
            history = SendHistory(path)
            # An earlier run that stored the number as written in the spreadsheet.
            history.claim("1112345678", "Ana Pérez", reminders.datetime.now().strftime("%Y-%m"))
            history.finish("1112345678", reminders.datetime.now().strftime("%Y-%m"), True)
            history.rekey(reminders.whatsapp_number)
            self.run_once([row("Ana Pérez", "+5491112345678")], history, session)
            self.run_once([row("Ana Pérez", "1512345678")], history, session)
            history.close()
        self.assertEqual(session.sent, [])

    def test_bad_numbers_are_logged_not_guessed(self):
        rows = [row("Sin Tel", ""), row("Raro Num", "54911123"), row("Falla Envio", "1199999999")]
        with tempfile.TemporaryDirectory() as folder:
            history = SendHistory(Path(folder) / "history.sqlite3")
            session = FakeSession(fail_for={"5491199999999"})
            save = self.run_once(rows, history, session)
            history.close()
        statuses = [entry["Status"] for entry in save.call_args[0][0]]
        self.assertEqual(statuses, ["Skipped - missing phone", "Skipped - invalid phone", "Not sent"])
        self.assertEqual(session.sent, [])


if __name__ == "__main__":
    unittest.main()
