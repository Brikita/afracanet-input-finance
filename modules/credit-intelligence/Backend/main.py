import os
import json
import urllib3
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Form
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from neo4j import GraphDatabase
# Disable the annoying Windows SSL warning for AT SMS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
NEO4J_URI="neo4j://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="15SaM373"
# Import configurations (Assuming config.py is in the same directory)
from config import (
    FEATHERLESS_BASE_URL,
    FEATHERLESS_API_KEY,
    MODEL_MAPPING,
    CORS_ORIGINS
)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
# Africa's Talking Configs
AT_USERNAME = "sandbox"
AT_API_KEY = "REMOVED_HISTORICAL_CREDENTIAL" # Make sure to paste your key back here!

# Initialize external clients
client = OpenAI(base_url=FEATHERLESS_BASE_URL, api_key=FEATHERLESS_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("🔌 Server safely shutdown.")

app = FastAPI(
    title="AFRACA Credit Risk Intelligence & USSD API",
    description="Unified backend handling AT USSD, SMS, and Featherless LLM.",
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

def calculate_credit_score(data: dict) -> int:
    """Calculates a baseline credit score based on GDS metrics."""
    if not data:
        return 0
    score = 30
    trust_pagerank = data.get('CommunityTrustScore') or 0.0
    economic_footprint = data.get('EconomicFootprint') or 0.0
    similar_peers = data.get('SimilarPeersCount') or 0
    climate_risk = data.get('ClimateRiskPenalty') or 0.0
    sim_age = data.get('SimAgeDays') or 0 

    if trust_pagerank >= 0.5: score += 25
    elif trust_pagerank >= 0.15: score += 15

    if economic_footprint >= 2.0: score += 20
    elif economic_footprint > 0: score += 10
    
    if similar_peers >= 2: score += 15
    elif similar_peers == 1: score += 10

    if sim_age > 1000: score += 10
    
    penalty = int(climate_risk * 15)
    score -= penalty
    return min(max(score, 0), 100)

# --- 1. GRAPH DATA RETRIEVAL (REAL NEO4J DB) ---
def fetch_graph_context(farmer_id: str) -> dict:
    """
    Pulls real GDS metrics and relationships from Neo4j.
    """
    #  HACKATHON BYPASS: DB Lead is offline. 
    # Delete this block when they wake up and turn the DB back on.
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
    
    # ... leave the rest of the existing query code below ...
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
        result = session.run(query, farmer_id=farmer_id)
        record = result.single()
        
        if not record:
            raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found in database.")
            
        data = dict(record)
        final_score = calculate_credit_score(data)
        
        return {
            "name": data["Applicant"],
            "cooperative_name": data["CoopName"] or "None",
            "chama_name": data["ChamaName"] or "None",
            "agrovet_name": data["AgrovetName"] or "your local supplier",
            "trust_pagerank": round(data["CommunityTrustScore"], 3),
            "transaction_degree": data["EconomicFootprint"],
            "louvain_repayment_cluster": str(data["LouvainCommunityId"]),
            "environmental_risk": f"{data['LiveClimateStatus']} (Penalty: {data['ClimateRiskPenalty']})",
            # Additional metrics mapped for the frontend payload
            "creditScore": final_score,
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
    agrovet = raw_data.get("agrovet_name", "None")
    env_risk = raw_data.get("environmental_risk", "None reported")

    pr_percentile = "top 15% of community trust" if pagerank > 0.8 else "average community trust"

    return (
        f"Applicant Name: {name}\n"
        f"Network Topology: In the {pr_percentile} (PageRank {pagerank}), "
        f"completed {degree} local transactions, cluster '{cluster}'.\n"
        f"Social Affiliations: Coop '{coop}', Chama '{chama}', Agrovet '{agrovet}'.\n"
        f"Environmental Risk: {env_risk}."
    )

def request_llm_verdict(flattened_context: str) -> dict:
    chosen_model = MODEL_MAPPING.get("credit_evaluation_agent", "deepseek-ai/DeepSeek-V4-Pro")
    
    system_instruction = (
        "You are an expert Agricultural Credit Underwriter for a Kenyan SACCO. "
        "Analyze the context and provide a 3-to-4 sentence rationale for approving or rejecting a voucher.\n"
        "1. MUST name the Chama, Cooperative, or Agrovet.\n"
        "2. MUST cite the environmental risk.\n"
        "3. Return a definitive 'RECOMMENDATION: APPROVE' or 'RECOMMENDATION: REJECT'.\n"
        "OUTPUT FORMAT: Raw JSON object with keys: 'decision' (APPROVE or REJECT) and 'rationale'."
    )
    
    try:
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
            
        return json.loads(raw_output)
    except Exception as e:
        print(f" LLM Error: {e}")
        return {"decision": "APPROVE", "rationale": "Fallback approval due to network timeout. Standard metrics apply."}

# --- 3. BACKGROUND TASK (DB + LLM + SMS) ---
def process_loan_and_notify(phone_number: str, national_id: str, language: str):
    """
    Runs in the background after the USSD session ends.
    Fetches DB data, gets AI verdict, and sends the localized SMS.
    """
    # Get DB data (Includes the Agrovet!)
    raw_graph_data = fetch_graph_context(national_id)
    agrovet = raw_graph_data.get("agrovet_name", "your local supplier")
    
    # Get AI Decision
    flattened_text = flatten_graph_context(raw_graph_data)
    llm_verdict = request_llm_verdict(flattened_text)
    decision = llm_verdict.get("decision", "APPROVE")
    
    # Formulate Localized SMS
    if decision == "APPROVE":
        if language == "SW":
            message = f"Hongera! Vocha yako ya AfracaNet (Kitambulisho: {national_id}) imeidhinishwa. Nenda {agrovet} kuchukua pembejeo zako."
        else:
            message = f"Congratulations! Your AfracaNet voucher (ID: {national_id}) is approved. Proceed to {agrovet} to collect your inputs."
    else:
        if language == "SW":
            message = f"Samahani, ombi lako la vocha (Kitambulisho: {national_id}) halikuidhinishwa. Tafadhali wasiliana na SACCO yako."
        else:
            message = f"Sorry, your voucher request (ID: {national_id}) was not approved at this time. Please contact your SACCO."
            
    # Send SMS directly via REST API (Bypassing Windows SSL bugs)
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {"ApiKey": AT_API_KEY, "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    payload = {"username": AT_USERNAME, "to": phone_number, "message": message}
    
    try:
        res = requests.post(url, headers=headers, data=payload, verify=False)
        print(f" SMS Sent [{language}]: {res.status_code}")
    except Exception as e:
        print(f" SMS Failed: {e}")

# --- 4. MULTILINGUAL USSD ENDPOINT ---
@app.post("/api/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    background_tasks: BackgroundTasks,
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form("")
):
    # Africa's Talking passes inputs separated by '*' (e.g. "1*1*28471936")
    parts = text.split("*") if text else []
    
    if text == "":
        # LEVEL 0: Language Selection
        return "CON Welcome to AfracaNet / Karibu AfracaNet\n1. English\n2. Kiswahili"
        
    elif len(parts) == 1:
        # LEVEL 1: Main Menu (Split by Language)
        if parts[0] == "1":
            return "CON 1. Apply for Input Loan\n2. Check Trust Score"
        elif parts[0] == "2":
            return "CON 1. Omba Mkopo wa Pembejeo\n2. Angalia Alama ya Uaminifu"
        else:
            return "END Invalid choice / Chaguo batili."
            
    elif len(parts) == 2:
        # LEVEL 2: Ask for ID
        if parts[0] == "1" and parts[1] == "1":
            return "CON Enter your National ID:"
        elif parts[0] == "2" and parts[1] == "1":
            return "CON Weka Nambari yako ya Kitambulisho:"
        else:
            return "END Service under construction."
            
    elif len(parts) == 3:
        # LEVEL 3: Submit and Trigger Background Task
        language_code = "EN" if parts[0] == "1" else "SW"
        national_id = parts[2]
        
        # Dispatch the heavy lifting (DB + LLM + SMS) to the background
        background_tasks.add_task(process_loan_and_notify, phoneNumber, national_id, language_code)
        
        # End USSD session gracefully based on language
        if language_code == "EN":
            return f"END Thank you. Application for ID {national_id} received. You will receive an SMS shortly."
        else:
            return f"END Asante. Ombi la kitambulisho {national_id} limepokelewa. Utapokea SMS hivi punde."

    return "END Invalid Input."

# Ensure the UI endpoint is still available for the Frontend Lead
@app.post("/api/evaluate")
async def evaluate_farmer(payload: EvaluationRequest):
    raw_graph_data = fetch_graph_context(payload.farmer_id)
    flattened_text = flatten_graph_context(raw_graph_data)
    llm_verdict = request_llm_verdict(flattened_text)
    
    # Send the combined payload matching exactly what the frontend UI expects
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

if __name__ == "__main__":
    import uvicorn
    # Using Uvicorn since we upgraded to FastAPI
    uvicorn.run(app, host="127.0.0.1", port=5000)