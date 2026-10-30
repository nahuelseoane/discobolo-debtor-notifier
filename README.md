# 🧾 Discóbolo Debtor Notifier

Automated system for generating and sending debtor notifications for **Club de Deportes Discóbolo**.  
Built with **Python**, this tool extracts, cleans, and formats monthly debtor data from Excel files, then sends personalized notifications (via WhatsApp, email, or PDF exports).

---

## 🚀 Features

- **Excel data parsing** using `pandas` and `openpyxl`
- **Automatic formatting and validation** of debtor lists
- **Customizable notification templates**
- **WhatsApp or email sending** integration
- **Logging & progress tracking**
- **Easy configuration** with `.env` environment variables

---

## 📷 Screenshot
![Screenshot of the script running](https://i.imgur.com/BtujamF.png)

---

## 🧠 Project Architecture

```
discobolo-debtor-notifier/
│
├── data/                     # Input Excel files (bank or debtor lists)
├── output/                   # Processed reports or notification exports
├── notifier/                 # Core modules
│   ├── data_loader.py        # Handles Excel reading & cleaning
│   ├── message_builder.py    # Formats debtor messages
│   ├── notifier.py           # Manages message sending
│   └── utils.py              # Logging & helper functions
│
├── .env.example              # Example environment config
├── requirements.txt
└── main.py                   # Entry point
```

---

## ⚙️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/nahuelscode/discobolo-debtor-notifier.git
cd discobolo-debtor-notifier
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuration

Create a `.env` file based on `.env.example` and update values:

```bash
WHATSAPP_SESSION_PATH=/path/to/session
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=app_password
DEBTOR_EXCEL_PATH=./data/debtors.xlsx
```

---

## ▶️ Usage

### Run the notifier
```bash
python main.py
```

### Command-line options (if you added Typer/CLI)
```bash
python main.py send --month October
python main.py generate-report
```

---

## 🧩 Example Workflow

1. Download latest debtor Excel file  
2. Place it in the `data/` directory  
3. Run the notifier script  
4. Review logs and generated Excel or PDF output  
5. Notifications are sent automatically via WhatsApp or email  

---

## 📊 Tech Stack

- **Python 3.10+**
- **pandas** / **openpyxl** — Excel parsing and formatting
- **Typer** — CLI management
- **dotenv** — environment variable handling
- **Selenium / pywhatkit / smtplib** — (optional) message sending

---

## 🧹 To-Do

- [ ] Add logging configuration file  
- [ ] Add tests for Excel parsing  
- [ ] Add PDF export for manual notifications  
- [ ] Improve CLI error handling  

---

## 👤 Author

**Juan Nahuel Seoane**  
📍 Buenos Aires, Argentina  
🌐 [jnahuel.com](https://jnahuel.com)  
💻 [github.com/nahuelscode](https://github.com/nahuelscode)  

---

## 🪪 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

### Monthly WhatsApp duplicate protection

`python whatsapp_notifier.py` keeps persistent history in
`whatsapp_history.sqlite3`, beside the script. A normalized phone number can be
claimed only once per local calendar month (including the year), even across
restarts or concurrent runs. Changing the reminder text or balance does not
allow another send that month. Keep this database when updating the script.
`whatsapp_sent_log.xlsx`, beside the script, keeps a separate tab for each
month (`YYYY-MM`). Runs append results to that month's tab, preserving earlier
runs and months. Existing undated tabs are preserved. The Excel file is a
report; the SQLite database remains the duplicate guard.

The old Excel report has no dates. On the first run, explicitly assign its
successful sends to their actual month, for example:

```bash
python whatsapp_notifier.py --legacy-month 2026-09
```

Use `--legacy-month ignore` only if those old sends should not suppress any
current reminders. Import happens once and only includes `Sent` entries.

A claim is saved before interacting with WhatsApp. Interrupted sends stay
`Pending`; unsuccessful attempts become `Needs review`. Both block automatic
retries that month because browser errors can leave delivery uncertain. Check
the chat before manually removing a corresponding database row to allow a retry.
`Sent` means the browser submitted the message, not confirmed delivery.
