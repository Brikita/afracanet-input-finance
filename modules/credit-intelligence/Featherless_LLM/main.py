import os
from openai import OpenAI
from neo4j import GraphDatabase
# Import our clean configurations
from config import (
    FEATHERLESS_BASE_URL,
    FEATHERLESS_API_KEY,
    MODEL_MAPPING,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
)

# 1. Initialize the Featherless Client safely
# It will automatically error out immediately if FEATHERLESS_API_KEY is missing
if not FEATHERLESS_API_KEY:
    raise ValueError("❌ CRITICAL ERROR: FEATHERLESS_API_KEY is missing from your environment variables!")

client = OpenAI(
    base_url=FEATHERLESS_BASE_URL,
    api_key=FEATHERLESS_API_KEY
)

# 2. Initialize the Neo4j Driver using decoupled individual variables
if not NEO4J_PASSWORD:
    raise ValueError("❌ CRITICAL ERROR: NEO4J_PASSWORD is not set. Cannot establish a safe database connection.")

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def fetch_farmer_graph_context(farmer_id):
    """
    GraphRAG Step 1: Query Neo4j to pull alternative risk indicators.
    NOTE: Change node labels (e.g., :Farmer, :Cooperative) to match your dummy database.
    """
    cypher_query = """
    MATCH (f:Farmer {id: $farmer_id})
    OPTIONAL MATCH (f)-[:MEMBER_OF]->(c:Cooperative)
    OPTIONAL MATCH (f)-[:TRANSACTS_WITH]->(m:MobileMoneyWallet)
    RETURN f.name AS name,
           f.demographic_category AS demographic, 
           c.repayment_history AS coop_history,
           m.transaction_consistency AS mobile_consistency
    """
    
    try:
        with neo4j_driver.session() as session:
            result = session.run(cypher_query, farmer_id=farmer_id)
            record = result.single()
            
            if record:
                return dict(record)
            
            # Fallback mock context if your dummy DB doesn't have this specific ID yet
            print(f"⚠️ Farmer ID '{farmer_id}' not found. Using fallback dummy profile for layout validation.")
            return {
                "name": "Grace Omwamba",
                "demographic": "Female / Youth",
                "coop_history": "Consistent 12-month on-time repayment for seed inputs",
                "mobile_consistency": 0.88
            }
    except Exception as e:
        print(f"⚠️ Neo4j Query failed ({e}). Using safety fallback data.")
        return {
            "name": "Grace Omwamba (Fallback)",
            "demographic": "Female / Youth",
            "coop_history": "Consistent 12-month on-time repayment for seed inputs",
            "mobile_consistency": 0.88
        }


def run_credit_evaluation_agent(farmer_context):
    """
    GraphRAG Step 2: Feed the graph context directly into our DeepSeek 
    Credit Evaluation Agent via Featherless.
    """
    # Pull model string dynamically from our centralized config map
    chosen_model = MODEL_MAPPING["credit_evaluation_agent"]
    print(f"🤖 Activating Credit Evaluation Agent via Featherless using: {chosen_model}")

    system_instruction = (
        "You are an expert microfinance credit risk intelligence engine specializing "
        "in sub-Saharan African agriculture. Your role is to evaluate alternative data "
        "to empower marginalized farmers (women, youth, persons with disabilities) who "
        "lack traditional collateral, while strictly managing risk for rural banks."
    )

    prompt = f"""
    Analyze the following alternative data retrieved from our Neo4j Knowledge Graph:
    
    - Farmer Name: {farmer_context.get('name')}
    - Demographic Category: {farmer_context.get('demographic')}
    - Mobile Money Transaction Consistency: {farmer_context.get('mobile_consistency')} (Scale: 0.0 to 1.0)
    - Cooperative Lending History: {farmer_context.get('coop_history')}
    
    Provide your decision in this exact layout for the rural loan officer:
    
    ### [CREDITWORTHY / NOT CREDITWORTHY]
    
    **Risk Profile Overview:**
    (Provide a 2-sentence summary of why they fit this category, highlighting how alternative data overrides traditional missing land-title collateral if applicable).
    
    **Key Strengths (Graph Signals):**
    - Bullet point 1
    - Bullet point 2
    
    **Suggested Loan Terms:**
    - Maximum Recommended Principal: (e.g., $200 USD equivalent in local currency)
    - Structural Advice: (e.g., align repayment with harvest cycle)
    """

    response = client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1  # Low temperature ensures deterministic, highly analytical logic
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    print("🌾 Starting AFRACA Credit Risk Intelligence Protocol...")
    
    # Target a dummy farmer ID
    target_farmer_id = "F-999" 
    
    # Step 1: Extract Graph Data
    print(f"🔍 GraphRAG: Fetching sub-graph context for ID: {target_farmer_id}...")
    context_data = fetch_farmer_graph_context(target_farmer_id)
    print(f"📊 Context Extracted: {context_data}\n")
    
    # Step 2: Render Decision through Featherless
    try:
        report = run_credit_evaluation_agent(context_data)
        print("==================================================")
        print("                 LOAN OFFICER REPORT              ")
        print("==================================================")
        print(report)
        print("==================================================")
    except Exception as e:
        print(f"❌ Featherless Inference Failed: {e}")
    finally:
        # Step 3: Always clean up connections safely
        neo4j_driver.close()
        print("\n🔌 Database connections safely closed. Process terminated.")