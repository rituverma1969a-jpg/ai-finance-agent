import google.generativeai as genai
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def build_credit_memo(client_name, client_address, original_invoice,
                      items, reason, authorized_by):

    items_text = "\n".join([f"- {item['description']}: Rs.{item['amount']:,}"
                            for item in items])
    total = sum(item['amount'] for item in items)
    memo_number = f"CM-{original_invoice}-{date.today().strftime('%Y%m%d')}"

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"""
    Generate a formal professional credit memo document with this information:

    CREDIT MEMO NUMBER: {memo_number}
    DATE: {date.today().strftime('%d %B %Y')}
    ORIGINAL INVOICE: {original_invoice}

    ISSUED TO:
    {client_name}
    {client_address}

    CREDIT ITEMS:
    {items_text}

    TOTAL CREDIT AMOUNT: Rs.{total:,}

    REASON FOR CREDIT: {reason}
    AUTHORIZED BY: {authorized_by}

    Format this as a complete professional credit memo with:
    1. Header with company details and memo number
    2. Client details section
    3. Itemized credit table
    4. Total credit amount
    5. Reason for credit
    6. Payment adjustment instructions
    7. Authorized signature section
    Make it formal and ready to send to a client.
    """)

    memo = response.text
    filename = f"credit_memo_{memo_number}.txt"

    with open(filename, "w") as f:
        f.write(memo)

    return memo, filename, total

# Test it with sample data
items = [
    {"description": "Returned damaged goods - 10 units", "amount": 12000},
    {"description": "Overcharge correction on original invoice", "amount": 3000}
]

memo, filename, total = build_credit_memo(
    client_name="ABC Corporation Pvt Ltd",
    client_address="123 Business Park, Mumbai, Maharashtra - 400001",
    original_invoice="INV-2024-0042",
    items=items,
    reason="Customer returned damaged goods and billing correction required",
    authorized_by="Finance Manager"
)

print(memo)
print(f"\n✅ Credit memo saved as: {filename}")
print(f"✅ Total credit amount: Rs.{total:,}")