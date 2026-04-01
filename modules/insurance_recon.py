import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def reconcile_insurance(claims_file, settlements_file):
    claims = pd.read_csv(claims_file)
    settlements = pd.read_csv(settlements_file)

    merged = claims.merge(settlements, on="claim_id", how="left")
    merged["variance"] = merged["amount_claimed"] - merged["amount_settled"].fillna(0)
    merged["status"] = merged["status"].fillna("pending")

    pending = merged[merged["status"] == "pending"]
    settled = merged[merged["status"] == "settled"]
    high_variance = merged[merged["variance"] > 5000]

    total_claimed = claims["amount_claimed"].sum()
    total_settled = settlements["amount_settled"].sum()
    total_variance = merged["variance"].sum()

    summary = f"""
    Total claims submitted: {len(claims)}
    Claims settled: {len(settled)}
    Claims pending: {len(pending)}
    Total amount claimed: Rs.{total_claimed:,}
    Total amount settled: Rs.{total_settled:,}
    Total variance (underpaid/pending): Rs.{total_variance:,}
    High variance cases (gap > Rs.5000): {len(high_variance)}
    Pending claim IDs: {pending['claim_id'].tolist()}
    Pending insurers: {pending['insurer'].tolist()}
    High variance details:
    {high_variance[['claim_id','patient','amount_claimed','amount_settled','variance','insurer']].to_string()}
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"""
    You are an insurance reconciliation specialist.
    Review this claims data and provide:
    1. Summary of settlement status
    2. High risk cases that need immediate escalation
    3. Which insurers are underperforming
    4. Recommended follow-up actions
    Data: {summary}
    """)

    return response.text, pending, high_variance

result, pending, high_var = reconcile_insurance(
    "sample_data/claims.csv",
    "sample_data/settlements.csv"
)

print(result)
print("\n--- PENDING CLAIMS ---")
print(pending[['claim_id', 'patient', 'amount_claimed', 'insurer']])
print("\n--- HIGH VARIANCE CASES ---")
print(high_var[['claim_id', 'patient', 'amount_claimed', 'amount_settled', 'variance']])