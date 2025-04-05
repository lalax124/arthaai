import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_expense_pie_chart(expenses):
    """
    Create a pie chart of expenses by category.
    
    Args:
        expenses (dict): Dictionary of expense categories and amounts
        
    Returns:
        plotly.graph_objects.Figure: Pie chart figure
    """
    if not expenses:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No expense data available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create data for pie chart
    categories = list(expenses.keys())
    amounts = list(expenses.values())
    
    # Create pie chart
    fig = px.pie(
        names=categories,
        values=amounts,
        title="Expense Breakdown",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    
    # Update layout
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    return fig

def create_income_expense_bar_chart(income, total_expenses, remaining):
    """
    Create a bar chart comparing income, expenses, and remaining amount.
    
    Args:
        income (float): Total income
        total_expenses (float): Total expenses
        remaining (float): Remaining amount (income - expenses)
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Create data for bar chart
    categories = ['Income', 'Expenses', 'Remaining']
    amounts = [income, total_expenses, remaining]
    colors = ['#4CAF50', '#F44336', '#2196F3']
    
    # Create bar chart
    fig = go.Figure()
    
    # Add bars
    for i, (category, amount, color) in enumerate(zip(categories, amounts, colors)):
        fig.add_trace(go.Bar(
            x=[category],
            y=[amount],
            name=category,
            marker_color=color,
            text=f"Rs{amount:,.2f}",
            textposition='auto'
        ))
    
    # Update layout
    fig.update_layout(
        title="Income vs Expenses",
        yaxis=dict(
            title="Amount (Rs)",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, l=0, r=0, b=0)
    )
    
    return fig

def create_investment_growth_chart(initial_investment, monthly_contribution, years, rate_of_return):
    """
    Create a chart showing investment growth over time.
    
    Args:
        initial_investment (float): Initial investment amount
        monthly_contribution (float): Monthly contribution amount
        years (int): Number of years for investment
        rate_of_return (float): Annual rate of return as a decimal
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    # Generate data points for each year
    data = []
    
    # Monthly rate
    monthly_rate = rate_of_return / 12
    
    # Initialize variables
    current_value = initial_investment
    total_contributions = initial_investment
    
    # Add initial point
    data.append({
        'year': 0,
        'value': current_value,
        'contributions': total_contributions,
        'earnings': 0
    })
    
    # Calculate for each year
    for year in range(1, years + 1):
        # Calculate value after this year
        for _ in range(12):  # 12 months in a year
            current_value = current_value * (1 + monthly_rate) + monthly_contribution
            total_contributions += monthly_contribution
        
        # Calculate earnings
        earnings = current_value - total_contributions
        
        # Add data point
        data.append({
            'year': year,
            'value': current_value,
            'contributions': total_contributions,
            'earnings': earnings
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create figure
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['value'],
        mode='lines+markers',
        name='Total Value',
        line=dict(color='#4CAF50', width=3),
        hovertemplate='Year %{x}<br>Value: Rs.%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['contributions'],
        mode='lines+markers',
        name='Total Contributions',
        line=dict(color='#2196F3', width=2, dash='dash'),
        hovertemplate='Year %{x}<br>Contributions: Rs.%{y:,.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Investment Growth Projection ({rate_of_return*100:.1f}% Return)",
        xaxis=dict(
            title="Years",
            dtick=5
        ),
        yaxis=dict(
            title="Value (Rs.)",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    
    return fig

def create_expense_trend_chart(expense_history):
    """
    Create a line chart showing expense trends over time.
    
    Args:
        expense_history (dict): Dictionary with dates as keys and expense amounts as values
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    if not expense_history:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No expense history data available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Convert to DataFrame
    dates = list(expense_history.keys())
    amounts = list(expense_history.values())
    
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'amount': amounts
    })
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create line chart
    fig = px.line(
        df,
        x='date',
        y='amount',
        title="Expense Trend Over Time",
        markers=True
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            title="Date",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title="Amount (Rs.)",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    
    return fig

def create_savings_goal_progress_chart(goals, current_savings):
    """
    Create a chart showing progress towards savings goals.
    
    Args:
        goals (dict): Dictionary of goal names and target amounts
        current_savings (dict): Dictionary of goal names and current amounts
        
    Returns:
        plotly.graph_objects.Figure: Progress chart figure
    """
    if not goals or not current_savings:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No savings goals data available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Prepare data
    goal_names = []
    target_amounts = []
    current_amounts = []
    percentages = []
    
    for goal_name, target in goals.items():
        current = current_savings.get(goal_name, 0)
        percentage = (current / target) * 100 if target > 0 else 0
        
        goal_names.append(goal_name)
        target_amounts.append(target)
        current_amounts.append(current)
        percentages.append(percentage)
    
    # Create progress bars
    fig = go.Figure()
    
    for i, goal in enumerate(goal_names):
        # Add target amount (full bar)
        fig.add_trace(go.Bar(
            x=[target_amounts[i]],
            y=[goal],
            orientation='h',
            name=f"{goal} (Target)",
            marker=dict(
                color='rgba(0, 0, 0, 0.1)',
                line=dict(color='rgba(0, 0, 0, 0.2)', width=1)
            ),
            showlegend=False,
            hovertemplate=f"Target: Rs.{target_amounts[i]:,.2f}<extra></extra>"
        ))
        
        # Add current amount (progress)
        fig.add_trace(go.Bar(
            x=[current_amounts[i]],
            y=[goal],
            orientation='h',
            name=f"{goal} (Current)",
            marker=dict(
                color='#4CAF50',
                line=dict(color='#2E7D32', width=1)
            ),
            text=f"{percentages[i]:.1f}%",
            textposition='inside',
            insidetextanchor='middle',
            showlegend=False,
            hovertemplate=f"Current: Rs.{current_amounts[i]:,.2f} ({percentages[i]:.1f}%)<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title="Savings Goals Progress",
        barmode='overlay',
        xaxis=dict(
            title="Amount (Rs.)",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            title="",
            gridcolor='rgba(0,0,0,0.1)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="closest"
    )
    
    return fig
