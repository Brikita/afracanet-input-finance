# AfracaNet: Agentic Alternative Credit-Scoring Portal

## Project Overview

AfracaNet is a decentralized, agentic credit-scoring platform developed for the AFRACA challenge. It provides an alternative underwriting system for agricultural SACCOs by leveraging Graph Data Science (GDS) to evaluate a farmer's social and economic collateral rather than traditional credit scores.

The system integrates a bilingual USSD interface for field applications, a highly deterministic LLM for credit evaluation, and a React-based command center for loan officers.

## System Architecture

- **Frontend (Command Center):** A React/Tailwind dashboard built for loan officers to monitor live queues and review AI-generated underwriting rationales.
- **Backend (API Gateway):** A FastAPI orchestrator that handles USSD sessions, manages an in-memory application queue, and routes data between the database and the LLM.
- **Graph Database:** Neo4j running Graph Data Science algorithms (PageRank, Louvain, Degree Centrality, Node Similarity) alongside live Open-Meteo climate risk data.
- **Cognitive Underwriter:** Featherless AI models configured to parse raw graph metrics into actionable underwriting logic and anti-gaming (Goodhart's Law safe) SMS tips.
- **Telecom Gateway:** Africa's Talking API for USSD menus and localized (English/Swahili) SMS dispatch.

## File Structure

```
AFRACANET-GREEN-PATH/
├── Backend/
│   ├── __pycache__/
│   ├── assets/
│   ├── app.py                 # Legacy DB Lead Flask application (Microservice target)
│   ├── at.py                  # Initial Africa's Talking routing scripts
│   ├── config.py              # Environment variables and API keys
│   ├── databaseSeed.py        # Neo4j initialization, data seeding, and GDS algorithms
│   ├── main.py                # Master FastAPI orchestrator (Queue, USSD, LLM endpoints)
│   ├── nul                    # Windows null device artifact
│   ├── README.md
│   └── requirements.txt       # Python dependencies (fastapi, uvicorn, neo4j, etc.)
├── Featherless_LLM/
│   ├── __pycache__/
│   ├── .vscode/
│   ├── config.py              # Model mapping and LLM configurations
│   ├── list_models.py         # Utility to query available Featherless models
│   ├── main.py                # Initial LLM integration drafts
│   ├── main2.py
│   ├── Readme.md
│   └── test_llm_graph.py      # Scripts for flattening Graph JSON for deterministic prompts
├── node_modules/              # Local frontend dependencies
└── src/                       # React Frontend (Command Center Dashboard)
    ├── components/            # UI components (Sidebar, OverviewQueue, Data Cards)
    ├── hooks/                 # React hooks (Live API polling logic)
    └── lib/                   # Utility functions and API configurations
```

## Running the Platform Locally

### 1. Start the Backend Orchestrator

Ensure your `.env` variables are configured. Navigate to the `Backend` directory, activate your virtual environment, and start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

### 2. Establish the Telecom Tunnel

Expose the local backend to the Africa's Talking webhook using Ngrok:

```bash
ngrok http 8000
```

Update the Africa's Talking dashboard callback URL to match the generated Ngrok address, appending `/api/ussd`.

### 3. Launch the Command Center

Navigate to the root directory and start the Vite development server to launch the React frontend:

```bash
npm run dev
```

Access the dashboard via the localhost URL provided in the terminal to monitor the live queue and evaluate incoming USSD applications.
