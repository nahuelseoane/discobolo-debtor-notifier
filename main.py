# src/main.py
import typer
from email_notifier import send_email_notifier as send_email_reminders
from whatsapp_notifier import send_whatsapp_reminders

app = typer.Typer()

@app.command()
def run(method: str = typer.Option("email", help="Choose 'email' or 'whatsapp'")):
    if method == "email":
        send_email_reminders()
    elif method == "whatsapp":
        send_whatsapp_reminders()
    else:
        typer.echo("❌ Invalid method. Use 'email' or 'whatsapp'.")

if __name__ == "__main__":
    app()
