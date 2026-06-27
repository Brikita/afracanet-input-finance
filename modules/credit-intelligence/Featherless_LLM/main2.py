# main.py
import os
from openai import OpenAI
# Import our configuration maps
from config import MODEL_MAPPING, FEATHERLESS_BASE_URL, FEATHERLESS_API_KEY

# Initialize the centralized client
client = OpenAI(
    base_url=FEATHERLESS_BASE_URL,
    api_key=FEATHERLESS_API_KEY
)

def run_credit_agent(farmer_profile_data):
    # Dynamically calling the model mapped to this specific agent role
    chosen_model = MODEL_MAPPING["credit_evaluation_agent"]
    print(f"🤖 Spinning up Credit Evaluation Agent using: {chosen_model}")
    
    response = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": "You are the risk assessment engine for AFRACA microfinance."},
            {"role": "user", "content": f"Evaluate this farmer: {farmer_profile_data}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    dummy_farmer = {"name": "Amina Bello", "coop_standing": "Excellent", "mobile_money_consistency": 0.89}
    verdict = run_credit_agent(dummy_farmer)
    print(verdict)