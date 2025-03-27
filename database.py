import sqlite3
import os
import json
from datetime import datetime

# Database path
DB_PATH = "artha_finance.db"

def initialize_database():
    """Initialize the database with necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create income_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS income_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        source TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create assets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        value REAL NOT NULL,
        category TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create liabilities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS liabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        interest_rate REAL,
        category TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create financial_goals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS financial_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0,
        deadline TEXT,
        priority INTEGER,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create investment_portfolio table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investment_portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        shares REAL NOT NULL,
        cost_basis REAL NOT NULL,
        purchase_date TEXT,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create ai_insights table to store generated insights
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        insight_type TEXT NOT NULL,
        content TEXT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_or_create_user(username, email=None):
    """Get a user or create if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
    else:
        # Create new user
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
    
    conn.close()
    return user_id

def save_income(user_id, amount, source=None):
    """Save income data for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO income_data (user_id, amount, source) VALUES (?, ?, ?)",
        (user_id, amount, source)
    )
    
    conn.commit()
    conn.close()

def save_expenses(user_id, expenses_dict):
    """Save expenses for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing expenses for the user (optional, depending on your needs)
    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
    
    # Insert new expenses
    for category, amount in expenses_dict.items():
        cursor.execute(
            "INSERT INTO expenses (user_id, category, amount) VALUES (?, ?, ?)",
            (user_id, category, amount)
        )
    
    conn.commit()
    conn.close()

def save_assets(user_id, assets_dict):
    """Save assets for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing assets for the user
    cursor.execute("DELETE FROM assets WHERE user_id = ?", (user_id,))
    
    # Insert new assets
    for name, value in assets_dict.items():
        cursor.execute(
            "INSERT INTO assets (user_id, name, value) VALUES (?, ?, ?)",
            (user_id, name, value)
        )
    
    conn.commit()
    conn.close()

def save_liabilities(user_id, liabilities_dict):
    """Save liabilities for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing liabilities for the user
    cursor.execute("DELETE FROM liabilities WHERE user_id = ?", (user_id,))
    
    # Insert new liabilities
    for name, amount in liabilities_dict.items():
        cursor.execute(
            "INSERT INTO liabilities (user_id, name, amount) VALUES (?, ?, ?)",
            (user_id, name, amount)
        )
    
    conn.commit()
    conn.close()

def save_financial_goals(user_id, goals_data):
    """Save financial goals for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing goals for the user
    cursor.execute("DELETE FROM financial_goals WHERE user_id = ?", (user_id,))
    
    # Insert new goals
    for goal in goals_data:
        cursor.execute(
            """INSERT INTO financial_goals 
            (user_id, name, target_amount, current_amount, deadline, priority)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id, 
                goal['name'], 
                goal['target_amount'], 
                goal.get('current_amount', 0),
                goal.get('deadline'),
                goal.get('priority', 0)
            )
        )
    
    conn.commit()
    conn.close()

def save_investment_portfolio(user_id, portfolio_data):
    """Save investment portfolio data for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing portfolio data for the user
    cursor.execute("DELETE FROM investment_portfolio WHERE user_id = ?", (user_id,))
    
    # Insert new portfolio data
    for item in portfolio_data:
        cursor.execute(
            """INSERT INTO investment_portfolio 
            (user_id, ticker, shares, cost_basis, purchase_date)
            VALUES (?, ?, ?, ?, ?)""",
            (
                user_id,
                item['ticker'],
                item['shares'],
                item['cost_basis'],
                item.get('purchase_date')
            )
        )
    
    conn.commit()
    conn.close()

def save_ai_insight(user_id, insight_type, content):
    """Save AI-generated insights for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Convert content to JSON if it's not a string
    if not isinstance(content, str):
        content = json.dumps(content)
    
    cursor.execute(
        "INSERT INTO ai_insights (user_id, insight_type, content) VALUES (?, ?, ?)",
        (user_id, insight_type, content)
    )
    
    conn.commit()
    conn.close()

def get_user_income(user_id):
    """Get the latest income for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT amount FROM income_data WHERE user_id = ? ORDER BY date DESC LIMIT 1",
        (user_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0

def get_user_expenses(user_id):
    """Get expenses for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT category, amount FROM expenses WHERE user_id = ?",
        (user_id,)
    )
    
    expenses = {}
    for row in cursor.fetchall():
        category, amount = row
        expenses[category] = amount
    
    conn.close()
    return expenses

def get_user_assets(user_id):
    """Get assets for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, value FROM assets WHERE user_id = ?",
        (user_id,)
    )
    
    assets = {}
    for row in cursor.fetchall():
        name, value = row
        assets[name] = value
    
    conn.close()
    return assets

def get_user_liabilities(user_id):
    """Get liabilities for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, amount FROM liabilities WHERE user_id = ?",
        (user_id,)
    )
    
    liabilities = {}
    for row in cursor.fetchall():
        name, amount = row
        liabilities[name] = amount
    
    conn.close()
    return liabilities

def get_user_financial_goals(user_id):
    """Get financial goals for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT name, target_amount, current_amount, deadline, priority 
           FROM financial_goals WHERE user_id = ? ORDER BY priority DESC""",
        (user_id,)
    )
    
    goals = []
    for row in cursor.fetchall():
        name, target_amount, current_amount, deadline, priority = row
        goals.append({
            'name': name,
            'target_amount': target_amount,
            'current_amount': current_amount,
            'deadline': deadline,
            'priority': priority
        })
    
    conn.close()
    return goals

def get_user_portfolio(user_id):
    """Get investment portfolio for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT ticker, shares, cost_basis, purchase_date
           FROM investment_portfolio WHERE user_id = ?""",
        (user_id,)
    )
    
    portfolio = []
    for row in cursor.fetchall():
        ticker, shares, cost_basis, purchase_date = row
        portfolio.append({
            'ticker': ticker,
            'shares': shares,
            'cost_basis': cost_basis,
            'purchase_date': purchase_date
        })
    
    conn.close()
    return portfolio

def get_user_insights(user_id, insight_type=None, limit=5):
    """Get AI insights for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if insight_type:
        cursor.execute(
            """SELECT insight_type, content, generated_at
               FROM ai_insights WHERE user_id = ? AND insight_type = ?
               ORDER BY generated_at DESC LIMIT ?""",
            (user_id, insight_type, limit)
        )
    else:
        cursor.execute(
            """SELECT insight_type, content, generated_at
               FROM ai_insights WHERE user_id = ?
               ORDER BY generated_at DESC LIMIT ?""",
            (user_id, limit)
        )
    
    insights = []
    for row in cursor.fetchall():
        insight_type, content, generated_at = row
        
        # Convert JSON strings back to Python objects if needed
        try:
            content_parsed = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            content_parsed = content
        
        insights.append({
            'type': insight_type,
            'content': content_parsed,
            'generated_at': generated_at
        })
    
    conn.close()
    return insights