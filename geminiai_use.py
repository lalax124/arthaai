import os
import json
import google.generativeai as genai

# Get the Gemini API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not GOOGLE_API_KEY:
    raise ValueError("The GOOGLE_API_KEY environment variable is not set.")

# Configure the Gemini API key
genai.configure(api_key=GOOGLE_API_KEY)

# Set the model to use
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

system_prompt = """
You are a helpful financial advisor named ARTHA. You are an expert in personal finance, budgeting, and investment.
Provide clear, concise, and actionable advice.
"""

def generate_financial_adivice(query, financial_content=None):
    """Generates financial advice based on the user's query and optional financial context."""
    chat = model.start_chat(history=[])
    chat.send_message(system_prompt)

    if financial_content:
        context_message = f"Financial Content: {financial_content}"
        chat.send_message(context_message)

    chat.send_message(query)
    try:
        response = chat.last.text
        return response
    except Exception as e:
        return f"An error occurred: {e}"

def analyze_budget(income, expenses):
    """Analyzes the user's budget and provides recommendations."""
    budget_data = {
        "salary_per_month": income,
        "expenses": expenses
    }
    prompt = f"""
    Analyze the following budget data and provide:
    1. An overall analysis of the budget.
    2. Specific recommendations for improvement.
    3. Areas where the user can potentially save more.
    4. A breakdown of the expenses.
    Budget Data: {json.dumps(budget_data, indent=2)}
    Return in JSON format with keys overall_analysis, recommendations, improvements, expense_breakdown .
    """
    try:
        response = model.generate_content(prompt)
        try:
            # Attempt to load the JSON
            json_response = json.loads(response.text)
            return json.dumps(json_response)
        except json.JSONDecodeError:
           # If not valid JSON, return a fallback message or the raw text
           print("Not valid json")
           return response.text
           
    except Exception as e:
        return f"An error occurred: {e}"

def investement_advise(risk_involved, investment_horizon, current_investments=None):
    """Provides investment advice based on risk tolerance, investment horizon, and current investments."""
    investemnt_data = {
        "risk_involved": risk_involved,
        "investment_horizon": investment_horizon,
        "current_investments": current_investments
    }
    prompt = f"""
    Provide investment advice based on the following information:
    {json.dumps(investemnt_data, indent=2)}
    Consider the risk involved, investment horizon, and current investments.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example usage (for testing)
    print("Testing generate_financial_adivice:")
    advice = generate_financial_adivice("How can I save more money each month?", {"income": 50000, "expenses": {"rent": 15000, "food": 10000}})
    print(advice)

    print("\nTesting analyze_budget:")
    budget_analysis = analyze_budget(50000, {"rent": 15000, "food": 10000, "utilities": 3000})
    print(budget_analysis)

    print("\nTesting investement_advise:")
    investment_advice = investement_advise("low", "long-term", {"stocks": 10000, "bonds": 5000})
    print(investment_advice)
