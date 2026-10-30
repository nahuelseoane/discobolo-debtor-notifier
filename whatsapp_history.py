"""Persistent monthly claims for WhatsApp reminders."""
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
HISTORY_PATH = BASE_DIR / 'whatsapp_history.sqlite3'
LEGACY_PATH = BASE_DIR / 'whatsapp_sent_log.xlsx'


def normalize_phone(value):
    if pd.isna(value):
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return ''.join(ch for ch in str(value) if ch.isdigit())


class SendHistory:
    def __init__(self, path=HISTORY_PATH):
        # The WhatsApp client runs the send loop in its own thread; only one
        # thread uses the connection at a time, so sharing it is safe.
        self.connection = sqlite3.connect(path, check_same_thread=False)
        with self.connection:
            self.connection.execute('''CREATE TABLE IF NOT EXISTS sends (
                phone TEXT NOT NULL, month TEXT NOT NULL, name TEXT,
                status TEXT NOT NULL, updated_at TEXT NOT NULL,
                PRIMARY KEY (phone, month)
            )''')
            self.connection.execute('CREATE TABLE IF NOT EXISTS migrations (name TEXT PRIMARY KEY)')

    def import_legacy(self, path=LEGACY_PATH, month=None):
        if self.connection.execute("SELECT 1 FROM migrations WHERE name = 'excel'").fetchone():
            return
        if path.exists():
            log = pd.read_excel(path, dtype={'Phone': str})
            successful = log[log['Status'] == 'Sent']
            if not successful.empty and month is None:
                raise ValueError('Existing Excel sends have no dates. Run once with '
                                 '--legacy-month YYYY-MM or --legacy-month ignore.')
            with self.connection:
                if month != 'ignore':
                    for _, row in successful.iterrows():
                        phone = normalize_phone(row['Phone'])
                        if phone:
                            self.connection.execute(
                                'INSERT OR IGNORE INTO sends VALUES (?, ?, ?, ?, ?)',
                                (phone, month, row['Name'], 'Sent', datetime.now().isoformat()))
                self.connection.execute("INSERT INTO migrations VALUES ('excel')")
        else:
            with self.connection:
                self.connection.execute("INSERT INTO migrations VALUES ('excel')")

    def claim(self, phone, name, month):
        """Commit before sending; pending claims also block automatic retries."""
        with self.connection:
            cursor = self.connection.execute(
                'INSERT OR IGNORE INTO sends VALUES (?, ?, ?, ?, ?)',
                (phone, month, name, 'Pending', datetime.now().isoformat()))
            return cursor.rowcount == 1

    def finish(self, phone, month, sent):
        with self.connection:
            self.connection.execute(
                'UPDATE sends SET status = ?, updated_at = ? WHERE phone = ? AND month = ?',
                ('Sent' if sent else 'Needs review', datetime.now().isoformat(), phone, month))

    def close(self):
        self.connection.close()
