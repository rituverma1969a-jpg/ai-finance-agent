import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def forecast_budget(budget_file, forecast_months=6):
    df = pd.read_csv(budget_file)
    df['month'] = pd.to_datetime(df['month'])
    df['net'] = df['income'] - df['expenses']
    df['expense_ratio'] = (df['expenses'] / df['income'] * 100).round(1)

    avg_income = df['income'].mean()
    avg_expenses = df['expenses'].mean()
    avg_net = df['net'].mean()
    income_growth = df['income'].pct_change().mean() * 100
    expense_growth = df['expenses'].pct_change().mean() * 100
    best_month = df.loc[df['net'].idxmax(), 'month'].strftime('%B %Y')
    worst_month = df.loc[df['net'].idxmin(), 'month'].strftime('%B %Y')

    summary = f"""
    Historical period: {len(df)} months
    Average monthly income: Rs.{avg_income:,.0f}
    Average monthly expenses: Rs.{avg_expenses:,.0f}
    Average monthly net surplus: Rs.{avg_net:,.0f}
    Income growth rate: {income_growth:.1f}% per month
    Expense growth rate: {expense_growth:.1f}% per month
    Average expense ratio: {df['expense_ratio'].mean():.1f}%
    Best performing month: {best_month}
    Worst performing month: {worst_month}
    Last 3 months data:
    {df.tail(3)[['month','income','expenses','net']].to_string()}
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(f"""
    You are a senior financial planning analyst.
    Based on this budget history provide a {forecast_months} month
    mid-term forecast including:

    1. MONTHLY PROJECTIONS TABLE
       Show projected income, expenses and net for each
       of the next {forecast_months} months

    2. CASH FLOW WARNINGS
       Flag any months where expenses may exceed income

    3. KEY TRENDS
       Income and expense growth patterns

    4. TOP 3 RECOMMENDATIONS
       Specific actions to improve financial performance

    5. RISK FACTORS
       What could negatively affect this forecast

    Historical data: {summary}
    """)

    return response.text

forecast = forecast_budget(
    "sample_data/budget.csv",
    forecast_months=6
)
print(forecast)