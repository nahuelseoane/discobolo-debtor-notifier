import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import whatsapp_notifier as notifier
from whatsapp_history import SendHistory


class NotifierTests(unittest.TestCase):
    def test_monthly_log_preserves_legacy_and_appends_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'log.xlsx'
            row = {'Name': 'Person', 'Phone': '00123', 'Amount': 12000,
                   'Status': 'Sent'}
            pd.DataFrame([row]).to_excel(path, index=False)
            notifier.save_monthly_log([row], '2026-09', path)
            notifier.save_monthly_log([row], '2026-09', path)
            notifier.save_monthly_log([row], '2026-10', path)
            notifier.save_monthly_log([row], '2027-09', path)
            sheets = pd.read_excel(path, sheet_name=None, dtype={'Phone': str})
            self.assertEqual(list(sheets), ['Sheet1', '2026-09', '2026-10', '2027-09'])
            self.assertEqual([len(sheet) for sheet in sheets.values()], [1, 2, 1, 1])
            self.assertEqual(sheets['2026-09']['Phone'].tolist(), ['00123', '00123'])
            self.assertEqual(sheets['Sheet1'].iloc[0].to_dict(), row)

    def test_rerun_and_duplicate_rows_send_only_once(self):
        row = {'CLIENTE': 'Person', 'First Name': 'Person', 'SALDO': 12000,
               'Celular': '+54 123', 'WhatsApp Name': 'Person'}
        with tempfile.TemporaryDirectory() as directory:
            history = SendHistory(Path(directory) / 'history.sqlite3')
            driver = MagicMock()
            driver.find_element.side_effect = notifier.NoSuchElementException()
            with patch.object(notifier, 'get_debtor_data', return_value=pd.DataFrame([row, row])), \
                 patch.object(notifier, 'get_driver', return_value=driver), \
                 patch.object(notifier.time, 'sleep'), \
                 patch.object(notifier, 'send_message', return_value=True) as send, \
                 patch.object(notifier, 'save_monthly_log'), \
                 patch('builtins.print'):
                notifier._send_whatsapp_reminders(history)
                history.close()
                history = SendHistory(Path(directory) / 'history.sqlite3')
                notifier._send_whatsapp_reminders(history)
                self.assertEqual(send.call_count, 1)
            history.close()
