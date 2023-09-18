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
import plotly.express as px
import calendar
from streamlit_lottie import st_lottie
from streamlit_extras.stylable_container import stylable_container

# Streamlit page configuration
st.set_page_config(
    page_title="Home Loan Calculator",
    page_icon=":house:",
    layout="centered"
)

# Hide "Made with Streamlit" footer menu
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

# Function to load Lottie animation from URL
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie animation
lottie_coding = load_lottieurl("https://lottie.host/488138f0-954d-4e4f-a6ac-a5847226b2a3/IqZMv94lzs.json")

# Create page header
left_column, right_column = st.columns(2)
with right_column:
    pass
with left_column:
    st_lottie(lottie_coding, height=100, key="coding")

st.write("A tool to estimate your monthly loan payments and measure the impact of changes on your loan.")
st.sidebar.header("Home Loan Calculator")
st.write("##")
st.sidebar.subheader("Input your loan details below:")

# Input fields for loan details
loan_amount = st.sidebar.number_input("Loan Amount (R)", value=1000000, step=1000)
interest_rate = st.sidebar.number_input("Interest Rate (%)", value=11.75, step=0.1)
loan_term = st.sidebar.number_input("Loan Term (Years)", value=20, step=1)

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
st.session_state.num_payments = num_payments

# Create a stylable container for the loan summary
with stylable_container(
    key="container_with_border",
    css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px)
        }
        """,
):
    # Inside the `st.markdown` section, update it as follows:
    st.markdown(
        # Header
        f"""
        <div style="border-bottom: 1px solid #ccc; margin-bottom: 16px;">
            <span style="font-size: 16px; font-weight: bold;">LOAN SUMMARY</span>
            
        </div>
        """, unsafe_allow_html=True
    )

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
            <p style="font-weight: lighter; color: #888; margin-bottom: 8px;">Interest paid</p>
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
#st.markdown("---")
st.write("##")
# Initialize new_total_payment with the original payment
new_total_payment = 0
# Initialize new_loan_term_difference with a default value
new_loan_term_difference = 0
payment_difference = 0
new_interest_rate = interest_rate
new_loan_term = 0
new_extra_payment = 0
# interest_rate = 11.75
# loan_term = 30
new_interest_rate_input = interest_rate
new_loan_term_input = loan_term
extra_payment = 0

# Display the input widgets in the sidebar
st.sidebar.subheader("Change loan details below:")
new_interest_rate_input = st.sidebar.number_input("New Interest Rate (%)", value=new_interest_rate_input, step=0.1)
new_loan_term_input = st.sidebar.number_input("New Loan Term (Years)", value=new_loan_term_input, step=1)
new_extra_payment_input = st.sidebar.number_input("New Extra Monthly Payment (R)", value=0, step=10)

# Initialize session_state variables
st.session_state.new_interest_rate = st.session_state.get("new_interest_rate", interest_rate)
st.session_state.new_loan_term = st.session_state.get("new_loan_term", loan_term)
st.session_state.new_extra_payment = st.session_state.get("new_extra_payment", 0)


def generate_amortization_schedule(loan_amount, new_interest_rate, new_loan_term, new_extra_payment):
    monthly_interest_rate = new_interest_rate / 12 / 100
    num_payments = new_loan_term * 12
    monthly_payment = (loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1) + new_extra_payment)

    amortization_schedule = []

    remaining_balance = loan_amount

    for month in range(1, int(num_payments) + 1):
        interest_payment = remaining_balance * monthly_interest_rate 
        principal_payment = monthly_payment - interest_payment 
        remaining_balance -= principal_payment 

        amortization_schedule.append({
            'Month': month,
            'Principal Payment': principal_payment,
            'Interest Payment': interest_payment,
            'Remaining Balance': remaining_balance
        })

    return pd.DataFrame(amortization_schedule)


new_total_interest_paid = 0

def calculate_loan_changes(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate, new_loan_term, new_extra_payment):
    # Original calculations
    monthly_interest_rate = interest_rate / 12 / 100
    num_payments = loan_term * 12
    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)

    # New calculations
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = new_loan_term * 12
    if new_loan_term < loan_term:
        new_num_payments = new_loan_term * 12
    new_total_payment = (loan_amount * (new_monthly_interest_rate * (1 + new_monthly_interest_rate) ** new_num_payments) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1) + new_extra_payment)
    
    # Calculate the payment difference
    payment_difference = monthly_payment - new_total_payment

    return {
        'original_monthly_payment': monthly_payment,
        'new_total_payment': new_total_payment,
        'payment_difference': payment_difference,
    }


def calculate_loan_term(loan_amount, monthly_payment, interest_rate, loan_term, extra_payment):
    # Calculate the monthly interest rate
    monthly_interest_rate = interest_rate / 12 / 100

    # Calculate the number of payments
    num_payments = loan_term * 12

    # Initialize the remaining balance
    remaining_balance = loan_amount

    # Initialize the number of months
    months_elapsed = 0

    # Add a safeguard to limit the number of iterations
    max_iterations = 10000  # You can adjust this value as needed

    # Calculate the estimated loan term in months
    while remaining_balance > 0 and months_elapsed < max_iterations:
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment - extra_payment
        remaining_balance -= principal_payment
        months_elapsed += 1

    # Convert the number of months to years, but set a minimum of 1 year
    estimated_loan_term_in_years = max(months_elapsed / 12, 1)

    return estimated_loan_term_in_years



def calculate_loan_term_difference(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate, new_loan_term, new_extra_payment):
    # Calculate the original monthly payment and loan term
    monthly_interest_rate = interest_rate / 12 / 100
    num_payments = loan_term * 12
    original_monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / ((1 + monthly_interest_rate) ** num_payments - 1)

    # Calculate the new monthly payment and loan term with the extra payment considered
    new_monthly_interest_rate = new_interest_rate / 12 / 100
    new_num_payments = new_loan_term * 12
    if new_loan_term < loan_term:
        new_num_payments = new_loan_term * 12
    new_total_payment = (loan_amount * (new_monthly_interest_rate * (1 + new_monthly_interest_rate) ** new_num_payments) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1) + new_extra_payment)

    # Calculate the estimated loan term difference
    estimated_loan_term_difference = calculate_loan_term(loan_amount, new_total_payment, interest_rate, loan_term, extra_payment) - loan_term

    return estimated_loan_term_difference


# Calculate loan changes and loan term difference
results = calculate_loan_changes(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate_input, new_loan_term_input, new_extra_payment_input)

# Store the new inputs in session state
st.session_state.new_interest_rate = new_interest_rate_input
st.session_state.new_loan_term = new_loan_term_input
st.session_state.new_extra_payment = new_extra_payment_input

# Display loan changes

st.markdown(
    # Header
    f"""
    <div style="border-bottom: 1px solid #ccc; margin-bottom: 16px;">
        <span style="font-size: 16px; font-weight: bold;">UPDATED LOAN SUMMARY</span>

    </div>
    """, unsafe_allow_html=True
)

# Determine whether it's a cost or savings
cost = 0  # Define the threshold for considering it as a cost
savings_or_cost = "cost" if results['payment_difference'] < cost else "savings"

Updated_Loan_Term = (calculate_loan_term(loan_amount, results['new_total_payment'], interest_rate, loan_term, extra_payment)) 
# Create the new monthly payment sentence
new_payment_sentence = f"💡: Based on your loan changes, the new monthly payment is estimated at **R{results['new_total_payment']:,.2f}** with a {savings_or_cost} of **R{results['payment_difference']:,.2f}** and an updated loan term of **{Updated_Loan_Term:.1f} years**."

# Write the sentence
st.write(new_payment_sentence)

# Display the estimated loan term difference
#st.write("💡: Updated Loan Term: {:.2f} years".format(calculate_loan_term(loan_amount, results['new_total_payment'], interest_rate, loan_term, extra_payment)))


# Calculate new amortization schedule
new_amortization_schedule_df = generate_amortization_schedule(loan_amount, new_interest_rate_input, new_loan_term_input, new_extra_payment_input)

#st.write("Visualize how your loan balance decreases over time with each payment.")

new_monthly_interest_rate = new_interest_rate / 12 / 100

# Function to calculate the balance DataFrame based on loan term difference
def calculate_updated_balance_df(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate, new_loan_term, new_extra_payment):
    # Calculate the original and new monthly payments
    original_results = calculate_loan_changes(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate_input, new_loan_term_input, new_extra_payment_input)

    
    if new_loan_term == 0:
        new_total_payment = 0
    else:
        new_results = calculate_loan_changes(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate_input, new_loan_term_input, new_extra_payment_input)

        new_monthly_payment = new_results['new_total_payment']

        new_num_payments = new_loan_term * 12
        # Calculate the new total payment
        new_total_payment = (loan_amount * (new_monthly_interest_rate * (1 + new_monthly_interest_rate) ** new_num_payments) / ((1 + new_monthly_interest_rate) ** new_num_payments - 1) + new_extra_payment)

    # Create DataFrames for the amortization schedules
    original_amortization_df = generate_amortization_schedule(loan_amount, interest_rate, loan_term, extra_payment)
    
    if new_loan_term == 0:
        new_amortization_df = pd.DataFrame(columns=original_amortization_df.columns)
    else:
        new_amortization_df = generate_amortization_schedule(loan_amount, new_interest_rate, new_loan_term, new_extra_payment)

    # Create DataFrames for the balance calculations
    original_balance_df = pd.DataFrame({
        'Payment Number': original_amortization_df['Month'],
        'Balance Type': 'Original',
        'Balance Amount': original_amortization_df['Remaining Balance']

    })

    new_balance_df = pd.DataFrame({
        'Payment Number': new_amortization_df['Month'],
        'Balance Type': 'Updated',
        'Balance Amount': new_amortization_df['Remaining Balance']
    })

    # Concatenate the DataFrames
    combined_balance_df = pd.concat([original_balance_df, new_balance_df])

    return combined_balance_df


# Calculate the updated balance DataFrame
updated_balance_df = calculate_updated_balance_df(loan_amount, interest_rate, loan_term, extra_payment, new_interest_rate_input, new_loan_term_input, new_extra_payment_input)


# Create a plotly express line chart for the balance visualization
line_chart = px.line(
    updated_balance_df,
    x='Payment Number',
    y='Balance Amount',
    color='Balance Type',
    title='Original vs. Updated Loan Balance Over Time',
    labels={'Balance Amount': 'Remaining Balance (R)', 'Payment Number': 'Payment Number'},
)

# Update the layout of the chart
line_chart.update_layout(
    xaxis_title='Payment Number',
    yaxis_title='Remaining Balance (R)',
    showlegend=True,
    legend_title_text='Balance Type',
)

line_chart.update_layout(showlegend=True,
    yaxis_range=[0, max(updated_balance_df["Balance Amount"]) + 50000],  # Adjust the range as needed
 
    yaxis=dict(rangemode="tozero")  # Set y-axis to start from 0
)
# Display the line chart
st.plotly_chart(line_chart, theme="streamlit")


st.markdown("---")
st.subheader("Disclaimer")
st.write("This calculator provides rough estimates of loan payments. It assumes a fixed interest rate for the entire loan term and does not consider other factors like taxes, insurance, or variable interest rates. The results may not be accurate, and you should consult with a financial advisor or lender for precise loan information.")
