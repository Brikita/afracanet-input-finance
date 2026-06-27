# Cognitive Underwriter: Featherless LLM Integration Documentation

This document provides a comprehensive breakdown of the AI underwriting engine engineered for the AFRACA Hackathon. It serves as both a technical guide for team alignment and an evaluation framework for the judging panel to review our implementation of **GraphRAG-driven Cognitive Underwriting**.

---

## 1. Executive Overview

Traditional agricultural credit underwriting relies on backward-looking, flat ledgers that systematically exclude smallholder farmers (women, youth, and persons with disabilities) who lack formal collateral.

Our system solves this "thin-file" issue by using **Graph Data Science (GDS)** network topology metrics computed in Neo4j, combined with a highly deterministic **Cognitive Underwriting Engine** powered by the **Featherless LLM API**. Instead of acting as a creative chatbot, the LLM operates as a strict, risk-averse financial credit officer capable of translating mathematical graph data into plain-English credit risk summaries and structural lending decisions.

---

## 2. Core Operational Philosophy

The implementation strictly enforces a 3-step cognitive pipeline to transform complex network data into structured frontend components:

1. **The Context Injector (Data Flattening):** LLMs struggle to read multi-level, nested JSON data structures natively without hallucinating or misinterpreting weights. The Python backend intercepts the raw database graph metrics and flattens them into an analytical, narrative text block before sending them to the model.
2. **Deterministic Constraint Modeling:** The system prompt strips all "creativity" from the model by applying a `temperature` of `0.0`. It binds the model to strict rules of execution, forcing it to explicitly site localized entities (Chamas, Cooperatives) and environmental data points.
3. **Structured JSON Output Enforcement:** To prevent UI parsing errors, the model is strictly forbidden from returning raw Markdown blocks or conversation fillers. It must output a strict, un-wrapped JSON payload with predictable schema properties.

---

## 3. Data Flow Architecture

The backend establishes a seamless, asynchronous communication channel between the database, the intelligence engine, and the frontend web UI:

```
[Lovable Frontend UI] 
       │
       ▼ (Sends: Farmer ID)
[FastAPI Backend Router]
       │
       ├─► [Neo4j Database] ✨ Pulls PageRank, Louvain Cluster, Centrality Metrics
       │         │
       │         ▼ (Returns raw math scores)
       ├─► [Context Injector] ✨ Translates math into narrative text block
       │         │
       │         ▼ (Sends flattened context)
       └─► [Featherless LLM API] ✨ Processes via DeepSeek Cognitive Underwriter
                 │
                 ▼ (Returns structured raw JSON object)
[Lovable Frontend UI] ✨ Renders Approval/Rejection & Rationale instantly

```

---

## 4. API Endpoint Specification

The backend server exposes a production-ready, CORS-enabled REST API gateway that maps directly to the Lovable UI requirements.

### **POST /api/evaluate**

Executes the full GraphRAG evaluation pipeline for a specified smallholder profile.

#### **Input Payload (JSON)**

Sent by the Lovable UI to initiate an underwriting evaluation.

```json
{
  "farmer_id": "F-999"
}

```

#### **Output Response Payload (JSON)**

Returned by the backend to fuel the frontend dashboard layout. It includes the raw metrics for data visualization alongside the natural language decision object.

```json
{
  "farmer_id": "F-999",
  "raw_graph_data": {
    "name": "Grace Omwamba",
    "cooperative_name": "Machakos Seed Cooperative",
    "chama_name": "Tumaini Women's Group",
    "trust_pagerank": 0.85,
    "transaction_degree": 12,
    "louvain_repayment_cluster": "High-Performing",
    "environmental_risk": "Mild Drought in Machakos"
  },
  "evaluation": {
    "decision": "APPROVE",
    "rationale": "Grace Omwamba is approved for an agricultural input voucher. She demonstrates exceptionally high social collateral, placing in the top 15% of community trust via PageRank (0.85) and maintaining strong ties with the Tumaini Women's Group. Despite a localized risk of Mild Drought in Machakos, her consistent transaction velocity (12 transactions) and membership in a high-performing Louvain repayment cluster within the Machakos Seed Cooperative mitigate overall default risks."
  }
}

```

---

## 5. Intelligence Layer Prompt Engineering

The system configuration uses a master template designed specifically to handle alternative underwriting risk.

### **System Role & Persona**

```text
You are an expert Agricultural Credit Underwriter for a Kenyan SACCO. Your job is to analyze alternative graph-data metrics and provide a 3-to-4 sentence rationale for approving or rejecting an agricultural input voucher.

```

### **Rules of Execution**

1. **Explainable Citations:** You MUST explicitly name the specific Chama, Cooperative, or Agrovet the farmer is connected to (to guarantee absolute explainability for audit purposes).
2. **Context Anchoring:** You MUST cite the environmental risk (e.g., regional climate/drought exposure indices) provided in the context.
3. **No Hallucinations:** Do not invent data. If a metric is missing, assess based entirely on available social and network collateral.
4. **Binary Conclusion:** Conclude with a definitive `RECOMMENDATION: APPROVE` or `RECOMMENDATION: REJECT` based on whether the overall network metrics skew positive.

### **Output Format Constraints**

```text
You must return your response as a raw JSON object with exactly two keys. DO NOT wrap the output in Markdown blocks (like ```json). Just the raw object.
{"decision": "APPROVE" | "REJECT", "rationale": "Your explanation here."}

```

---

## 6. Model Selection Strategy

Our architecture abstracts model selection using a centralized configuration file (`config.py`). We utilize premium foundational endpoints hosted via **Featherless.ai**, prioritizing models with exceptional multi-lingual comprehension and strict constraint-following capabilities.

* **Primary Evaluation Model:** DeepSeek-based architecture (`MODEL_MAPPING["credit_evaluation_agent"]`).
* **Justification:** Chosen for its industry-leading reasoning benchmarks, high density of parameter logic for extracting data patterns, and its precise execution of JSON formatting rules under a `0.0` temperature setting, eliminating erratic behavior or variable keys during high-concurrency API calls.