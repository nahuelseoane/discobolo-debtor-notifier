import tempfile
import unittest
from pathlib import Path

import pandas as pd
from whatsapp_history import SendHistory, normalize_phone


class HistoryTests(unittest.TestCase):
    def test_persistence_month_and_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.sqlite3'
            first = SendHistory(path)
            self.assertTrue(first.claim('549123', 'Person', '2026-09'))
            first.close()
            second = SendHistory(path)
            self.assertFalse(second.claim('549123', 'Changed name', '2026-09'))
            second.finish('549123', '2026-09', True)
            self.assertFalse(second.claim('549123', 'Person', '2026-09'))
            self.assertTrue(second.claim('549123', 'Person', '2026-10'))
            second.finish('549123', '2026-10', False)
            self.assertFalse(second.claim('549123', 'Person', '2026-10'))
            second.close()

    def test_usable_from_another_thread(self):
        # The WhatsApp client runs the send loop in a worker thread.
        import threading
        with tempfile.TemporaryDirectory() as directory:
            history = SendHistory(Path(directory) / 'history.sqlite3')
            results = []
            def work():
                results.append(history.claim('549123', 'Person', '2026-10'))
                history.finish('549123', '2026-10', True)
            thread = threading.Thread(target=work)
            thread.start()
            thread.join()
            self.assertEqual(results, [True])
            self.assertFalse(history.claim('549123', 'Person', '2026-10'))
            history.close()

    def test_two_connections_cannot_claim_same_recipient(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.sqlite3'
            first, second = SendHistory(path), SendHistory(path)
            self.assertTrue(first.claim('123', 'Person', '2026-09'))
            self.assertFalse(second.claim('123', 'Person', '2026-09'))
            first.close()
            second.close()

    def test_legacy_requires_month_and_imports_successes_only_once(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            log = path / 'legacy.xlsx'
            pd.DataFrame([
                {'Name': 'A', 'Phone': '+54 123', 'Status': 'Sent'},
                {'Name': 'B', 'Phone': '456', 'Status': 'Not sent'},
            ]).to_excel(log, index=False)
            history = SendHistory(path / 'history.sqlite3')
            with self.assertRaises(ValueError):
                history.import_legacy(log)
            history.import_legacy(log, '2026-09')
            history.import_legacy(log, '2026-10')
            self.assertFalse(history.claim('54123', 'A', '2026-09'))
            self.assertTrue(history.claim('456', 'B', '2026-09'))
            self.assertTrue(history.claim('54123', 'A', '2026-10'))
            history.close()

    def test_phone_normalization(self):
        self.assertEqual(normalize_phone(549123.0), '549123')
        self.assertEqual(normalize_phone('+54 9-123'), '549123')
        self.assertEqual(normalize_phone(float('nan')), '')


if __name__ == '__main__':
    unittest.main()
