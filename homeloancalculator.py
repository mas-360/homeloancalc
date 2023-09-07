# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 08:26:00 2023

@author: 27823
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import calendar

st.set_page_config(page_title="Home Loan Calculator",
                   layout="wide"
)


st.title(":house: Home Loan Calculator ")
st.write("A tool that helps you estimate your monthly loan payments and the total interest you will pay over the life of the loan. ")
st.sidebar.subheader("User Input")

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


st.subheader("Loan Details")
# Create a summary box
st.markdown('<div class="summary-box-container pos-sticky box-shadow-1 bg-white rounded-md p-6 mx-4">', unsafe_allow_html=True)


# Place the columns within the container
col1, col2, col3 = st.columns(3)

# Monthly payment
with col1:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Monthly payment</p>
        <span style="font-size: 20px; color: #000;">R{monthly_payment:,.2f}</span>
    """, unsafe_allow_html=True)

# Total interest paid
with col2:
    st.markdown(f"""
        <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Total interest paid</p>
        <span style="font-size: 20px; color: #000;">R{amortization_df['Interest Payment'].sum():,.2f}</span>
    """, unsafe_allow_html=True)

# Payoff date
with col3:
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


# Create a function to calculate the new total payment
def calculate_new_total_payment(
    new_loan_amount, new_interest_rate, new_loan_term, new_extra_payment
):
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = new_loan_term * 12
    new_monthly_payment = (
        new_loan_amount
        * new_monthly_interest_rate
        * (1 + new_monthly_interest_rate) ** new_num_payments
    ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
    
    if new_extra_payment > 0:
        return new_monthly_payment + new_extra_payment
    else:
        return new_monthly_payment

# Allow users to change variables and see the impact
st.sidebar.subheader("Change Variables")
new_loan_amount = st.sidebar.number_input("New Loan Amount (R)", value=loan_amount, step=1000)
new_interest_rate = st.sidebar.number_input("New Interest Rate (%)", value=interest_rate, step=0.1)
new_loan_term = st.sidebar.number_input("New Loan Term (Years)", value=loan_term, step=1)
new_extra_payment = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)

# Initialize new_total_payment with the original payment
new_total_payment = monthly_payment
new_monthly_payment = monthly_payment
new_monthly_interest_rate = interest_rate

# Calculate the impact of changes when the "Calculate" button is clicked
if st.sidebar.button("Calculate"):
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = new_loan_term * 12
    new_monthly_payment = (
        new_loan_amount
        * new_monthly_interest_rate
        * (1 + new_monthly_interest_rate) ** new_num_payments
    ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
    if new_extra_payment > 0:
        new_total_payment = new_monthly_payment + new_extra_payment
    else:
        new_total_payment = new_monthly_payment

st.subheader("Impact of Changes")
st.write(f"Monthly Payment: R{monthly_payment:,.2f}")
st.write(f"New Monthly Payment: R{new_total_payment:,.2f}")
# Calculate and display the savings or additional cost
payment_difference = monthly_payment - new_total_payment
st.write(
    f"Difference: R{payment_difference:,.2f} {'additional cost' if payment_difference < 0 else 'savings'}"
)
st.markdown("##")
# Create a DataFrame for comparing new and original balance over the total loan period
selected_month_df = amortization_df.copy()
new_balance = new_loan_amount
new_amortization_df = pd.DataFrame(columns=["Month", "Balance", "Principal", "Interest"])

# Initialize variables to calculate total amounts
original_principal_total = 0
modified_principal_total = 0

original_interest_total = 0
modified_interest_total = 0

for index, row in selected_month_df.iterrows():
    # Calculate new balance based on new payments
    interest_payment = new_balance * new_monthly_interest_rate
    principal_payment = new_monthly_payment - interest_payment
    new_balance -= principal_payment

    # Update total amounts
    original_principal_total += float(row["Principal"].strip("R").replace(",", ""))
    modified_principal_total += principal_payment

    original_interest_total += float(row["Interest"].strip("R").replace(",", ""))
    modified_interest_total += interest_payment

    # Append the data to the new DataFrame with thousand separators
    new_row_data = {
        "Month": row["Month"],
        "Balance": f"R{new_balance:,.2f}",
        "Principal": f"R{principal_payment:,.2f}",
        "Interest": f"R{interest_payment:,.2f}",
    }
    new_amortization_df = new_amortization_df.append(new_row_data, ignore_index=True)

# Extract the last entry to compare balances over the total loan period
last_original_balance = float(selected_month_df["Balance"].iloc[-1].strip("R").replace(",", ""))
last_new_balance = float(new_amortization_df["Balance"].iloc[-1].strip("R").replace(",", ""))

# Calculate the original and modified loan amount breakdown
original_balance_breakdown = [original_principal_total, original_interest_total]
modified_balance_breakdown = [modified_principal_total, modified_interest_total]

principal_total = [original_principal_total, modified_principal_total]
interest_total = [original_interest_total, modified_interest_total ]

if st.checkbox("Show Total Loan Payment Comparison"): 
    fig = go.Figure()
    fig.add_trace(go.Bar(x=principal_total,
                         y=["Original", "Modified"],
                         orientation='h',
                         name='Principal',
                         text=[f"R{val:,.2f}" for val in principal_total],
                         textposition='inside',
                         marker=dict(
                         color='#c6c5b9',
                         line=dict(color='#022B3A', width=3)
        )))
    fig.add_trace(go.Bar(x=interest_total,
                         y=["Original", "Modified"],
                         orientation='h',
                         name='Interest',
                         text=[f"R{val:,.2f}" for val in interest_total],
                         textposition='inside',
                         marker=dict(
                         color='#BFDBF7',
                         line=dict(color='#022B3A', width=3)
        )
    ))
    
    fig.update_layout(barmode='stack', xaxis_title='Amount (R)')
    st.plotly_chart(fig, theme="streamlit")
    
st.markdown("---") 
with st.expander(
    "**Disclaimer:**", expanded=True
):
    st.write(""" Please note that by default this calculator uses the prime interest rate for bond payment calculations. This is purely for convenience and not an indication of the interest rate that might be offered to you by a bank. This calculator is intended to provide estimates based on the indicated amounts and rates. Whilst we make every effort to ensure the accuracy of these calculations, we cannot be held liable for inaccuracies. **masinsight** does not accept liability for any damages arising from the use of this calculator.
             """)   
