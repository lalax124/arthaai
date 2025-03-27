import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go

# Import database module
from database import (
    initialize_database,
    get_or_create_user,
    save_income,
    save_expenses,
    save_assets,
    save_liabilities,
    save_financial_goals,
    save_investment_portfolio,
    save_ai_insight,
    get_user_income,
    get_user_expenses,
    get_user_assets,
    get_user_liabilities,
    get_user_financial_goals,
    get_user_portfolio,
    get_user_insights
)

# Function to apply custom styling
def apply_custom_style():
    # Get the background image path
    image_path = "assets/background.png"
    
    # Read the background image file and encode it in base64
    with open(image_path, "rb") as f:
        background_image = base64.b64encode(f.read()).decode("utf-8")
    
    # Read the CSS content from file
    with open("assets/style.css", "r") as f:
        css_content = f.read()
    
    # Replace the placeholder with the actual encoded image
    css_content = css_content.replace("{background_image_base64}", background_image)
    
    # Apply the custom styling
    st.markdown(f"""
    <style>
    {css_content}
    </style>
    """, unsafe_allow_html=True)

# Initialize the database
initialize_database()

# Import utility modules
from geminiai_use import (
     
    analyze_budget, 
    investment_recommendation,
    analyze_financial_goals
)
from data_processing import (
    format_currency,
    calculate_budget_summary,
    fetch_stock_data,
    calculate_investment_returns,
    calculate_loan_payment,
    generate_amortization_schedule,
    categorize_expenses
)
from frontend import (
    create_expense_pie_chart,
    create_income_expense_bar_chart,
    create_investment_growth_chart,
    create_expense_trend_chart,
    create_savings_goal_progress_chart
)
from moneyanalyser import (
    calculate_net_worth,
    calculate_debt_to_income_ratio,
    calculate_emergency_fund_ratio,
    analyze_retirement_readiness,
    analyze_mortgage_affordability,
    get_stock_metrics,
    calculate_portfolio_metrics
)

# Set page configuration
st.set_page_config(
    page_title="Artha - AI-Powered Financial Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_style()

# Initialize session state variables if they don't exist
if 'income' not in st.session_state:
    st.session_state.income = 0.0
if 'expenses' not in st.session_state:
    st.session_state.expenses = {}
if 'assets' not in st.session_state:
    st.session_state.assets = {}
if 'liabilities' not in st.session_state:
    st.session_state.liabilities = {}
if 'financial_goals' not in st.session_state:
    st.session_state.financial_goals = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# App header with gradient effect
st.markdown('<h1 class="gradient-text">Artha</h1><h1>: Your AI Financial Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.2em; font-style: italic;">Make smarter financial decisions with AI-powered insights</p>', unsafe_allow_html=True)

# User Authentication Section
if not st.session_state.authenticated:
    st.sidebar.title("User Authentication")
    auth_option = st.sidebar.radio("Choose an option:", ["Login", "Register"])
    
    if auth_option == "Login":
        username = st.sidebar.text_input("Username")
        if st.sidebar.button("Login"):
            if username:
                user_id = get_or_create_user(username)
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.authenticated = True
                
                # Load user data from database
                st.session_state.income = get_user_income(user_id)
                st.session_state.expenses = get_user_expenses(user_id)
                st.session_state.assets = get_user_assets(user_id)
                st.session_state.liabilities = get_user_liabilities(user_id)
                st.session_state.financial_goals = get_user_financial_goals(user_id)
                st.session_state.portfolio = get_user_portfolio(user_id)
                
                st.sidebar.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Please enter a username")
    
    elif auth_option == "Register":
        username = st.sidebar.text_input("Username")
        email = st.sidebar.text_input("Email (optional)")
        
        if st.sidebar.button("Register"):
            if username:
                user_id = get_or_create_user(username, email)
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.session_state.authenticated = True
                st.sidebar.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Please enter a username")
    
    # Show limited content for non-authenticated users
    st.info("Please login or register to access all features.")
    st.markdown("""
    ### Welcome to Artha, your AI-powered financial assistant!
    
    Artha helps you:
    * Track your income and expenses
    * Monitor your net worth
    * Set and track financial goals
    * Get AI-powered financial advice
    
    Login or create an account to get started!
    """)
    
    # Stop rendering the rest of the app
    st.stop()

# User is authenticated, show navigation
st.sidebar.title(f"Welcome, {st.session_state.username}")
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a section:",
    ["Dashboard", "Budget Analyzer", "AI Financial Advisor"]
)

# Save Button to persist data to database
if st.sidebar.button("Save Data"):
    with st.spinner("Saving your data..."):
        # Save all user data to database
        save_income(st.session_state.user_id, st.session_state.income)
        save_expenses(st.session_state.user_id, st.session_state.expenses)
        save_assets(st.session_state.user_id, st.session_state.assets)
        save_liabilities(st.session_state.user_id, st.session_state.liabilities)
        
        if st.session_state.financial_goals:
            save_financial_goals(st.session_state.user_id, st.session_state.financial_goals)
        
        if st.session_state.portfolio:
            save_investment_portfolio(st.session_state.user_id, st.session_state.portfolio)
            
        st.sidebar.success("Data saved successfully!")

# Helper function for displaying advice from AI with styled container
def display_ai_advice(title, advice_text):
    st.markdown(f"### {title}")
    st.markdown("""
    <div style="background-color:#f0f2f6; padding:15px; border-radius:5px; border-left:4px solid #4169E1;">
    <h4 style="margin-top:0;">AI-Generated Advice</h4>
    {advice}
    </div>
    """.format(advice=advice_text.replace('\n', '<br>')), unsafe_allow_html=True)

# Dashboard
if page == "Dashboard":
    st.header("Financial Dashboard")
    
    # Layout with columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Financial Summary")
        
        # Net Worth Calculation
        net_worth, total_assets, total_liabilities = calculate_net_worth(
            st.session_state.assets, 
            st.session_state.liabilities
        )
        
        # Display key metrics
        st.metric("Net Worth", format_currency(net_worth))
        
        # Income and Expenses
        if st.session_state.expenses:
            total_expenses = sum(st.session_state.expenses.values())
            st.metric("Monthly Income", format_currency(st.session_state.income))
            st.metric("Monthly Expenses", format_currency(total_expenses))
            savings = st.session_state.income - total_expenses
            st.metric("Monthly Savings", format_currency(savings))
        
        # Emergency Fund Status (if expenses exist)
        if st.session_state.expenses and 'Emergency Fund' in st.session_state.assets:
            monthly_expenses = sum(st.session_state.expenses.values())
            emergency_fund = st.session_state.assets.get('Emergency Fund', 0)
            months_covered = calculate_emergency_fund_ratio(emergency_fund, monthly_expenses)
            if months_covered is not None:
                st.metric("Emergency Fund Coverage", f"{months_covered:.1f} months")
        
    with col2:
        # Expense breakdown (if expenses exist)
        if st.session_state.expenses:
            st.subheader("Expense Breakdown")
            fig = create_expense_pie_chart(st.session_state.expenses)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add your expenses in the Budget Analyzer to see a breakdown.")

# Budget Analyzer
elif page == "Budget Analyzer":
    st.header("Budget Analyzer")
    
    # Create solid black background container
    st.markdown("""
    <div style="background-color: #000000; padding: 20px; border-radius: 10px;">
    """, unsafe_allow_html=True)
    
    # Income Input
    st.subheader("Monthly Income")
    income = st.number_input("Enter your monthly salary (Rs):", 
                            min_value=0.0, 
                            value=st.session_state.income, 
                            step=1000.0,
                            format="%.2f")
    
    # Update session state
    st.session_state.income = income
    
    # Expenses Input
    st.subheader("Monthly Expenses")
    
    # Define common expense categories
    expense_categories = [
        "Housing (Rent/Mortgage)",
        "Utilities (Electricity, Water, Gas)",
        "Groceries",
        "Transportation",
        "Health Care",
        "Entertainment",
        "Dining Out",
        "Shopping",
        "Education",
        "Insurance",
        "Savings",
        "Other"
    ]
    
    # Create expense inputs
    updated_expenses = {}
    
    for category in expense_categories:
        # Get existing value or default to 0
        default_value = st.session_state.expenses.get(category, 0.0)
        
        # Create number input for each category
        expense_value = st.number_input(
            f"{category} (Rs):", 
            min_value=0.0, 
            value=default_value,
            step=100.0,
            format="%.2f",
            key=f"expense_{category}"
        )
        
        # Add to expenses dict if value > 0
        if expense_value > 0:
            updated_expenses[category] = expense_value
    
    # Custom expense category
    st.markdown("---")
    custom_category = st.text_input("Add a custom expense category:")
    
    if custom_category:
        default_value = st.session_state.expenses.get(custom_category, 0.0)
        custom_value = st.number_input(
            f"{custom_category} (Rs):", 
            min_value=0.0, 
            value=default_value,
            step=100.0,
            format="%.2f"
        )
        if custom_value > 0:
            updated_expenses[custom_category] = custom_value
    
    # Update session state
    st.session_state.expenses = updated_expenses
    
    # Calculate budget summary
    budget_summary = calculate_budget_summary(income, updated_expenses)
    
    # Display budget summary
    st.markdown("---")
    st.subheader("Budget Summary")
    
    total_expenses = budget_summary["total_expenses"]
    remaining = budget_summary["remaining"]
    savings_rate = budget_summary["savings_rate"]
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Income", format_currency(income))
    with col2:
        st.metric("Expenses", format_currency(total_expenses))
    with col3:
        st.metric("Remaining", format_currency(remaining))
    
    # Savings rate gauge
    st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    # Income vs Expenses visualization
    if updated_expenses:
        st.subheader("Income vs Expenses")
        fig = create_income_expense_bar_chart(income, total_expenses, remaining)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Expense Breakdown")
        pie_fig = create_expense_pie_chart(updated_expenses)
        st.plotly_chart(pie_fig, use_container_width=True)
    
    # AI Budget analysis and advice
    if updated_expenses and income > 0:
        st.markdown("---")
        st.subheader("AI Budget Analysis")
        
        with st.spinner("Analyzing your budget..."):
            budget_analysis = analyze_budget(income, updated_expenses)
            
            if isinstance(budget_analysis, str):
                # Handle case where response is a simple string
                display_ai_advice("Budget Recommendations", budget_analysis)
            elif isinstance(budget_analysis, dict):
                # Handle case where response is structured data
                if "analysis" in budget_analysis:
                    display_ai_advice("Budget Analysis", budget_analysis["analysis"])
                
                if "recommendations" in budget_analysis:
                    display_ai_advice("Recommendations", budget_analysis["recommendations"])
            
            # Save the AI insight
            if st.session_state.user_id:
                ai_insight = str(budget_analysis)
                save_ai_insight(st.session_state.user_id, "budget_analysis", ai_insight)
    
    # Close the black background container
    st.markdown("</div>", unsafe_allow_html=True)

# AI Financial Advisor
elif page == "AI Financial Advisor":
    st.header("AI Financial Advisor")
    
    # Display chat interface
    st.markdown("Ask me any financial question and I'll provide personalized advice.")
    
    # User input
    user_query = st.text_input("Your financial question:", placeholder="e.g., How can I reduce my debt? or What's the best way to save for retirement?")
    
    # Process user query
    if user_query:
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Get financial context
        financial_context = {
            "income": st.session_state.income,
            "expenses": st.session_state.expenses,
            "assets": st.session_state.assets,
            "liabilities": st.session_state.liabilities,
            "goals": st.session_state.financial_goals,
            "portfolio": st.session_state.portfolio
        }
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = generate_financial_advice(user_query, financial_context) # type: ignore
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Display chat history
    st.markdown("### Conversation")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Financial Advisor:** {message['content']}")
    
    # Clear chat button
    if st.session_state.chat_history and st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Financial topics suggestions
    st.markdown("---")
    st.subheader("Suggested Financial Topics")
    
    topic_cols = st.columns(3)
    
    topics = [
        "How can I improve my credit score?",
        "What's the best way to pay off my debt?",
        "How should I prioritize my financial goals?",
        "How much should I save for retirement?",
        "What's the difference between a Roth IRA and traditional IRA?",
        "How can I reduce my tax burden legally?"
    ]
    
    for i, topic in enumerate(topics):
        with topic_cols[i % 3]:
            if st.button(topic, key=f"topic_{i}"):
                # Set the topic as user query
                user_query = topic
                
                # Add to chat history
                st.session_state.chat_history.append({"role": "user", "content": topic})
                
                # Get financial context
                financial_context = {
                    "income": st.session_state.income,
                    "expenses": st.session_state.expenses,
                    "assets": st.session_state.assets,
                    "liabilities": st.session_state.liabilities,
                    "goals": st.session_state.financial_goals,
                    "portfolio": st.session_state.portfolio
                }
                
                # Get AI response
                with st.spinner("Thinking..."):
                    response = generate_financial_advice(topic, financial_context) # type: ignore
                    
                    # Add to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()

# Display page footer
st.markdown("---")
st.markdown("*Disclaimer: This application provides general financial information and is not a substitute for professional financial advice.*")

