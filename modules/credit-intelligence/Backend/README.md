# **The Invisible Farmer \- Graph AI Credit Scoring Engine**

An alternative credit-scoring engine designed to assess the creditworthiness of unbanked Kenyan farmers. This project leverages a **Neo4j Graph Database**, the **Neo4j Graph Data Science (GDS) Library**, **Python (Flask)**, and the **Open-Meteo API** to calculate risk using Machine Learning algorithms on social collateral, production history, transaction velocity, and live environmental data.

## ** Features**

* **Graph-Based Risk Assessment:** Uses a Neo4j graph database to model complex relationships between Farmers, Chamas (savings groups), Agricultural Cooperatives, and AgriDealers.  
* **Graph AI & Machine Learning (GDS):** Replaces traditional banking metrics with advanced algorithmic scoring:  
  * **PageRank (Community Trust):** Solves the "thin-file" problem by allowing unbanked youth to inherit trust equity from established guarantors in their network.  
  * **Degree Centrality (Economic Footprint):** Mathematically proves cash-flow liquidity by tracking the density of M-Pesa transaction edges.  
  * **Louvain Modularity (Risk Clusters):** Automatically detects high-performing and high-risk lending communities based on cooperative interactions.  
  * **Node Similarity / KNN (Predictive Approval):** Identifies "look-alike" safe borrowers by comparing structural graph similarities.  
* **Live Climate Risk Integration:** Dynamically queries the live Open-Meteo API to adjust credit scores based on real-time soil moisture and drought risks in the farmer's region (e.g., Meru County, Machakos) to protect against systemic agricultural defaults.  
* **Defensive Scoring Algorithm:** A robust Flask API that processes these AI metrics and safely handles missing data fields to return a mathematical credit score out of 100\.

## **Tech Stack**

* **Database:** Neo4j (Graph Database) \+ Graph Data Science (GDS) Plugin  
* **Backend Framework:** Python / Flask  
* **External APIs:** Open-Meteo (Live Climate & Soil Data)  
* **Libraries:** neo4j, flask, flask-cors, requests

## ** Project Structure**

* databaseSeed.py: The database provisioning and AI script. It clears the local database, fetches live environmental data, seeds the graph, and **executes the automated GDS algorithms** (projecting the graph into RAM, mutating scores, and writing properties back to the nodes).  
* app.py: The Flask API backend. It connects to Neo4j, retrieves the AI-generated properties alongside traditional metrics, applies the custom credit-scoring algorithm, and serves the data to the frontend via JSON.

## **Setup & Installation**

### **1\. Prerequisites**

* Python 3.x installed  
* Neo4j Desktop installed (or a free Neo4j AuraDB cloud instance)  
* Neo4j Database running locally on port 7687

### **2\. Install the Neo4j GDS Plugin (Crucial\!)**

To run the AI algorithms, you must enable GDS in your database:

1. Open Neo4j Desktop.  
2. Click on your active database project.  
3. On the right-side panel, go to the **"Plugins"** tab.  
4. Find **Graph Data Science Library** and click **Install**.  
5. Restart your database.

### **3\. Install Python Dependencies**

Open your terminal and install the required packages:

pip install flask flask-cors neo4j requests

### **4\. Database Configuration**

In both databaseSeed.py and app.py, ensure your Neo4j credentials match your active instance:

NEO4J\_URI \= "bolt://localhost:7687"  
NEO4J\_USER \= "neo4j"  
NEO4J\_PASSWORD \= "YOUR\_ACTUAL\_PASSWORD\_HERE"

## **Running the Application**

### **Step 1: Seed the Database & Run the AI Pipeline**

Run the seeding script. This will populate the data, pull live weather, and run all 4 Machine Learning algorithms (PageRank, Louvain, Degree, KNN) on the network:

python databaseSeed.py

*You should see a success message indicating the data was seeded and the Graph AI metrics were written to the nodes.*

### **Step 2: Start the Flask API**

Run the backend server:

python app.py

*The server will start running on http://localhost:5000.*

## **API Documentation**

### **Get Farmer Credit Score**

Retrieves the complete graph AI analysis and calculated credit score for a specific farmer.

* **Endpoint:** /api/farmer/\<farmer\_id\>/score  
* **Method:** GET  
* **Available Test IDs:** F-101 (Amina), F-102 (Kiprono), F-103 (David)

**Example Request:**

curl http://localhost:5000/api/farmer/F-101/score

**Example Response:**

{  
  "aiMetrics": {  
    "degreeCentralityFootprint": 2.0,  
    "knnSimilarEstablishedPeers": 1,  
    "louvainRiskCommunityId": 0,  
    "pageRankTrustScore": 0.85  
  },  
  "creditScore": 95.0,  
  "environmentalRisk": {  
    "penaltyScore": 0.1,  
    "status": "Optimal Condition"  
  },  
  "farmerId": "F-101",  
  "name": "Amina Wanjiku",  
  "traditionalMetrics": {  
    "simCardAgeDays": 1200  
  }  
}  
