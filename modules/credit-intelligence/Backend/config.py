# config.py
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Masumi Protocol Setup
MASUMI_NETWORK = os.getenv("MASUMI_NETWORK", "preprod")
MASUMI_WALLET_MNEUMONIC = os.getenv("MASUMI_WALLET_MNEUMONIC")

# Server Configurations
PORT = int(os.getenv("PORT", 8000))

_default_origins = (
    "http://localhost:8080,"
    "http://localhost:3000,"
    "http://localhost:5173,"
    "https://afracanet-ai.vercel.app,"
    "https://crepuscular-elvis-tumulous.ngrok-free.dev"
)

# Split and trim; allow overriding with ALLOWED_CORS_ORIGINS env var (comma-separated)
CORS_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_CORS_ORIGINS", _default_origins).split(",") if o.strip()]
