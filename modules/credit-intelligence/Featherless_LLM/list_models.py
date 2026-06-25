import os
from openai import OpenAI
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

# Initialize the client
client = OpenAI(
    base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
    api_key=os.getenv("FEATHERLESS_API_KEY")
)

try:
    print("Fetching available models from Featherless...\n")
    
    # Call the models.list() endpoint
    models_response = client.models.list()
    
    print("=== AVAILABLE MODELS ===")
    # Loop through and print the exact ID you need to use in your code
    for model in models_response.data:
        # We can filter to only show models containing our hackathon targets
        if any(keyword in model.id.lower() for keyword in ["deepseek", "kimi", "moonshot", "glm"]):
            print(f"- {model.id}")
            
    print("\n========================")
    print("Look for DeepSeek in the list above and copy the EXACT string into your config.py.")

except Exception as e:
    print(f"Failed to fetch models: {e}")