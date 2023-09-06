# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 08:26:00 2023

@author: 27823
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import calendar

st.title(":house: Home Loan Calculator ")
st.sidebar.subheader("User Input")
# Input fields for loan details
loan_amount = st.sidebar.number_input("Loan Amount (R)", value=100000, step=1000)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=11.75, step=0.1)
loan_term = st.sidebar.number_input("Loan Term (Years)", value=30, step=1)

# Input fields for additional payments
extra_payment = st.sidebar.number_input("Extra Monthly Payment (R)", value=0, step=10)

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


# Calculate monthly payment and create amortization table
monthly_interest_rate = interest_rate / 12 / 100
num_payments = loan_term * 12
monthly_payment = (
    loan_amount
    * monthly_interest_rate
    * (1 + monthly_interest_rate) ** num_payments
) / ((1 + monthly_interest_rate) ** num_payments - 1)

if extra_payment > 0:
    total_payment = monthly_payment + extra_payment
else:
    total_payment = monthly_payment

st.subheader("Loan Details")
st.write(f"Monthly Payment: R{monthly_payment:.2f}")
st.write(f"Total Payment (including extra): R{total_payment:.2f}")
#st.write(f"Total Interest Paid: R{total_interest_paid:.2f}")


# Create an amortization table
amortization_df = pd.DataFrame(
    columns=["Month", "Payment", "Principal", "Interest", "Balance"]
)

balance = loan_amount
total_interest_paid = 0  # Initialize total interest paid

for month in range(selected_start_month + 1, num_payments + 1):
    interest_payment = balance * monthly_interest_rate
    principal_payment = total_payment - interest_payment
    balance -= principal_payment
    total_interest_paid += interest_payment  # Accumulate interest payments

    amortization_df = amortization_df.append(
        {
            "Month": f"{calendar.month_name[month % 12]} {selected_start_year + month // 12}",
            "Payment": f"R{total_payment:.2f}",
            "Principal": f"R{principal_payment:.2f}",
            "Interest": f"R{interest_payment:.2f}",
            "Balance": f"R{balance:.2f}",
        },
        ignore_index=True,
    )
selected_month = st.selectbox("Select a Month", list(amortization_df["Month"]))
if st.checkbox("Show Amortization Table"):    
    #st.subheader("Amortization Table")        
    # Display the total interest paid
    st.write(f"Below is the amortization schedule for a R{loan_amount} home loan,for {loan_term} years with a {interest_rate}% rate: ")
    st.dataframe(amortization_df, hide_index=True, use_container_width=True)
st.markdown("---")

# Allow users to change variables and see the impact
st.sidebar.subheader("Change Variables")
new_loan_amount = st.sidebar.number_input("New Loan Amount (R)", value=loan_amount, step=1000)
new_interest_rate = st.sidebar.number_input("New Interest Rate (%)", value=interest_rate, step=0.1)
new_loan_term = st.sidebar.number_input("New Loan Term (Years)", value=loan_term, step=1)
new_extra_payment = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)

# Calculate the impact of changes
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
#st.write(f"New Monthly Payment: R{new_monthly_payment:.2f}")
st.write(f"Monthly Payment (including extra): R{total_payment:.2f}")
st.write(f"New Monthly Payment (including extra): R{new_total_payment:.2f}")

# Calculate and display the savings or additional cost
payment_difference = new_total_payment - total_payment
st.write(f"Difference: R{payment_difference:.2f} {'savings' if payment_difference < 0 else 'additional cost'}")

#Layered Area Chart of new payment and old payment

# Create a DataFrame for new_total_payment, total_payment, and loan_term
df_summary = pd.DataFrame(
    {
        "Original": [loan_term, total_payment],
        "Modified": [new_loan_term, new_total_payment],
    },
    index=["Loan Term (Years)", "Total Payment (including extra)"],
)

# Transpose the DataFrame
df_summary = df_summary.T

# Create a DataFrame for comparing new and original payments over selected months
selected_month_df = amortization_df[
    amortization_df["Month"] >= selected_month
].copy()

selected_month_df["New Payment"] = new_total_payment
selected_month_df["Original Payment"] = total_payment

# Create the area chart to compare payments over months
chart = alt.Chart(selected_month_df).mark_area(opacity=0.5).encode(
    x="Month",
    y=alt.Y("Payment", title="Payment Amount ($)", stack=None),
    color=alt.Color("Payment:N", scale=alt.Scale(scheme="tableau20")),
).properties(
    width=700,
    height=400,
    title="Comparison of New and Original Payments Over Selected Months",
)

st.altair_chart(chart, use_container_width=True)