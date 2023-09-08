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
from streamlit_lottie import st_lottie
import calendar

st.set_page_config(page_title="Home Loan Calculator",
                   page_icon=":house:",
                   layout="wide"
)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottieurl("https://lottie.host/7ae44262-17df-4ce9-a3d0-f0d7b7941dee/GkrOD8l8vl.json")

with st.container():
  left_column, right_column = st.columns((1,1))
  with left_column:
    st_lottie(lottie_coding,height=100,key="coding")
  with right_column:
    st.title("Home Loan Calculator") 
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
    loan_amount, new_interest_rate, new_loan_term, new_extra_payment
):
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = loan_term * 12
    new_monthly_payment = (
        loan_amount
        * new_monthly_interest_rate
        * (1 + new_monthly_interest_rate) ** new_num_payments
    ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
    
    if new_extra_payment > 0:
        return new_monthly_payment + new_extra_payment
    else:
        return new_monthly_payment

# Allow users to change variables and see the impact
st.sidebar.subheader("Change Variables")
#new_loan_amount = st.sidebar.number_input("New Loan Amount (R)", value=loan_amount, step=1000)
new_interest_rate = st.sidebar.number_input("New Interest Rate (%)", value=interest_rate, step=0.1)
new_loan_term = st.sidebar.number_input("New Loan Term (Years)", value=loan_term, step=1)
new_extra_payment = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)

# Initialize new_total_payment with the original payment
new_total_payment = monthly_payment
new_monthly_payment = monthly_payment
new_monthly_payment_with_interest_rate = monthly_payment  # Initialize the second monthly payment

# Calculate the impact of changes when the "Calculate" button is clicked
if st.sidebar.button("Calculate"):
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = new_loan_term * 12

    if new_extra_payment > 0:
        new_monthly_payment = (
            loan_amount
            * new_monthly_interest_rate
            * (1 + new_monthly_interest_rate) ** new_num_payments
        ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)
        new_total_payment = new_monthly_payment + new_extra_payment

    if new_monthly_interest_rate != interest_rate / 12 / 100:
        new_monthly_payment_with_interest_rate = (
            loan_amount
            * new_monthly_interest_rate
            * (1 + new_monthly_interest_rate) ** new_num_payments
        ) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1)

    # Calculate the payment difference
    payment_difference = monthly_payment - new_total_payment

    # Calculate the loan term difference
    original_num_payments = loan_term * 12
    new_loan_term_difference = new_num_payments - original_num_payments
else:
    # If the "Calculate" button has not been clicked, set the payment and loan term differences to 0
    payment_difference = 0
    new_loan_term_difference = 0

st.subheader("Impact of Changes")
#st.write(f"Monthly Payment: R{monthly_payment:,.2f}")
#st.write(f"New Monthly Payment: R{new_monthly_payment:,.2f}")
#st.write(f"New Monthly Payment (with Interest Rate Change): R{new_monthly_payment_with_interest_rate:,.2f}")
#st.write(
    #f"Difference: R{payment_difference:,.2f} {'savings' if payment_difference < 0 else 'additional cost'}"
#)



def explain_loan_changes(new_extra_payment, new_interest_rate, new_loan_term_difference): #new_loan_term):
    explanations = []

    # Explain the impact of adding extra payment
    if new_extra_payment > 0:
        explanations.append(
           
            f"New Monthly Payment: R{new_monthly_payment:,.2f}.\n"  
            f"Difference: R{payment_difference:,.2f} {'savings' if payment_difference < 0 else 'additional cost'}.\n"  
            "When you make extra payments towards your loan principal, it has a positive effect on your loan. It reduces the outstanding balance faster, potentially shortening the loan term and saving you money on interest payments."
        )

    # Explain the impact of a lower interest rate
    if new_interest_rate < 0:
        explanations.append(

            "When you secure a loan with a lower interest rate than the original loan, it has a positive impact. A lower interest rate means you'll pay less in interest over the life of the loan, resulting in lower overall costs."
        )

    # Explain the impact of a shorter loan term 

    #if new_loan_term < 0:
        #explanations.append(
            #"Shorter Loan Term than Original:\n"
            #"Relationship: Positive\n"
            #"Having a shorter loan term compared to the original loan is also a positive factor. A shorter term typically means higher monthly payments, but it can save you a significant amount of money in interest over the life of the loan. It also allows you to pay off the loan more quickly, reducing financial stress and risk."
        #)
        
    if new_loan_term_difference != 0:
        st.write(
            f"Loan Term Difference: {abs(new_loan_term_difference) / 12} years {'shorter' if new_loan_term_difference < 0 else 'longer'}.\n"  
            "Having a shorter loan term compared to the original loan is a positive factor. A shorter term typically means higher monthly payments, but it can save you a significant amount of money in interest over the life of the loan. It also allows you to pay off the loan more quickly, reducing financial stress and risk."
        )

    # Check if no changes were made
    if not explanations:
        explanations.append(
            "No changes in the loan variables were made.\n"
            "The original loan terms remain unchanged."
        )

    return "\n\n".join(explanations)


explanation = explain_loan_changes(new_extra_payment, new_interest_rate, new_loan_term_difference) #new_loan_term)
st.write(explanation)

st.markdown("---") 
with st.expander(
    "**Disclaimer:**", expanded=True
):
    st.write(""" Please note that by default this calculator uses the prime interest rate for bond payment calculations. This is purely for convenience and not an indication of the interest rate that might be offered to you by a bank. This calculator is intended to provide estimates based on the indicated amounts and rates. Whilst we make every effort to ensure the accuracy of these calculations, we cannot be held liable for inaccuracies and do not accept liability for any damages arising from the use of this calculator.
             """)   
