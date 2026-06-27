import os
import json
import requests
import urllib3
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI
from neo4j import GraphDatabase

# --- CONFIGURATIONS ---
from config import (
    FEATHERLESS_BASE_URL,
    FEATHERLESS_API_KEY,
    MODEL_MAPPING,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    CORS_ORIGINS
)

# Disable SSL Warnings for the Africa's Talking Hackathon Bypass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
AT_USERNAME = "sandbox"
AT_API_KEY = "REMOVED_HISTORICAL_CREDENTIAL"

# Initialize external clients
client = OpenAI(base_url=FEATHERLESS_BASE_URL, api_key=FEATHERLESS_API_KEY)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# --- HACKATHON IN-MEMORY QUEUE ---
# Stores incoming USSD applications for the Lovable UI to fetch
pending_applications = []

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

# --- PYDANTIC MODELS ---
class EvaluationRequest(BaseModel):
    farmer_id: str

class ApprovalRequest(BaseModel):
    farmer_id: str

# --- 1. GRAPH DATA RETRIEVAL ---
def fetch_graph_context(farmer_id: str) -> dict:
    """Pulls real GDS metrics and relationships from Neo4j."""
    
    #  HACKATHON BYPASS: DB Lead is offline.
    # We return Amina's data directly so you can build the UI.
    if farmer_id.upper() in ["F-101", "F101"]:
        return {
            "name": "Amina Wanjiku",
            "cooperative_name": "Meru Dairy Cooperative",
            "chama_name": "Bidii Women Table Banking",
            "agrovet_name": "Mavuno Fertilizer & Seeds",
            "trust_pagerank": 0.85,
            "transaction_degree": 12,
            "louvain_repayment_cluster": "High-Performing",
            "environmental_risk": "Mild Drought (Penalty: 10)",
            "creditScore": 85,
            "similarPeers": 3,
            "simAgeDays": 1200
        }
    
    #  LIVE DB QUERY (Runs when DB is turned back on)
    query = """
    MATCH (f:Farmer {id: $farmer_id})
    OPTIONAL MATCH (f)-[:LOCATED_IN]->(reg:Region)-[:EXPOSED_TO]->(risk:EnvironmentalRisk)
    OPTIONAL MATCH (f)-[sim:SIMILAR_TO]->(peer:Farmer)
    OPTIONAL MATCH (f)-[:MEMBER_OF]->(c:Chama)
    OPTIONAL MATCH (f)-[:DELIVERS_TO]->(coop:AgriCooperative)
    OPTIONAL MATCH (f)-[:PERFORMED_TX]->(m:MpesaTransaction)-[:PAID_TO]->(dealer:AgriDealer)
    RETURN 
        f.name AS Applicant,
        COALESCE(f.mobileMoneySimCardAgeDays, f.simAge, 0) AS SimAgeDays,
        COALESCE(f.trust_pagerank, 0.0) AS CommunityTrustScore,
        COALESCE(f.economic_footprint, 0.0) AS EconomicFootprint,
        COALESCE(f.community_id, -1) AS LouvainCommunityId,
        count(sim) AS SimilarPeersCount,
        COALESCE(risk.intensityScore, 0.0) AS ClimateRiskPenalty,
        COALESCE(risk.type, 'Unknown') AS LiveClimateStatus,
        c.name AS ChamaName,
        coop.name AS CoopName,
        dealer.businessName AS AgrovetName
    """
    with neo4j_driver.session() as session:
        result = session.run(query, farmer_id=farmer_id.upper())
        record = result.single()
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found in database.")
            
        data = dict(record)
        return {
            "name": data["Applicant"],
            "cooperative_name": data["CoopName"] or "None",
            "chama_name": data["ChamaName"] or "None",
            "agrovet_name": data["AgrovetName"] or "your local supplier",
            "trust_pagerank": round(data["CommunityTrustScore"], 3),
            "transaction_degree": data["EconomicFootprint"],
            "louvain_repayment_cluster": str(data["LouvainCommunityId"]),
            "environmental_risk": f"{data['LiveClimateStatus']} (Penalty: {data['ClimateRiskPenalty']})",
            "creditScore": min(max(30 + (data["CommunityTrustScore"] * 50) + data["EconomicFootprint"], 0), 100), # Simplified DB score
            "similarPeers": data["SimilarPeersCount"],
            "simAgeDays": data["SimAgeDays"]
        }

# --- 2. FEATHERLESS LLM LOGIC ---
def flatten_graph_context(raw_data: dict) -> str:
    name = raw_data.get("name", "The applicant")
    pagerank = raw_data.get("trust_pagerank", 0)
    degree = raw_data.get("transaction_degree", 0)
    cluster = raw_data.get("louvain_repayment_cluster", "Unknown")
    coop = raw_data.get("cooperative_name", "None")
    chama = raw_data.get("chama_name", "None")
    env_risk = raw_data.get("environmental_risk", "None reported")

    pr_percentile = "top 15% of community trust" if pagerank > 0.8 else "average community trust" if pagerank > 0.5 else "low community trust"

    flattened_text = (
        f"Applicant Name: {name}\n"
        f"Network Topology & Financial Velocity: The farmer is in the {pr_percentile} (PageRank {pagerank}), "
        f"has completed {degree} local transactions (Degree Centrality), and belongs to a '{cluster}' repayment cluster (Louvain).\n"
        f"Social Affiliations: Connects to Cooperative '{coop}' and Chama '{chama}'.\n"
        f"Environmental Risk: {env_risk}."
    )
    return flattened_text

def request_llm_verdict(flattened_context: str) -> dict:
    chosen_model = MODEL_MAPPING["credit_evaluation_agent"]
    
    system_instruction = (
        "You are an expert Agricultural Credit Underwriter for a Kenyan SACCO. "
        "Your job is to analyze alternative graph-data metrics and provide a 3-to-4 sentence rationale "
        "for approving or rejecting an agricultural input voucher.\n\n"
        "RULES OF EXECUTION:\n"
        "1. You MUST explicitly name the specific Chama, Cooperative, or Agrovet the farmer is connected to.\n"
        "2. You MUST cite the environmental risk provided in the context.\n"
        "3. Do not invent data. Assess based only on available social collateral.\n"
        "4. Conclude with a definitive 'RECOMMENDATION: APPROVE' or 'RECOMMENDATION: REJECT'.\n\n"
        "OUTPUT FORMAT:\n"
        "You must return your response as a raw JSON object with exactly two keys. DO NOT wrap the output in Markdown blocks.\n"
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
        return {"decision": "ERROR", "rationale": "The Underwriting AI failed to format its response correctly."}

# --- 3. AFRICA'S TALKING SMS EXECUTOR ---
def execute_approval_sms(phone_number: str, national_id: str, lang: str, agrovet_name: str):
    """Bypasses local Windows SSL errors to hit AT via direct REST requests."""
    if lang == "sw":
        message = f"Hongera! Vocha yako ya AfracaNet ya Kitambulisho {national_id} imeidhinishwa na SACCO. Nenda {agrovet_name} kuchukua pembejeo zako."
    else:
        message = f"Congratulations! Your AfracaNet voucher for ID {national_id} has been approved. Proceed to {agrovet_name} to collect your inputs."
        
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {
        "ApiKey": AT_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "username": AT_USERNAME,
        "to": phone_number,
        "message": message
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        print(f"SMS API Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Encountered an error while sending SMS: {e}")

# ==========================================
# --- API ENDPOINTS (THE ORCHESTRATION) ---
# ==========================================

@app.post("/api/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(default=""),
    serviceCode: str = Form(default=""),
    phoneNumber: str = Form(default=""),
    text: str = Form(default="")
):
    """Handles the Phone Menu and pushes applications to the Lovable Queue."""
    parts = text.split("*") if text else []
    
    if text == "":
        # Language Selection
        response = "CON Welcome to AfracaNet / Karibu AfracaNet.\n1. English\n2. Kiswahili"
        
    elif len(parts) == 1:
        if parts[0] == "1":
            response = "CON Enter your National ID (e.g., F-101):"
        elif parts[0] == "2":
            response = "CON Weka Namba yako ya Kitambulisho (mfano: F-101):"
        else:
            response = "END Invalid choice. / Chaguo batili."
            
    elif len(parts) == 2:
        lang = parts[0]
        national_id = parts[1].upper()
        
        #  PUSH TO QUEUE
        pending_applications.append({
            "farmer_id": national_id,
            "phone": phoneNumber,
            "language": "en" if lang == "1" else "sw",
            "status": "Awaiting Review",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        if lang == "1":
            response = f"END Thank you. Your application for ID {national_id} is queued for review by the Loan Officer. You will receive an SMS shortly."
        else:
            response = f"END Asante. Ombi lako la kitambulisho {national_id} linasubiri ukaguzi na Afisa. Utapokea SMS hivi punde."
    else:
        response = "END Invalid Input."

    return response

@app.get("/api/pending_loans")
async def get_pending_loans():
    """Lovable UI hits this endpoint every 3 seconds to update the live sidebar."""
    return {"pending": pending_applications}

@app.post("/api/evaluate")
async def evaluate_farmer(payload: EvaluationRequest):
    """Triggered when the Loan Officer clicks a pending application in Lovable."""
    raw_graph_data = fetch_graph_context(payload.farmer_id)
    flattened_text = flatten_graph_context(raw_graph_data)
    llm_verdict = request_llm_verdict(flattened_text)
    
    return {
        "farmerId": payload.farmer_id,
        "name": raw_graph_data["name"],
        "creditScore": raw_graph_data["creditScore"],
        "aiMetrics": {
            "pageRankTrustScore": raw_graph_data["trust_pagerank"],
            "degreeCentralityFootprint": raw_graph_data["transaction_degree"],
            "louvainRiskCommunityId": raw_graph_data["louvain_repayment_cluster"],
            "knnSimilarEstablishedPeers": raw_graph_data["similarPeers"]
        },
        "traditionalMetrics": {
            "simCardAgeDays": raw_graph_data["simAgeDays"]
        },
        "environmentalRisk": raw_graph_data["environmental_risk"],
        "evaluation": llm_verdict
    }

@app.post("/api/approve")
async def approve_loan(payload: ApprovalRequest, background_tasks: BackgroundTasks):
    """Triggered when the Loan Officer clicks 'Approve' in the Lovable UI."""
    app_record = next((app for app in pending_applications if app["farmer_id"] == payload.farmer_id.upper()), None)
    
    if not app_record:
        raise HTTPException(status_code=404, detail="Farmer not found in queue.")
        
    # Mark as approved in the live queue
    app_record["status"] = "Approved"
    
    # We need to know which agrovet to route them to
    raw_graph_data = fetch_graph_context(payload.farmer_id)
    agrovet_name = raw_graph_data.get("agrovet_name", "your local supplier")
    
    # Fire the SMS autonomously in the background!
    background_tasks.add_task(
        execute_approval_sms, 
        app_record["phone"], 
        payload.farmer_id, 
        app_record["language"], 
        agrovet_name
    )
    
    return {"status": "success", "message": f"Loan for {payload.farmer_id} approved. Dispatching SMS."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)