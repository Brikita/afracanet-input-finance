# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Centralized Featherless Model Registry for our Agents
MODEL_MAPPING = {
    # DeepSeek handles logical analysis, financial scoring, and final edge cases
    "credit_evaluation_agent": "deepseek-ai/DeepSeek-V4-Pro", 
    
    # Kimi-K2 handles parsing large, nested history from agricultural cooperatives
    "cooperative_data_agent": "moonshotai/Kimi-K2.7-Code",   
    
    # GLM handles localized variables, weather reports, and language edge-cases
    "climate_risk_agent": "zai-org/GLM-5.1"
}

# General API Configurations
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

 
# Masumi Protocol Setup
MASUMI_NETWORK = os.getenv("MASUMI_NETWORK", "preprod")
MASUMI_WALLET_MNEUMONIC = os.getenv("MASUMI_WALLET_MNEUMONIC")

# Server Configurations
PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("ALLOWED_CORS_ORIGINS", "*").split(",")