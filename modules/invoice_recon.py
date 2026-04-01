import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def reconcile_invoices(invoice_file, payment_file):
    invoices = pd.read_csv(invoice_file)
    payments = pd.read_csv(payment_file)

    merged = invoices.merge(payments, on="invoice_id", how="left", indicator=True)
    unmatched = merged[merged["_merge"] == "left_only"]
    matched = merged[merged["_merge"] == "both"]

    total_invoiced = invoices["amount"].sum()
    total_paid = matched["paid_amount"].sum() if len(matched) > 0 else 0
    total_unpaid = total_invoiced - total_paid

    summary = f"""
    Total invoices: {len(invoices)}
    Total matched/paid: {len(matched)}
    Total unmatched/unpaid: {len(unmatched)}
    Total invoiced amount: Rs.{total_invoiced:,}
    Total paid amount: Rs.{total_paid:,}
    Total outstanding: Rs.{total_unpaid:,}
    Unpaid vendors: {unmatched['vendor'].tolist()}
    Unpaid invoice IDs: {unmatched['invoice_id'].tolist()}
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"""
    You are a finance operations analyst.
    Analyze this invoice reconciliation summary and provide:
    1. Key findings
    2. Which vendors need immediate follow-up
    3. Recommended next actions
    Data: {summary}
    """)

    return response.text, unmatched, matched

result, unpaid, paid = reconcile_invoices(
    "sample_data/invoices.csv",
    "sample_data/payments.csv"
)
print(result)
print("\n--- UNPAID INVOICES ---")
print(unpaid[['invoice_id','vendor','amount']])