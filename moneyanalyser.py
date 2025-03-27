import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def calculate_net_worth(assets, liabilities):
    """
    Calculate net worth from assets and liabilities.
    
    Args:
        assets (dict): Dictionary of asset categories and values
        liabilities (dict): Dictionary of liability categories and values
        
    Returns:
        tuple: (net_worth, assets_total, liabilities_total)
    """
    assets_total = sum(assets.values()) if assets else 0
    liabilities_total = sum(liabilities.values()) if liabilities else 0
    net_worth = assets_total - liabilities_total
    
    return net_worth, assets_total, liabilities_total

def calculate_debt_to_income_ratio(monthly_debt_payments, monthly_income):
    """
    Calculate debt-to-income ratio.
    
    Args:
        monthly_debt_payments (float): Total monthly debt payments
        monthly_income (float): Monthly income
        
    Returns:
        float: Debt-to-income ratio as a decimal
    """
    if monthly_income <= 0:
        return None
    
    return monthly_debt_payments / monthly_income

def calculate_emergency_fund_ratio(emergency_fund, monthly_expenses):
    """
    Calculate emergency fund ratio (months of expenses covered).
    
    Args:
        emergency_fund (float): Emergency fund amount
        monthly_expenses (float): Monthly expenses
        
    Returns:
        float: Number of months covered by emergency fund
    """
    if monthly_expenses <= 0:
        return None
    
    return emergency_fund / monthly_expenses

def analyze_retirement_readiness(current_age, retirement_age, life_expectancy, 
                               current_savings, monthly_contribution, expected_return,
                               desired_retirement_income):
    """
    Analyze retirement readiness.
    
    Args:
        current_age (int): Current age
        retirement_age (int): Expected retirement age
        life_expectancy (int): Life expectancy
        current_savings (float): Current retirement savings
        monthly_contribution (float): Monthly contribution to retirement
        expected_return (float): Expected annual return as decimal
        desired_retirement_income (float): Desired annual income in retirement
        
    Returns:
        dict: Retirement analysis
    """
    try:
        # Years until retirement
        years_until_retirement = retirement_age - current_age
        
        # Years in retirement
        retirement_years = life_expectancy - retirement_age
        
        # Calculate future value of current savings at retirement
        future_value_current_savings = current_savings * (1 + expected_return) ** years_until_retirement
        
        # Calculate future value of monthly contributions
        monthly_return = expected_return / 12
        months_until_retirement = years_until_retirement * 12
        
        future_value_contributions = 0
        if monthly_return > 0:
            future_value_contributions = monthly_contribution * (((1 + monthly_return) ** months_until_retirement - 1) / monthly_return)
        else:
            future_value_contributions = monthly_contribution * months_until_retirement
        
        # Total projected savings at retirement
        projected_savings = future_value_current_savings + future_value_contributions
        
        # Calculate sustainable annual withdrawal (using 4% rule as a simple starting point)
        sustainable_withdrawal_rate = 0.04
        sustainable_annual_income = projected_savings * sustainable_withdrawal_rate
        
        # Calculate retirement income gap
        income_gap = desired_retirement_income - sustainable_annual_income
        income_gap_percentage = (income_gap / desired_retirement_income) * 100 if desired_retirement_income > 0 else 0
        
        # Determine if on track
        on_track = sustainable_annual_income >= desired_retirement_income
        
        # Return analysis
        return {
            "years_until_retirement": years_until_retirement,
            "retirement_years": retirement_years,
            "projected_savings": projected_savings,
            "sustainable_annual_income": sustainable_annual_income,
            "income_gap": income_gap,
            "income_gap_percentage": income_gap_percentage,
            "on_track": on_track
        }
    
    except Exception as e:
        return {"error": f"Error analyzing retirement readiness: {str(e)}"}

def analyze_mortgage_affordability(income, debt, down_payment, interest_rate, term_years, property_tax_rate=0.01, insurance=100, pmi_rate=0.005):
    """
    Analyze mortgage affordability.
    
    Args:
        income (float): Annual income
        debt (float): Monthly debt payments (excluding housing)
        down_payment (float): Down payment amount
        interest_rate (float): Annual interest rate as decimal
        term_years (int): Mortgage term in years
        property_tax_rate (float): Annual property tax rate as decimal
        insurance (float): Monthly insurance cost
        pmi_rate (float): Annual PMI rate as decimal
        
    Returns:
        dict: Mortgage affordability analysis
    """
    try:
        # Monthly income
        monthly_income = income / 12
        
        # Calculate maximum housing payment (using 28/36 rule)
        # Front-end ratio: Housing costs should be less than 28% of gross monthly income
        front_end_max = monthly_income * 0.28
        
        # Back-end ratio: Total debt payments (including housing) should be less than 36% of gross monthly income
        back_end_max = monthly_income * 0.36 - debt
        
        # Use the more conservative of the two
        max_housing_payment = min(front_end_max, back_end_max)
        
        # Calculate monthly mortgage payment for various home prices
        monthly_rate = interest_rate / 12
        total_payments = term_years * 12
        
        price_ranges = []
        max_price = 0
        
        for price_multiple in range(1, 16):
            home_price = price_multiple * 50000  # $50K increments
            
            # Calculate loan amount
            loan_amount = home_price - down_payment
            
            if loan_amount <= 0:
                continue
                
            # Check if PMI is required (down payment < 20%)
            pmi_required = down_payment / home_price < 0.2
            monthly_pmi = (loan_amount * pmi_rate / 12) if pmi_required else 0
            
            # Calculate mortgage payment
            if monthly_rate == 0:
                monthly_mortgage = loan_amount / total_payments
            else:
                monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
            
            # Add property tax and insurance
            monthly_tax = (home_price * property_tax_rate) / 12
            monthly_total = monthly_mortgage + monthly_tax + insurance + monthly_pmi
            
            # Check if affordable
            affordable = monthly_total <= max_housing_payment
            
            # Store the result
            price_ranges.append({
                "home_price": home_price,
                "monthly_payment": monthly_total,
                "affordable": affordable,
                "details": {
                    "mortgage": monthly_mortgage,
                    "property_tax": monthly_tax,
                    "insurance": insurance,
                    "pmi": monthly_pmi
                }
            })
            
            # Update max affordable price
            if affordable:
                max_price = home_price
        
        # Return analysis
        return {
            "max_housing_payment": max_housing_payment,
            "max_affordable_price": max_price,
            "price_ranges": price_ranges
        }
    
    except Exception as e:
        return {"error": f"Error analyzing mortgage affordability: {str(e)}"}

def get_stock_metrics(ticker):
    """
    Get key metrics for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Stock metrics
    """
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        
        # Basic info
        info = stock.info
        
        # Get historical data for returns calculation
        hist = stock.history(period="1y")
        
        if hist.empty:
            return {"error": f"Could not retrieve data for ticker symbol: {ticker}"}
        
        # Calculate returns
        current_price = hist['Close'].iloc[-1]
        
        # Get 52-week high and low
        price_52wk_high = hist['High'].max()
        price_52wk_low = hist['Low'].min()
        
        # Calculate 1-month return
        if len(hist) >= 21:  # Approximately 1 month of trading days
            price_1mo_ago = hist['Close'].iloc[-21]
            return_1mo = ((current_price / price_1mo_ago) - 1) * 100
        else:
            return_1mo = None
        
        # Calculate 3-month return
        if len(hist) >= 63:  # Approximately 3 months of trading days
            price_3mo_ago = hist['Close'].iloc[-63]
            return_3mo = ((current_price / price_3mo_ago) - 1) * 100
        else:
            return_3mo = None
        
        # Calculate 1-year return
        if len(hist) >= 252:  # Approximately 1 year of trading days
            price_1yr_ago = hist['Close'].iloc[0]
            return_1yr = ((current_price / price_1yr_ago) - 1) * 100
        else:
            return_1yr = None
        
        # Get company name
        name = info.get('longName', ticker)
        
        # Get P/E ratio
        pe_ratio = info.get('trailingPE', None)
        
        # Get dividend yield
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield:
            dividend_yield *= 100  # Convert to percentage
        
        # Return metrics
        return {
            "name": name,
            "current_price": current_price,
            "price_52wk_high": price_52wk_high,
            "price_52wk_low": price_52wk_low,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "returns": {
                "1mo": return_1mo,
                "3mo": return_3mo,
                "1yr": return_1yr
            }
        }
    
    except Exception as e:
        return {"error": f"Error getting stock metrics: {str(e)}"}

def calculate_portfolio_metrics(holdings):
    """
    Calculate portfolio metrics from holdings.
    
    Args:
        holdings (list): List of dictionaries with ticker, shares, and cost_basis
        
    Returns:
        dict: Portfolio metrics
    """
    try:
        if not holdings:
            return {
                "total_value": 0,
                "total_cost": 0,
                "total_gain_loss": 0,
                "total_gain_loss_pct": 0,
                "holdings_data": []
            }
        
        holdings_data = []
        total_value = 0
        total_cost = 0
        
        # Process each holding
        for holding in holdings:
            ticker = holding['ticker']
            shares = holding['shares']
            cost_basis = holding['cost_basis']
            
            # Get current price
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            
            if hist.empty:
                continue
                
            latest_price = hist['Close'].iloc[-1]
            
            # Calculate values
            current_value = shares * latest_price
            total_cost_basis = shares * cost_basis
            gain_loss = current_value - total_cost_basis
            gain_loss_pct = (gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
            
            # Add to holdings data
            holdings_data.append({
                "ticker": ticker,
                "shares": shares,
                "cost_basis": cost_basis,
                "latest_price": latest_price,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct
            })
            
            # Update totals
            total_value += current_value
            total_cost += total_cost_basis
        
        # Calculate portfolio totals
        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
        
        # Return metrics
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_pct": total_gain_loss_pct,
            "holdings_data": holdings_data
        }
    
    except Exception as e:
        return {"error": f"Error calculating portfolio metrics: {str(e)}"}