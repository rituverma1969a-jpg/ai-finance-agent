import plotly.express as px
import plotly.graph_objects as go
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
    "📊 Dashboard",
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
    """)

# ─── DASHBOARD ──────────────────────────────────────
elif module == "📊 Dashboard":
    st.title("📊 Finance Analytics Dashboard")
    st.markdown("Upload all your data files for a complete financial overview.")

    st.subheader("📁 Upload Your Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        dash_inv = st.file_uploader("Invoices CSV", type="csv", key="dash_inv")
        dash_pay = st.file_uploader("Payments CSV", type="csv", key="dash_pay")
    with col2:
        dash_claims = st.file_uploader("Claims CSV", type="csv", key="dash_claims")
        dash_settle = st.file_uploader("Settlements CSV", type="csv", key="dash_settle")
    with col3:
        dash_budget = st.file_uploader("Budget CSV", type="csv", key="dash_budget")

    if st.button("Generate Dashboard", type="primary"):

        if dash_inv and dash_pay:
            invoices = pd.read_csv(dash_inv)
            payments = pd.read_csv(dash_pay)
            merged_inv = invoices.merge(payments, on="invoice_id", how="left", indicator=True)
            unmatched_inv = merged_inv[merged_inv["_merge"] == "left_only"]
            matched_inv = merged_inv[merged_inv["_merge"] == "both"]
            total_inv = invoices["amount"].sum()
            total_paid = matched_inv["paid_amount"].sum() if len(matched_inv) > 0 else 0
            outstanding = total_inv - total_paid

            st.subheader("🧾 Invoice Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invoices", len(invoices))
            col2.metric("Paid", len(matched_inv))
            col3.metric("Unpaid", len(unmatched_inv))
            col4.metric("Outstanding", "Rs." + str(int(outstanding)))

            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(
                    values=[len(matched_inv), len(unmatched_inv)],
                    names=["Paid", "Unpaid"],
                    color_discrete_sequence=["#2ecc71", "#e74c3c"],
                    title="Invoice Status"
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.bar(
                    x=["Total Invoiced", "Total Paid", "Outstanding"],
                    y=[total_inv, total_paid, outstanding],
                    color=["Total Invoiced", "Total Paid", "Outstanding"],
                    color_discrete_map={
                        "Total Invoiced": "#3498db",
                        "Total Paid": "#2ecc71",
                        "Outstanding": "#e74c3c"
                    },
                    title="Invoice Amount Breakdown",
                    labels={"x": "Type", "y": "Amount (Rs.)"}
                )
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        if dash_claims and dash_settle:
            claims = pd.read_csv(dash_claims)
            settlements = pd.read_csv(dash_settle)
            merged_cl = claims.merge(settlements, on="claim_id", how="left")
            merged_cl["status"] = merged_cl["status"].fillna("pending")
            pending_cl = merged_cl[merged_cl["status"] == "pending"]
            settled_cl = merged_cl[merged_cl["status"] == "settled"]
            total_claimed = claims["amount_claimed"].sum()
            total_settled = settlements["amount_settled"].sum()

            st.subheader("🏥 Insurance Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Claims", len(claims))
            col2.metric("Settled", len(settled_cl))
            col3.metric("Pending", len(pending_cl))
            col4.metric("Total Claimed", "Rs." + str(int(total_claimed)))

            col1, col2 = st.columns(2)
            with col1:
                fig3 = px.pie(
                    values=[len(settled_cl), len(pending_cl)],
                    names=["Settled", "Pending"],
                    color_discrete_sequence=["#2ecc71", "#e74c3c"],
                    title="Claims Status"
                )
                st.plotly_chart(fig3, use_container_width=True)
            with col2:
                fig4 = px.bar(
                    x=["Total Claimed", "Total Settled"],
                    y=[total_claimed, total_settled],
                    color=["Total Claimed", "Total Settled"],
                    color_discrete_map={
                        "Total Claimed": "#3498db",
                        "Total Settled": "#2ecc71"
                    },
                    title="Claimed vs Settled",
                    labels={"x": "Type", "y": "Amount (Rs.)"}
                )
                fig4.update_layout(showlegend=False)
                st.plotly_chart(fig4, use_container_width=True)

        if dash_budget:
            df = pd.read_csv(dash_budget)
            df['net'] = df['income'] - df['expenses']

            st.subheader("📈 Budget Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Income", "Rs." + str(int(df['income'].mean())))
            col2.metric("Avg Expenses", "Rs." + str(int(df['expenses'].mean())))
            col3.metric("Avg Net", "Rs." + str(int(df['net'].mean())))

            col1, col2 = st.columns(2)
            with col1:
                fig5 = px.line(
                    df, x="month", y=["income", "expenses"],
                    title="Income vs Expenses",
                    color_discrete_map={"income": "#2ecc71", "expenses": "#e74c3c"}
                )
                st.plotly_chart(fig5, use_container_width=True)
            with col2:
                colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in df['net']]
                fig6 = go.Figure(go.Bar(
                    x=df['month'], y=df['net'],
                    marker_color=colors
                ))
                fig6.update_layout(title="Monthly Net Surplus/Deficit")
                st.plotly_chart(fig6, use_container_width=True)

        st.success("Dashboard Generated! ✅")
        
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

                summary = (
                    "Total invoices: " + str(len(invoices)) + "\n"
                    "Matched: " + str(len(matched)) + "\n"
                    "Unmatched: " + str(len(unmatched)) + "\n"
                    "Total invoiced: Rs." + str(int(total_invoiced)) + "\n"
                    "Total paid: Rs." + str(int(total_paid)) + "\n"
                    "Outstanding: Rs." + str(int(total_unpaid)) + "\n"
                    "Unpaid vendors: " + str(unmatched['vendor'].tolist())
                )

                model = get_model()
                response = model.generate_content(
                    "You are a finance analyst. Analyze this invoice reconciliation and give:\n"
                    "1. Key findings\n"
                    "2. Vendors needing follow-up\n"
                    "3. Recommended actions\n"
                    "Data: " + summary
                )

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invoices", len(invoices))
            col2.metric("Paid", len(matched))
            col3.metric("Unpaid", len(unmatched))

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invoiced", "Rs." + str(int(total_invoiced)))
            col2.metric("Total Paid", "Rs." + str(int(total_paid)))
            col3.metric("Outstanding", "Rs." + str(int(total_unpaid)))

            st.success("Reconciliation Complete!")
            st.subheader("🤖 AI Analysis")
            st.write(response.text)
            st.subheader("❌ Unpaid Invoices (" + str(len(unmatched)) + ")")
            st.dataframe(unmatched[['invoice_id', 'vendor', 'amount']])

            st.subheader("📊 Visual Analysis")

            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.bar(
                    x=["Paid Invoices", "Unpaid Invoices"],
                    y=[len(matched), len(unmatched)],
                    color=["Paid Invoices", "Unpaid Invoices"],
                    color_discrete_map={
                        "Paid Invoices": "#2ecc71",
                        "Unpaid Invoices": "#e74c3c"
                    },
                    title="Invoice Payment Status",
                    labels={"x": "Status", "y": "Count"}
                )
                fig1.update_layout(showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.pie(
                    values=[total_paid, total_unpaid],
                    names=["Amount Paid", "Outstanding"],
                    color_discrete_sequence=["#2ecc71", "#e74c3c"],
                    title="Payment Amount Breakdown"
                )
                st.plotly_chart(fig2, use_container_width=True)

            if len(unmatched) > 0:
                fig3 = px.bar(
                    unmatched,
                    x="vendor",
                    y="amount",
                    color_discrete_sequence=["#e74c3c"],
                    title="Unpaid Amount by Vendor",
                    labels={"vendor": "Vendor", "amount": "Amount (Rs.)"}
                )
                st.plotly_chart(fig3, use_container_width=True)

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
                merged = claims.merge(settlements, on="claim_id", how="left")
                merged["variance"] = merged["amount_claimed"] - merged["amount_settled"].fillna(0)
                merged["status"] = merged["status"].fillna("pending")

                pending = merged[merged["status"] == "pending"]
                settled = merged[merged["status"] == "settled"]
                high_variance = merged[merged["variance"] > 5000]

                total_claimed = claims["amount_claimed"].sum()
                total_settled = settlements["amount_settled"].sum()

                summary = (
                    "Total claims: " + str(len(claims)) + "\n"
                    "Settled: " + str(len(settled)) + "\n"
                    "Pending: " + str(len(pending)) + "\n"
                    "Total claimed: Rs." + str(int(total_claimed)) + "\n"
                    "Total settled: Rs." + str(int(total_settled)) + "\n"
                    "High variance: " + str(len(high_variance)) + "\n"
                    "Pending IDs: " + str(pending['claim_id'].tolist())
                )

                model = get_model()
                response = model.generate_content(
                    "You are an insurance analyst. Review this claims data and provide:\n"
                    "1. Settlement status summary\n"
                    "2. High risk cases for escalation\n"
                    "3. Insurer performance\n"
                    "4. Recommended actions\n"
                    "Data: " + summary
                )

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Claims", len(claims))
            col2.metric("Settled", len(settled))
            col3.metric("Pending", len(pending))

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Claimed", "Rs." + str(int(total_claimed)))
            col2.metric("Total Settled", "Rs." + str(int(total_settled)))
            col3.metric("High Variance Cases", len(high_variance))

            st.success("Analysis Complete!")
            st.subheader("🤖 AI Analysis")
            st.write(response.text)
            st.subheader("⏳ Pending Claims (" + str(len(pending)) + ")")
            st.dataframe(pending[['claim_id', 'patient', 'amount_claimed', 'insurer']])
            st.subheader("⚠️ High Variance Cases (" + str(len(high_variance)) + ")")
            st.dataframe(high_variance[['claim_id', 'patient', 'amount_claimed', 'amount_settled', 'variance']])

            st.subheader("📊 Visual Analysis")

            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.pie(
                    values=[len(settled), len(pending)],
                    names=["Settled", "Pending"],
                    color_discrete_sequence=["#2ecc71", "#e74c3c"],
                    title="Claims Settlement Status"
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.bar(
                    x=["Total Claimed", "Total Settled"],
                    y=[total_claimed, total_settled],
                    color=["Total Claimed", "Total Settled"],
                    color_discrete_map={
                        "Total Claimed": "#3498db",
                        "Total Settled": "#2ecc71"
                    },
                    title="Claimed vs Settled Amount",
                    labels={"x": "Type", "y": "Amount (Rs.)"}
                )
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

            if len(high_variance) > 0:
                fig3 = px.bar(
                    high_variance,
                    x="patient",
                    y="variance",
                    color_discrete_sequence=["#e74c3c"],
                    title="High Variance Cases",
                    labels={"patient": "Patient", "variance": "Variance Amount (Rs.)"}
                )
                st.plotly_chart(fig3, use_container_width=True)

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
                    "- " + item['description'] + ": Rs." + str(item['amount'])
                    for item in items
                ])
                total = sum(item['amount'] for item in items)
                memo_number = "CM-" + original_invoice + "-" + date.today().strftime('%Y%m%d')

                model = get_model()
                response = model.generate_content(
                    "Generate a formal professional credit memo:\n"
                    "MEMO NUMBER: " + memo_number + "\n"
                    "DATE: " + date.today().strftime('%d %B %Y') + "\n"
                    "INVOICE: " + original_invoice + "\n"
                    "CLIENT: " + client_name + "\n"
                    "ADDRESS: " + client_address + "\n"
                    "ITEMS: " + items_text + "\n"
                    "TOTAL: Rs." + str(int(total)) + "\n"
                    "REASON: " + reason + "\n"
                    "AUTHORIZED BY: " + authorized_by + "\n"
                    "Make it formal and ready to send."
                )

            st.success("Credit Memo Generated! Total: Rs." + str(int(total)))
            st.subheader("📄 Generated Credit Memo")
            st.text_area("", response.text, height=400)
            st.download_button(
                "⬇️ Download Credit Memo",
                response.text,
                file_name="credit_memo_" + memo_number + ".txt"
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

        avg_inc = df['income'].mean()
        avg_exp = df['expenses'].mean()
        avg_net = (df['income'] - df['expenses']).mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Monthly Income", "Rs." + str(int(avg_inc)))
        col2.metric("Avg Monthly Expenses", "Rs." + str(int(avg_exp)))
        col3.metric("Avg Net Surplus", "Rs." + str(int(avg_net)))

        st.subheader("📊 Historical Trend Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.line(
                df, x="month", y=["income", "expenses"],
                title="Income vs Expenses Trend",
                labels={"value": "Amount (Rs.)", "month": "Month"},
                color_discrete_map={"income": "#2ecc71", "expenses": "#e74c3c"}
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            df['net'] = df['income'] - df['expenses']
            colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in df['net']]
            fig2 = go.Figure(go.Bar(
                x=df['month'], y=df['net'],
                marker_color=colors, name="Net Surplus"
            ))
            fig2.update_layout(title="Monthly Net Surplus/Deficit")
            st.plotly_chart(fig2, use_container_width=True)

        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                df['net'] = df['income'] - df['expenses']
                income_growth = df['income'].pct_change().mean() * 100
                expense_growth = df['expenses'].pct_change().mean() * 100

                summary = (
                    "Months of data: " + str(len(df)) + "\n"
                    "Avg income: Rs." + str(int(df['income'].mean())) + "\n"
                    "Avg expenses: Rs." + str(int(df['expenses'].mean())) + "\n"
                    "Avg net: Rs." + str(int(df['net'].mean())) + "\n"
                    "Income growth: " + str(round(income_growth, 1)) + "% per month\n"
                    "Expense growth: " + str(round(expense_growth, 1)) + "% per month\n"
                    "Last 3 months: " + df.tail(3).to_string()
                )

                model = get_model()
                response = model.generate_content(
                    "You are a financial planning analyst.\n"
                    "Provide a " + str(months) + " month forecast with:\n"
                    "1. Monthly projections table\n"
                    "2. Cash flow warnings\n"
                    "3. Key trends\n"
                    "4. Top 3 recommendations\n"
                    "5. Risk factors\n"
                    "Data: " + summary
                )

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
                response = model.generate_content(
                    "You are a senior financial analyst.\n"
                    "Analyze this annual report and provide:\n"
                    "1. Company overview\n"
                    "2. Financial highlights with numbers\n"
                    "3. Top 3 risks\n"
                    "4. Business highlights\n"
                    "5. Management outlook\n"
                    "6. Overall health score (1-10)\n"
                    "Report: " + text[:10000]
                )
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
                    answer = model.generate_content(
                        "Answer this question based on the annual report.\n"
                        "Use specific numbers where available.\n"
                        "Report: " + st.session_state['pdf_text'][:10000] + "\n"
                        "Question: " + question
                    )
                st.write(answer.text)