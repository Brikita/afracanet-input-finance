import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from neo4j import GraphDatabase

# Import configurations
from config import (
    FEATHERLESS_BASE_URL,
    FEATHERLESS_API_KEY,
    MODEL_MAPPING,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    CORS_ORIGINS
)

# Initialize external clients
client = OpenAI(base_url=FEATHERLESS_BASE_URL, api_key=FEATHERLESS_API_KEY)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    neo4j_driver.close()
    print("🔌 Database connections safely closed.")

app = FastAPI(
    title="AFRACA Credit Risk Intelligence API",
    description="Cognitive Underwriter API utilizing Neo4j GDS and Featherless LLM.",
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

# --- GRAPH DATA RETRIEVAL ---
def fetch_graph_context(farmer_id: str) -> dict:
    """
    Simulates pulling the GDS metrics. Once the DB lead finishes the schema, 
    we will drop the actual Cypher query here.
    """
    return {
        "name": "Grace Omwamba",
        "cooperative_name": "Machakos Seed Cooperative",
        "chama_name": "Tumaini Women's Group",
        "trust_pagerank": 0.85,
        "transaction_degree": 12,
        "louvain_repayment_cluster": "High-Performing",
        "environmental_risk": "Mild Drought in Machakos"
    }

# --- ACTION 1: THE CONTEXT INJECTOR ---
def flatten_graph_context(raw_data: dict) -> str:
    """
    Translates raw JSON math scores into a deterministic, human-readable narrative 
    for the LLM so it doesn't get confused by nested data structures.
    """
    name = raw_data.get("name", "The applicant")
    pagerank = raw_data.get("trust_pagerank", 0)
    degree = raw_data.get("transaction_degree", 0)
    cluster = raw_data.get("louvain_repayment_cluster", "Unknown")
    coop = raw_data.get("cooperative_name", "None")
    chama = raw_data.get("chama_name", "None")
    env_risk = raw_data.get("environmental_risk", "None reported")

    # Dynamic baseline logic
    pr_percentile = "top 15% of community trust" if pagerank > 0.8 else "average community trust" if pagerank > 0.5 else "low community trust"

    flattened_text = (
        f"Applicant Name: {name}\n"
        f"Network Topology & Financial Velocity: The farmer is in the {pr_percentile} (PageRank {pagerank}), "
        f"has completed {degree} local transactions (Degree Centrality), and belongs to a '{cluster}' repayment cluster (Louvain).\n"
        f"Social Affiliations: Connects to Cooperative '{coop}' and Chama '{chama}'.\n"
        f"Environmental Risk: {env_risk}."
    )
    return flattened_text

# --- ACTION 2 & 3: MASTER PROMPT & STRICT JSON OUTPUT ---
def request_llm_verdict(flattened_context: str) -> dict:
    """
    Enforces the Kenyan SACCO Underwriter persona and parses the result safely into JSON.
    """
    chosen_model = MODEL_MAPPING["credit_evaluation_agent"]
    
    system_instruction = (
        "You are an expert Agricultural Credit Underwriter for a Kenyan SACCO. "
        "Your job is to analyze alternative graph-data metrics and provide a 3-to-4 sentence rationale "
        "for approving or rejecting an agricultural input voucher.\n\n"
        "RULES OF EXECUTION:\n"
        "1. You MUST explicitly name the specific Chama, Cooperative, or Agrovet the farmer is connected to.\n"
        "2. You MUST cite the environmental risk provided in the context.\n"
        "3. Do not invent data. Assess based only on available social collateral.\n"
        "4. Conclude with a definitive 'RECOMMENDATION: APPROVE' or 'RECOMMENDATION: REJECT' based on whether the overall metrics skew positive.\n\n"
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
        temperature=0.0  # Zero temperature for maximum deterministic rigidity
    )
    
    raw_output = response.choices[0].message.content.strip()
    
    # Failsafe: Strip markdown blocks if the LLM stubbornly includes them anyway
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:-3].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[3:-3].strip()
        
    try:
        # Action 3: Convert the text string into an actual Python dictionary
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # Fallback safeguard so the Lovable UI doesn't crash on a bad LLM generation
        print(f"⚠️ JSON Decode Error. Raw LLM Output: {raw_output}")
        return {
            "decision": "ERROR", 
            "rationale": "The Underwriting AI failed to format its response correctly."
        }

# --- API ENDPOINTS ---
@app.post("/api/evaluate")
async def evaluate_farmer(payload: EvaluationRequest):
    if not payload.farmer_id:
        raise HTTPException(status_code=400, detail="Missing farmer_id parameter")
    
    # 1. Fetch raw graph metrics
    raw_graph_data = fetch_graph_context(payload.farmer_id)
    
    # 2. Inject context via flattening
    flattened_text = flatten_graph_context(raw_graph_data)
    
    # 3. Request deterministic JSON response from LLM
    llm_json_response = request_llm_verdict(flattened_text)
    
    # 4. Return unified payload to Lovable UI
    return {
        "farmer_id": payload.farmer_id,
        "raw_graph_data": raw_graph_data,
        "evaluation": llm_json_response
    }