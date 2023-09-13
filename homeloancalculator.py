# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 08:26:00 2023

@author: anthea
"""
import requests
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import calendar
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Home Loan Calculator",
                   page_icon=":house:",
                   layout="centered"
)

# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottieurl("https://lottie.host/7ae44262-17df-4ce9-a3d0-f0d7b7941dee/GkrOD8l8vl.json")


left_column, right_column = st.columns((1,0.5))
with left_column:
  st.header("Home Loan Calculator")
with right_column:
  st_lottie(lottie_coding, height=100, key="coding")
st.write("A tool that helps you estimate your monthly loan payments and the total interest you will pay over the life of the loan. ")
st.sidebar.subheader("Input your loan details below:")

# Input fields for loan details
loan_amount = st.sidebar.number_input("Loan Amount (R)", value=100000, step=1000)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=11.75, step=0.1)
loan_term = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)

# Dropdown for selecting the start month
start_month_options = [
    f"{calendar.month_name[month]} ({year})"
    for year in range(2023, 2025)
    for month in range(1, 13)
]
start_month = st.sidebar.selectbox("Select Start Month", start_month_options, index=0)
st.sidebar.markdown("---")

# Extract the selected start month and year
selected_start_month, selected_start_year_with_parentheses = start_month.split()
selected_start_month = list(calendar.month_name).index(selected_start_month)
selected_start_year = int(selected_start_year_with_parentheses.strip("()"))

# Calculate monthly payment
monthly_interest_rate = interest_rate / 12 / 100
num_payments = loan_term * 12
monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)

# Calculate amortization schedule
amortization_schedule = []

remaining_principal = loan_amount
for month in range(1, num_payments + 1):
    interest_payment = remaining_principal * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_principal -= principal_payment
    amortization_schedule.append([month, monthly_payment, principal_payment, interest_payment, remaining_principal])

# Create a DataFrame for the amortization schedule
amortization_df = pd.DataFrame(amortization_schedule, columns=['Month', 'Monthly Payment', 'Principal Payment', 'Interest Payment', 'Remaining Principal'])

# Calculate payoff date based on the last date in the amortization table
last_month = amortization_df.iloc[-1]['Month']
payoff_date = pd.to_datetime(f"{selected_start_year}-{selected_start_month}-01") + pd.DateOffset(months=last_month)

st.subheader("Loan Summary:")
# Create a summary box
st.markdown('<div class="summary-box-container pos-sticky box-shadow-1 bg-white rounded-md p-6 mx-4">', unsafe_allow_html=True)


# Place the columns within the container
col1, col2, col3, col4 = st.columns(4)

# Loan Amount
with col1:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Loan Amount</p>
        <span style="font-size: 20px; color: #000;">R{loan_amount:,.2f}</span>
    """, unsafe_allow_html=True)
  
# Total interest paid
with col2:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Total interest paid</p>
        <span style="font-size: 20px; color: #000;">R{amortization_df['Interest Payment'].sum():,.2f}</span>
    """, unsafe_allow_html=True)

# Monthly Payment
with col3:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Monthly payment</p>
        <span style="font-size: 20px; color: #000;">R{monthly_payment:,.2f}</span>
    """, unsafe_allow_html=True)

# Payoff date
with col4:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Payoff date</p>
        <span style="font-size: 20px; color: #000;">{payoff_date.strftime('%b %Y')}</span>
    """, unsafe_allow_html=True)

# Close the summary box
st.markdown('</div>', unsafe_allow_html=True)

# Create an empty DataFrame with column names
amortization_df = pd.DataFrame(columns=["Month", "Payment", "Principal", "Interest", "Balance"])

balance = loan_amount
total_interest_paid = 0  # Initialize total interest paid

# Initialize an empty list to store row data
row_data_list = []

for month in range(1, num_payments + 1):
    interest_payment = balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    balance -= principal_payment
    total_interest_paid += interest_payment  # Accumulate interest payments

    # Append the data to the list with thousand separators
    row_data = {
        "Month": f"{calendar.month_name[selected_start_month]} {selected_start_year}",
        "Payment": f"R{monthly_payment:,.2f}",
        "Principal": f"R{principal_payment:,.2f}",
        "Interest": f"R{interest_payment:,.2f}",
        "Balance": f"R{balance:,.2f}",
    }
    row_data_list.append(row_data)

    # Update the selected month and year
    selected_start_month += 1
    if selected_start_month > 12:
        selected_start_month = 1
        selected_start_year += 1

# Create a DataFrame from the list of row data
amortization_df = pd.DataFrame(row_data_list)

# Update the selected month and year
selected_start_month += 1
if selected_start_month > 12:
    selected_start_month = 1
    selected_start_year += 1

selected_month = list(amortization_df["Month"])

if st.checkbox("Show Amortization Table"):    
    st.write(f"Below is the amortization schedule for a R{loan_amount:,} home loan, for {loan_term} years with a {interest_rate}% fixed rate: ")
    st.dataframe(amortization_df, hide_index=True, use_container_width=True)
st.markdown("---")

# Initialize new_total_payment with the original payment
new_total_payment = monthly_payment
# Initialize new_loan_term_difference with a default value
new_loan_term_difference = 0
payment_difference = 0
new_interest_rate = interest_rate
new_loan_term = loan_term
new_extra_payment = 0

st.sidebar.subheader("Change Variables below:")
new_interest_rate_input = st.sidebar.number_input("New Interest Rate (%)", value=interest_rate, step=0.1)
new_loan_term_input = st.sidebar.number_input("New Loan Term (Years)", value=loan_term, step=1)
new_extra_payment_input = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)

# Initialize session_state variables
#if 'new_interest_rate' not in st.session_state:
    #st.session_state.new_interest_rate = interest_rate
#if 'new_loan_term' not in st.session_state:
    #st.session_state.new_loan_term = loan_term
#if 'new_extra_payment' not in st.session_state:
    #st.session_state.new_extra_payment = 0

# Initialize session_state variables
st.session_state.new_interest_rate = st.session_state.get("new_interest_rate", interest_rate)
st.session_state.new_loan_term = st.session_state.get("new_loan_term", loan_term)
st.session_state.new_extra_payment = st.session_state.get("new_extra_payment", 0)
    
# Function to calculate loan term based on changes
def calculate_loan_term(loan_amount, interest_rate, monthly_payment, extra_payment=0):
    monthly_interest_rate = interest_rate / 12
    unpaid_balance = loan_amount
    months_elapsed = 0

    while unpaid_balance > 0:
        interest_payment = unpaid_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment - extra_payment
        unpaid_balance -= principal_payment
        months_elapsed += 1

    return months_elapsed
  

# Function to calculate loan changes
def calculate_loan_changes(
    loan_amount, interest_rate, loan_term, extra_payment,
    new_interest_rate, new_loan_term, new_extra_payment
):
    # Original calculations
    monthly_interest_rate = interest_rate / 12 / 100
    num_payments = loan_term * 12
    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)

    # New calculations
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = loan_term * 12
    if new_loan_term < loan_term:
        new_num_payments = new_loan_term * 12
    new_total_payment = (loan_amount * (new_monthly_interest_rate * (1 + new_monthly_interest_rate) ** new_num_payments) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1) + new_extra_payment)
    
    # Calculate the payment difference
    payment_difference = monthly_payment - new_total_payment

    # Calculate the loan term difference
    new_loan_term_difference = new_loan_term - loan_term

    return {
        'original_monthly_payment': monthly_payment,
        'new_total_payment': new_total_payment,
        'payment_difference': payment_difference,
        'new_loan_term_difference': new_loan_term_difference,
    }

# Function to update session_state variables and the summary box
def update_summary_box():
    new_interest_rate_input = st.sidebar.number_input("New Interest Rate (%)", key="new_interest_rate", value=st.session_state.new_interest_rate, step=0.1)
    new_loan_term_input = st.sidebar.number_input("New Loan Term (Years)", key="new_loan_term", value=st.session_state.new_loan_term, step=1)
    new_extra_payment_input = st.sidebar.number_input("New Extra Monthly Payment (R)", key="new_extra_payment", value=st.session_state.new_extra_payment, step=10)

    # Calculate the new monthly payment
    new_total_payment = calculate_loan_changes(
        loan_amount, interest_rate, loan_term, new_extra_payment_input,
        new_interest_rate_input, new_loan_term_input, new_extra_payment_input
    )['new_total_payment']

    # Calculate the payment difference
    payment_difference = new_total_payment - monthly_payment

    # Calculate the new loan term difference
    new_loan_term_difference = calculate_loan_term(
        loan_amount, new_interest_rate_input, new_total_payment, new_extra_payment_input
    ) - calculate_loan_term(loan_amount, interest_rate, monthly_payment, new_extra_payment_input)

    st.session_state.new_interest_rate = new_interest_rate_input
    st.session_state.new_loan_term = new_loan_term_input
    st.session_state.new_extra_payment = new_extra_payment_input

    return new_total_payment, payment_difference, new_loan_term_difference

# Trigger the update when the user presses a button
update_button = st.sidebar.button("Update")

# Update summary box and get results
if update_button:
    new_total_payment, payment_difference, new_loan_term_difference = update_summary_box()

# Create the summary box
st.markdown('<div class="summary-box-container pos-sticky box-shadow-1 bg-white rounded-md p-6 mx-4">', unsafe_allow_html=True)

# Place the columns within the container
col1, col2, col3, col4 = st.columns(4)

# Loan Amount
with col1:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Loan Amount</p>
        <span style="font-size: 20px; color: #000;">R{loan_amount:,.2f}</span>
    """, unsafe_allow_html=True)

# New Monthly Payment
with col2:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">New Monthly payment</p>
        <span style="font-size: 20px; color: #000;">R{new_total_payment:.2f}</span>
    """, unsafe_allow_html=True)
  
# New Total interest paid
with col3:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Payment Difference</p>
        <span style="font-size: 20px; color: #000;">R{payment_difference:.2f}</span>
    """, unsafe_allow_html=True)

# Loan Term Difference
with col3:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Loan Term Difference</p>
        <span style="font-size: 20px; color: #000;">{abs(new_loan_term_difference / 12):.1f} years {'shorter' if new_loan_term_difference < 0 else 'longer'}</span>
    """, unsafe_allow_html=True)

# Close the summary box
st.markdown('</div>', unsafe_allow_html=True)

st.write("##")

# Function to explain loan changes
def explain_loan_changes(new_extra_payment, new_interest_rate, new_loan_term_difference):
    explanations = []

    if new_extra_payment > 0:
        explanations.append(
            "💡: When you make extra payments towards your loan principal, it has a positive effect on your loan. It reduces the outstanding balance faster, potentially shortening the loan term and saving you money on interest payments."
        )
    elif new_extra_payment < 0:
        explanations.append(
            "💡: When you reduce your extra payments compared to the original loan terms, you are paying less money upfront, which typically leads to a longer loan term or higher overall interest payments. This is favorable in the short term but may result in higher overall costs over the life of the loan."
        )

    if new_interest_rate < interest_rate:
        explanations.append(
            "💡: When you secure a loan with a lower interest rate than the original loan, it has a positive impact. A lower interest rate means you'll pay less in interest over the life of the loan, resulting in lower overall costs."
        )
    elif new_interest_rate > interest_rate:
        explanations.append(
            "💡: When the interest rate on a loan increases compared to the original terms, it means you will pay more in interest over the life of the loan. This is unfavorable as it increases the cost of borrowing."
        )

    if new_loan_term_difference < 0:
        explanations.append(
            "💡: Having a shorter loan term compared to the original loan is a positive factor. A shorter term typically means higher monthly payments, but it can save you a significant amount of money in interest over the life of the loan. It also allows you to pay off the loan more quickly, reducing financial stress and risk."
        )
    elif new_loan_term_difference > 0:
        explanations.append(
            "💡: When borrowers choose to extend the loan term beyond the original terms, it typically results in lower monthly payments but may also lead to higher overall interest payments. Extending the loan term can make it more affordable in the short term but can increase the total cost of the loan over time."
        )

    if not explanations:
        explanations.append(
            "No changes in the loan variables were made.\n"
            "The original loan terms remain unchanged."
        )

    return "\n\n".join(explanations)

# Display explanations
explanation = explain_loan_changes(new_extra_payment_input, new_interest_rate_input, new_loan_term_difference)
st.subheader("Impact of Changes")
st.write(explanation)

st.markdown("---") 
with st.expander(
    "**Disclaimer:**", expanded=True
):
    st.write(""" Please note that by default this calculator uses the prime interest rate for bond payment calculations. This is purely for convenience and not an indication of the interest rate that might be offered to you by a bank. This calculator is intended to provide estimates based on the indicated amounts and rates. Whilst we make every effort to ensure the accuracy of these calculations, we cannot be held liable for inaccuracies and do not accept liability for any damages arising from the use of this calculator.
             """)
