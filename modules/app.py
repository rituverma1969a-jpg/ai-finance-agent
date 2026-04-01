import streamlit as st
import pandas as pd
import google.generativeai as genai
import pdfplumber
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="AI Finance Agent",
    page_icon="📊",
    layout="wide"
)

st.sidebar.title("📊 AI Finance Agent")
st.sidebar.markdown("Built by **Ritu Verma**")
st.sidebar.markdown("*AI & Finance Professional*")
st.sidebar.markdown("---")

module = st.sidebar.radio("Select Module", [
    "🏠 Home",
    "🧾 Invoice Reconciliation",
    "🏥 Insurance Reconciliation",
    "📝 Credit Memo Builder",
    "📈 Budget Forecast",
    "📄 Annual Report Analyzer"
])

def get_model():
    return genai.GenerativeModel("gemini-2.5-flash-lite")

# ─── HOME ───────────────────────────────────────────
if module == "🏠 Home":
    st.title("Welcome to AI Finance Agent 🤖")
    st.markdown("""
    ### Your intelligent finance operations assistant
    Built with **Gemini AI + Python + Streamlit**

    ---

    | Module | What it does |
    |---|---|
    | 🧾 Invoice Reconciliation | Match invoices to payments, flag unpaid |
    | 🏥 Insurance Reconciliation | Compare claims vs settlements |
    | 📝 Credit Memo Builder | Auto-generate professional credit memos |
    | 📈 Budget Forecast | 3-6 month financial projections |
    | 📄 Annual Report Analyzer | PDF analysis + Q&A |

    ---
    ### Built by Ritu Verma — AI & Finance Professional
    Finance Operations | AI Model Evaluation | Agentic AI Development
    
    📧 rituverma1969a@gmail.com
    🔗 linkedin.com/in/ritu-verma-/

# ─── INVOICE RECONCILIATION ─────────────────────────
elif module == "🧾 Invoice Reconciliation":
    st.title("🧾 Invoice Reconciliation")
    st.markdown("Upload your invoice and payment files to find mismatches automatically.")

    col1, col2 = st.columns(2)
    with col1:
        inv_file = st.file_uploader("Upload Invoices CSV", type="csv")
    with col2:
        pay_file = st.file_uploader("Upload Payments CSV", type="csv")

    if inv_file and pay_file:
        invoices = pd.read_csv(inv_file)
        payments = pd.read_csv(pay_file)

        st.subheader("📋 Uploaded Data")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Invoices")
            st.dataframe(invoices)
        with col2:
            st.write("Payments")
            st.dataframe(payments)

        if st.button("Run Reconciliation", type="primary"):
            with st.spinner("Analyzing invoices..."):
                merged = invoices.merge(
                    payments, on="invoice_id",
                    how="left", indicator=True
                )
                unmatched = merged[merged["_merge"] == "left_only"]
                matched = merged[merged["_merge"] == "both"]

                total_invoiced = invoices["amount"].sum()
                total_paid = matched["paid_amount"].sum() if len(matched) > 0 else 0
                total_unpaid = total_invoiced - total_paid

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Invoices", len(invoices))
                col2.metric("Paid", len(matched))
                col3.metric("Unpaid", len(unmatched))

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Invoiced", f"Rs.{total_invoiced:,}")
                col2.metric("Total Paid", f"Rs.{total_paid:,}")
                col3.metric("Outstanding", f"Rs.{total_unpaid:,}")

                summary = f"""
                Total invoices: {len(invoices)}
                Matched: {len(matched)}
                Unmatched: {len(unmatched)}
                Total invoiced: Rs.{total_invoiced:,}
                Total paid: Rs.{total_paid:,}
                Outstanding: Rs.{total_unpaid:,}
                Unpaid vendors: {unmatched['vendor'].tolist()}
                """

                model = get_model()
                response = model.generate_content(f"""
                You are a finance analyst. Analyze this
                invoice reconciliation and give:
                1. Key findings
                2. Vendors needing follow-up
                3. Recommended actions
                Data: {summary}
                """)

            st.success("Reconciliation Complete!")
            st.subheader("🤖 AI Analysis")
            st.write(response.text)
            st.subheader(f"❌ Unpaid Invoices ({len(unmatched)})")
            st.dataframe(unmatched[['invoice_id', 'vendor', 'amount']])

# ─── INSURANCE RECONCILIATION ───────────────────────
elif module == "🏥 Insurance Reconciliation":
    st.title("🏥 Insurance Reconciliation")
    st.markdown("Compare insurance claims against settlements to find gaps.")

    col1, col2 = st.columns(2)
    with col1:
        claims_file = st.file_uploader("Upload Claims CSV", type="csv")
    with col2:
        settle_file = st.file_uploader("Upload Settlements CSV", type="csv")

    if claims_file and settle_file:
        claims = pd.read_csv(claims_file)
        settlements = pd.read_csv(settle_file)

        col1, col2 = st.columns(2)
        with col1:
            st.write("Claims")
            st.dataframe(claims)
        with col2:
            st.write("Settlements")
            st.dataframe(settlements)

        if st.button("Analyze Claims", type="primary"):
            with st.spinner("Analyzing claims..."):
                merged = claims.merge(
                    settlements, on="claim_id", how="left"
                )
                merged["variance"] = merged["amount_claimed"] - merged["amount_settled"].fillna(0)
                merged["status"] = merged["status"].fillna("pending")

                pending = merged[merged["status"] == "pending"]
                settled = merged[merged["status"] == "settled"]
                high_variance = merged[merged["variance"] > 5000]

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Claims", len(claims))
                col2.metric("Settled", len(settled))
                col3.metric("Pending", len(pending))

                total_claimed = claims["amount_claimed"].sum()
                total_settled = settlements["amount_settled"].sum()

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Claimed", f"Rs.{total_claimed:,}")
                col2.metric("Total Settled", f"Rs.{total_settled:,}")
                col3.metric("High Variance Cases", len(high_variance))

                summary = f"""
                Total claims: {len(claims)}
                Settled: {len(settled)}
                Pending: {len(pending)}
                Total claimed: Rs.{total_claimed:,}
                Total settled: Rs.{total_settled:,}
                High variance: {len(high_variance)}
                Pending IDs: {pending['claim_id'].tolist()}
                """

                model = get_model()
                response = model.generate_content(f"""
                You are an insurance analyst. Review this
                claims data and provide:
                1. Settlement status summary
                2. High risk cases for escalation
                3. Insurer performance
                4. Recommended actions
                Data: {summary}
                """)

            st.success("Analysis Complete!")
            st.subheader("🤖 AI Analysis")
            st.write(response.text)
            st.subheader(f"⏳ Pending Claims ({len(pending)})")
            st.dataframe(pending[['claim_id', 'patient', 'amount_claimed', 'insurer']])
            st.subheader(f"⚠️ High Variance Cases ({len(high_variance)})")
            st.dataframe(high_variance[['claim_id', 'patient', 'amount_claimed', 'amount_settled', 'variance']])

# ─── CREDIT MEMO BUILDER ────────────────────────────
elif module == "📝 Credit Memo Builder":
    st.title("📝 Credit Memo Builder")
    st.markdown("Generate professional credit memos automatically.")

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        client_address = st.text_area("Client Address", height=80)
        original_invoice = st.text_input("Original Invoice Number")
        authorized_by = st.text_input("Authorized By")
    with col2:
        reason = st.text_area("Reason for Credit", height=80)
        st.markdown("**Credit Items**")
        desc1 = st.text_input("Item 1 Description")
        amt1 = st.number_input("Item 1 Amount (Rs.)", min_value=0)
        desc2 = st.text_input("Item 2 Description (optional)")
        amt2 = st.number_input("Item 2 Amount (Rs.)", min_value=0)

    if st.button("Generate Credit Memo", type="primary"):
        if client_name and original_invoice and desc1 and amt1 > 0:
            with st.spinner("Generating credit memo..."):
                items = [{"description": desc1, "amount": amt1}]
                if desc2 and amt2 > 0:
                    items.append({"description": desc2, "amount": amt2})

                items_text = "\n".join([
                    f"- {item['description']}: Rs.{item['amount']:,}"
                    for item in items
                ])
                total = sum(item['amount'] for item in items)
                memo_number = f"CM-{original_invoice}-{date.today().strftime('%Y%m%d')}"

                model = get_model()
                response = model.generate_content(f"""
                Generate a formal professional credit memo:
                MEMO NUMBER: {memo_number}
                DATE: {date.today().strftime('%d %B %Y')}
                INVOICE: {original_invoice}
                CLIENT: {client_name}
                ADDRESS: {client_address}
                ITEMS: {items_text}
                TOTAL: Rs.{total:,}
                REASON: {reason}
                AUTHORIZED BY: {authorized_by}
                Make it formal and ready to send.
                """)

            st.success(f"Credit Memo Generated! Total: Rs.{total:,}")
            st.subheader("📄 Generated Credit Memo")
            st.text_area("", response.text, height=400)
            st.download_button(
                "⬇️ Download Credit Memo",
                response.text,
                file_name=f"credit_memo_{memo_number}.txt"
            )
        else:
            st.error("Please fill in all required fields!")

# ─── BUDGET FORECAST ────────────────────────────────
elif module == "📈 Budget Forecast":
    st.title("📈 Budget Forecast (Mid-Term)")
    st.markdown("Upload budget history to get AI-powered 3-6 month forecasts.")

    budget_file = st.file_uploader("Upload Budget CSV", type="csv")
    months = st.slider("Forecast how many months ahead?", 3, 6, 6)

    if budget_file:
        df = pd.read_csv(budget_file)
        st.subheader("📋 Historical Budget Data")
        st.dataframe(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Monthly Income", f"Rs.{df['income'].mean():,.0f}")
        col2.metric("Avg Monthly Expenses", f"Rs.{df['expenses'].mean():,.0f}")
        col3.metric("Avg Net Surplus", f"Rs.{(df['income'] - df['expenses']).mean():,.0f}")

        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                df['net'] = df['income'] - df['expenses']
                income_growth = df['income'].pct_change().mean() * 100
                expense_growth = df['expenses'].pct_change().mean() * 100

                summary = f"""
                Months of data: {len(df)}
                Avg income: Rs.{df['income'].mean():,.0f}
                Avg expenses: Rs.{df['expenses'].mean():,.0f}
                Avg net: Rs.{df['net'].mean():,.0f}
                Income growth: {income_growth:.1f}% per month
                Expense growth: {expense_growth:.1f}% per month
                Last 3 months: {df.tail(3).to_string()}
                """

                model = get_model()
                response = model.generate_content(f"""
                You are a financial planning analyst.
                Provide a {months} month forecast with:
                1. Monthly projections table
                2. Cash flow warnings
                3. Key trends
                4. Top 3 recommendations
                5. Risk factors
                Data: {summary}
                """)

            st.success("Forecast Ready!")
            st.subheader("🤖 AI Forecast")
            st.write(response.text)

# ─── ANNUAL REPORT ANALYZER ─────────────────────────
elif module == "📄 Annual Report Analyzer":
    st.title("📄 Annual Report Analyzer")
    st.markdown("Upload any company's annual report PDF for instant AI analysis.")

    pdf_file = st.file_uploader("Upload Annual Report PDF", type="pdf")

    if pdf_file:
        if st.button("Analyze Report", type="primary"):
            with st.spinner("Reading PDF and analyzing... please wait..."):
                text = ""
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages[:30]:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

                model = get_model()
                response = model.generate_content(f"""
                You are a senior financial analyst.
                Analyze this annual report and provide:
                1. Company overview
                2. Financial highlights with numbers
                3. Top 3 risks
                4. Business highlights
                5. Management outlook
                6. Overall health score (1-10)
                Report: {text[:10000]}
                """)
                st.session_state['pdf_text'] = text
                st.session_state['analysis_done'] = True

            st.success("Analysis Complete!")
            st.subheader("🤖 AI Analysis")
            st.write(response.text)

        if st.session_state.get('analysis_done'):
            st.subheader("💬 Ask Questions About the Report")
            question = st.text_input("Type your question here:")
            if st.button("Ask"):
                with st.spinner("Thinking..."):
                    model = get_model()
                    answer = model.generate_content(f"""
                    Answer this question based on the annual report.
                    Use specific numbers where available.
                    Report: {st.session_state['pdf_text'][:10000]}
                    Question: {question}
                    """)
                st.write(answer.text)