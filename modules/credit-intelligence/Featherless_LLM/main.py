import os
import json
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Import configurations
from config import (
    FEATHERLESS_BASE_URL,
    FEATHERLESS_API_KEY,
    MODEL_MAPPING,
    CORS_ORIGINS
)

# Initialize external AI client
client = OpenAI(base_url=FEATHERLESS_BASE_URL, api_key=FEATHERLESS_API_KEY)

# The URL of the DB Lead's Flask API (using the Ngrok HTTP tunnel they created)
# Note: Update this if their Ngrok URL changes!
FLASK_DATA_API_URL = "https://sternum-detract-startup.ngrok-free.dev"

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Cognitive Underwriter API is live. Connecting to DB Microservice...")
    yield
    print("🔌 Server shutting down.")

app = FastAPI(
    title="AFRACA Credit Risk Intelligence API",
    description="Cognitive Underwriter API utilizing DB Microservice and Featherless LLM.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    farmer_id: str

# --- 1. DATA RETRIEVAL (MICROSERVICE HTTP CALL) ---
def fetch_graph_context(farmer_id: str) -> dict:
    """
    Makes a REST HTTP call to the DB Lead's Flask API to get the scored farmer data.
    """
    try:
        url = f"{FLASK_DATA_API_URL}/api/farmer/{farmer_id}/score"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            raise ValueError(f"Farmer ID '{farmer_id}' not found in the database.")
            
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Microservice Connection Failed: {e}")
        return {"error": "Failed to connect to the Data Database API."}

# --- 2. THE CONTEXT INJECTOR (UPDATED FOR FLASK PAYLOAD) ---
def flatten_graph_context(raw_data: dict) -> str:
    """
    Translates the Flask API JSON response into a deterministic narrative text for the LLM.
    """
    if "error" in raw_data:
        return f"System Error: {raw_data['error']}. Deny request or flag for manual review."

    name = raw_data.get("name", "The applicant")
    credit_score = raw_data.get("creditScore", 0)
    
    ai_metrics = raw_data.get("aiMetrics", {})
    pagerank = ai_metrics.get("pageRankTrustScore", 0)
    degree = ai_metrics.get("degreeCentralityFootprint", 0)
    peers = ai_metrics.get("knnSimilarEstablishedPeers", 0)
    
    sim_age = raw_data.get("traditionalMetrics", {}).get("simCardAgeDays", 0)
    env_risk = raw_data.get("environmentalRisk", {}).get("status", "Unknown")

    flattened_text = (
        f"Applicant Profile: {name}.\n"
        f"Algorithmic Credit Score: {credit_score}/100.\n"
        f"Network Topology (AI Metrics): PageRank Trust Score of {pagerank}. "
        f"Economic Footprint of {degree} transactions. "
        f"Identified {peers} look-alike successful peers in the network via KNN Similarity.\n"
        f"Identity Stability: Mobile SIM card age is {sim_age} days.\n"
        f"Systemic Environmental Risk: {env_risk}."
    )
    
    return flattened_text

# --- 3. MASTER PROMPT & STRICT JSON OUTPUT ---
def request_llm_verdict(flattened_context: str) -> dict:
    """
    Enforces the Kenyan SACCO Underwriter persona based on the new math-heavy payload.
    """
    chosen_model = MODEL_MAPPING["credit_evaluation_agent"]
    
    system_instruction = (
        "You are an expert Agricultural Credit Underwriter for a Kenyan SACCO. "
        "Your job is to analyze an applicant's algorithmic credit score and alternative network metrics, "
        "then provide a 3-to-4 sentence rationale for approving or rejecting an agricultural input voucher.\n\n"
        "RULES OF EXECUTION:\n"
        "1. You MUST explicitly mention the applicant's 'Algorithmic Credit Score'.\n"
        "2. You MUST justify the decision using the 'PageRank Trust Score' and 'Look-alike peers (KNN)'.\n"
        "3. You MUST cite the 'Systemic Environmental Risk' provided in the context.\n"
        "4. Conclude with a definitive 'RECOMMENDATION: APPROVE' or 'RECOMMENDATION: REJECT' based on whether the overall score and metrics skew positive.\n\n"
        "OUTPUT FORMAT:\n"
        "You must return your response as a raw JSON object with exactly two keys. DO NOT wrap the output in Markdown blocks (like ```json). Just the raw object.\n"
        '{"decision": "APPROVE" | "REJECT", "rationale": "Your explanation here."}'
    )
    
    response = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": flattened_context}
        ],
        temperature=0.0
    )
    
    raw_output = response.choices[0].message.content.strip()
    
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:-3].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[3:-3].strip()
        
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print(f"⚠️ JSON Decode Error. Raw LLM Output: {raw_output}")
        return {
            "decision": "ERROR", 
            "rationale": "The Underwriting AI failed to format its response correctly."
        }

# --- 4. API ENDPOINT ---
@app.post("/api/evaluate")
async def evaluate_farmer(payload: EvaluationRequest):
    if not payload.farmer_id:
        raise HTTPException(status_code=400, detail="Missing farmer_id parameter")
    
    raw_graph_data = fetch_graph_context(payload.farmer_id)
    flattened_text = flatten_graph_context(raw_graph_data)
    llm_json_response = request_llm_verdict(flattened_text)
    
    return {
        "farmer_id": payload.farmer_id,
        "raw_graph_data": raw_graph_data,
        "evaluation": llm_json_response
    }