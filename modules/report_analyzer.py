import pdfplumber
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_pdf_text(pdf_path, max_pages=30):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        pages_to_read = min(max_pages, total)
        for i in range(pages_to_read):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def analyze_annual_report(pdf_path):
    print("Reading PDF... please wait...")
    text = extract_pdf_text(pdf_path)

    if len(text) < 100:
        return "Could not extract enough text from PDF. Try a different file."

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"""
    You are a senior financial analyst at a top investment bank.
    Analyze this annual report and provide:

    1. COMPANY OVERVIEW
       - Company name and business description
       - Key products or services

    2. FINANCIAL HIGHLIGHTS
       - Revenue figures (current and previous year)
       - Net profit figures
       - Year on year growth percentage
       - Key financial ratios if available (ROE, ROI, debt ratio)

    3. TOP 3 RISKS
       - Most significant risks mentioned in the report
       - Potential impact of each risk

    4. BUSINESS HIGHLIGHTS
       - Major achievements this year
       - New products, markets or expansions
       - Key partnerships or acquisitions

    5. MANAGEMENT OUTLOOK
       - What management says about the future
       - Growth plans and strategies

    6. OVERALL HEALTH SCORE
       - Rate the company 1 to 10
       - Justify the score in 2 lines

    Report text: {text[:10000]}
    """)

    return response.text

def ask_question(pdf_text, question, conversation_history):
    conversation_history.append({
        "role": "user",
        "content": question
    })

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    chat = model.start_chat(history=[])

    response = model.generate_content(f"""
    You are a financial analyst. Answer this question based only
    on this annual report. Be specific and use numbers where available.

    Report: {pdf_text[:10000]}

    Question: {question}
    """)

    answer = response.text
    conversation_history.append({
        "role": "assistant",
        "content": answer
    })
    return answer, conversation_history

# Test it
pdf_path = "sample_data/annual_report.pdf"

if os.path.exists(pdf_path):
    analysis = analyze_annual_report(pdf_path)
    print(analysis)

    print("\n--- Q&A MODE ---")
    history = []
    questions = [
        "What was the revenue growth percentage?",
        "What are the top risks for this company?"
    ]
    pdf_text = extract_pdf_text(pdf_path)
    for q in questions:
        print(f"\nQ: {q}")
        answer, history = ask_question(pdf_text, q, history)
        print(f"A: {answer}")
else:
    print("Please add annual_report.pdf to sample_data folder!")