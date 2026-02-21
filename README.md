# OpenSec – AI Runtime Security Platform

OpenSec is a runtime security and governance platform that functions as an AI Security Gateway (or "Agent Firewall"). It sits between an autonomous agent (such as OpenClaw or Molt Bot) and external tools (LLMs, APIs, databases) to enforce strict control over agents that may operate with excessive privileges.

## Features

*   **Interception & Analysis**: Intercepts every request from the agent before execution to analyze input for prompt injection, secret extraction, or dangerous instructions using real LLM-based intelligence.
*   **Risk Scoring**: A multi-model detection layer assigns a deterministic risk score `[0.0 - 1.0]` to each prompt.
    *   *Prompt Injection & Secrets*: Secured by `llm-guard`.
    *   *AI Safety Layer*: Enforced by `llamafirewall`.
    *   *Advanced Brain*: Contextual intent parsing using an Ollama GLM-5 model.
*   **Identity & Permissions**: Assign unique identities and roles to restrict over-privileged behavior.
*   **Secure Execution**: Approved tasks are executed securely within isolated `e2b` sandboxes.
*   **Real-time Monitoring**: A beautiful dark-neon Streamlit dashboard provides live audit logs, displaying prompts, risk scores, tool usage, and real-time ALLOW/BLOCK responses.

## Architecture

*   **Backend API**: Built with **FastAPI** to act as the Bifrost gateway proxy and execute the security validation and E2B actions.
*   **Security Engines**: Leverages `llamafirewall`, `llm-guard`, and `Ollama` models. 
*   **Frontend Dashboard**: Built with **Streamlit** to consume live metrics and provide real-time visibility.

## Prerequisites

1.  **Python 3.12+**
2.  An **E2B API Key** for secure sandbox execution (if active, otherwise it falls back to a sandbox simulation).
3.  An **Ollama API Key** / Endpoint for the GLM-5 cloud integration.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Username/opensec-mvp.git
    cd opensec-mvp
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```bash
    E2B_API_KEY="your_e2b_api_key"
    OLLAMA_API_KEY="your_ollama_ssh_format_key"
    OLLAMA_ENDPOINT="http://localhost:11434/api/generate" # Optional, update for production
    MINIMAX_API_KEY="sk-cp-..." # Your Minimax API key for the m2.5 model 
    ```

## Running the Application

OpenSec requires two servers to run concurrently.

1.  **Start the Backend (FastAPI)**:
    ```bash
    # Ensures the .env file is loaded properly
    set -a; source .env; set +a; uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```

2.  **Start the Frontend Dashboard (Streamlit)**:
    ```bash
    # In a new terminal tab
    streamlit run frontend/app.py --server.port 8501 
    ```

## Demonstrating The Financial Compliance Pipeline 

You can execute standalone scripts to watch OpenSec govern multi-agent flows in real-time. Make sure both servers are running first.

### 1. Showcasing the Data Cleaner Agent (The Aggregator)
This agent gathers raw data, asks Bifrost's `m2.5` model to summarize suspicious activity, and then passes the summary through the strict OpenSec Firewall Interceptor to strip sensitive PII before letting it proceed.
    
    ```bash
    python3 data_cleaner.py
    ```

### 2. Showcasing the Validator Agent (The Auditor)
This agent acts as the final step in the pipeline. It takes the cleaned summary from the Data Cleaner, double-checks it against the gateway for safety, and then asks Bifrost's `m2.5` model to generate a formal compliance report.

    ```bash
    python3 validator.py
    ```

**Note on Bifrost Failover:** If your Minimax API key runs out of funds (e.g., throwing a `HTTP 429` error), the `BifrostGateway` will transparently catch the failure and re-route the agent's logic requests to your local Open-Source `glm-5:cloud` model! This prevents the agents from crashing in production environments when third-party downstream providers fail.
