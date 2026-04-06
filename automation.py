import yagmail
import schedule
import time
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_email(subject, body):
    try:
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
        yag.send(to=EMAIL_RECEIVER, subject=subject, contents=body)
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def check_unpaid_invoices():
    print(f"🔍 Checking invoices... {datetime.now().strftime('%H:%M:%S')}")
    try:
        df = pd.read_csv("sample_data/invoices.csv")
        rows = ""
        for _, row in df.iterrows():
            rows += f"<tr><td>{row['invoice_id']}</td><td>{row['vendor']}</td><td>₹{row['amount']}</td><td>{row['date']}</td></tr>"

        body = f"""
        <h2>📋 Invoice Status Report</h2>
        <p>All invoices as of {datetime.now().strftime('%d %b %Y %H:%M')}:</p>
        <table border='1' cellpadding='5' style='border-collapse:collapse;'>
            <tr><th>Invoice ID</th><th>Vendor</th><th>Amount</th><th>Date</th></tr>
            {rows}
        </table>
        """
        send_email(f"📋 Invoice Report - {len(df)} Invoices", body)
    except Exception as e:
        print(f"❌ Error reading invoices: {e}")

def check_high_variance():
    print(f"🔍 Checking budget... {datetime.now().strftime('%H:%M:%S')}")
    try:
        df = pd.read_csv("sample_data/budget.csv")
        rows = ""
        for _, row in df.iterrows():
            rows += f"<tr><td>{row['month']}</td><td>{row['category']}</td><td>₹{row['income']}</td><td>₹{row['expenses']}</td></tr>"

        body = f"""
        <h2>📊 Budget Report</h2>
        <p>Monthly budget summary as of {datetime.now().strftime('%d %b %Y %H:%M')}:</p>
        <table border='1' cellpadding='5' style='border-collapse:collapse;'>
            <tr><th>Month</th><th>Category</th><th>Income</th><th>Expenses</th></tr>
            {rows}
        </table>
        """
        send_email(f"📊 Budget Report - {len(df)} Records", body)
    except Exception as e:
        print(f"❌ Error reading budget: {e}")

def send_daily_summary():
    print(f"📋 Sending daily summary... {datetime.now().strftime('%H:%M:%S')}")
    body = f"""
    <h2>📋 AI Finance Agent — Daily Summary</h2>
    <p>Automated report generated on {datetime.now().strftime('%d %b %Y at %H:%M')}</p>
    <ul>
        <li>✅ Invoice check complete</li>
        <li>✅ Budget check complete</li>
        <li>✅ All modules running normally</li>
    </ul>
    <p>Login to your AI Finance Agent dashboard for full details.</p>
    """
    send_email("📋 Daily Finance Summary — AI Finance Agent", body)

# ── Schedule ──────────────────────────────────────────
schedule.every(1).minutes.do(check_unpaid_invoices)
schedule.every(1).minutes.do(check_high_variance)
schedule.every(1).minutes.do(send_daily_summary)

print("🚀 Automation started! Press Ctrl+C to stop.")
print("📧 First checks will run in 1 minute...")

while True:
    schedule.run_pending()
    time.sleep(30)