import os
from openai import OpenAI
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

# 1. Initialize Featherless Client (OpenAI-compatible)
featherless_client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY")
)

# 2. Initialize Neo4j Driver
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def fetch_dummy_farmer_data(farmer_id):
    """
    Simulates querying your dummy database for alternative metrics.
    Adjust the Cypher query below to match your dummy schema.
    """
    query = """
    MATCH (f:Farmer {id: $farmer_id})
    OPTIONAL MATCH (f)-[:USES]->(m:MobileMoney)
    OPTIONAL MATCH (f)-[:MEMBER_OF]->(c:Cooperative)
    RETURN f.name AS name, 
           m.consistency_score AS mobile_score, 
           c.repayment_status AS coop_status
    """
    with neo4j_driver.session() as session:
        result = session.run(query, farmer_id=farmer_id)
        record = result.single()
        if record:
            return dict(record)
        return {"name": "Unknown", "mobile_score": 0.45, "coop_status": "No history"}

def evaluate_creditworthiness(farmer_context):
    """
    Sends data to Featherless using DeepSeek for the final financial decision.
    """
    # Replace model name string with the specific variant listed in your Featherless dashboard
    # e.g., "deepseek-ai/DeepSeek-V4-Pro"
    model_name = "deepseek-ai/DeepSeek-V4-Pro" 
    
    prompt = f"""
    You are an advanced credit risk intelligence system built for rural loan officers.
    Analyze the following alternative data retrieved from our Neo4j knowledge graph:
    
    - Farmer Name: {farmer_context.get('name')}
    - Mobile Money Consistency Score: {farmer_context.get('mobile_score')} (Scale 0-1)
    - Cooperative Repayment Record: {farmer_context.get('coop_status')}
    
    Provide a concise assessment stating if this farmer is Creditworthy or Not Creditworthy.
    Justify your answer in 3 actionable bullet points designed for a rural loan officer.
    """

    response = featherless_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a pragmatic, risk-aware agricultural microfinance expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2 # Lower temperature for analytical reliability
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    try:
        print("⚡ Fetching dummy data from Neo4j...")
        # Replace 'F-101' with a real ID existing in your dummy DB, or rely on our fallback values
        context = fetch_dummy_farmer_data("F-101")
        print(f"📊 Retrieved context data: {context}")
        
        print("\n🤖 Sending payload to Featherless LLM...")
        verdict = evaluate_creditworthiness(context)
        
        print("\n=== LOAN OFFICER REPORT ===")
        print(verdict)
        print("===========================")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
    finally:
        neo4j_driver.close()