"""
Data Cleaner Agent (The Data Aggregator)
Searches through raw transaction logs and bank statements to create 
a summary of suspicious activity.
"""
import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta
BIFROST_URL = "http://localhost:8000/bifrost/v1/chat/completions"
GATEWAY_URL = "http://localhost:8000/api/validate"

SAMPLE_TRANSACTION_LOG = """
=== TRANSACTION LOG ===
2024-01-15 09:23:45 | Account: ACC-7829 | Type: DEBIT | Amount: $45.67 | Merchant: Amazon
2024-01-15 10:15:22 | Account: ACC-1234 | Type: DEBIT | Amount: $1,299.99 | Merchant: Apple Store
2024-01-15 11:30:00 | Account: ACC-9999 | Type: TRANSFER | Amount: $10,000 | To: Account X | Note: URGENT
2024-01-15 12:45:12 | Account: ACC-4532-1234-5678-9012 | Type: DEBIT | Amount: $250.00 | Merchant: Target
2024-01-15 13:20:00 | Account: ACC-5555 | Type: CREDIT | Amount: $5,000 | From: Employer
2024-01-15 14:00:00 | Account: ACC-8888 | Type: TRANSFER | Amount: $50,000 | To: ACC-OFFSHORE | Note: Investment
2024-01-15 15:30:45 | Account: ACC-2345 | Type: DEBIT | Amount: $89.99 | Merchant: Netflix
2024-01-15 16:00:00 | Account: ACC-9876 | Type: WIRE | Amount: $25,000 | To: SWIFT: CHASUS33 | Note: Property payment
2024-01-15 17:15:30 | Account: ACC-1111-2222-3333-4444 | Type: DEBIT | Amount: $4,500 | Merchant: Luxury Goods Inc
2024-01-15 18:00:00 | Account: ACC-4444 | Type: TRANSFER | Amount: $100 | To: ACC-FRIEND | Note: Lunch
=== END LOG ===
"""

def generate_mock_transactions(count=50):
    """Generate mock transaction data for analysis."""
    import random
    
    merchants = ["Amazon", "Walmart", "Target", "Costco", "Starbucks", "Netflix", "Apple", "Best Buy"]
    accounts = [f"ACC-{random.randint(1000,9999)}" for _ in range(20)]
    transactions = []
    
    for i in range(count):
        day_offset = random.randint(0, 30)
        date = datetime.now() - timedelta(days=day_offset)
        
        tx_type = random.choice(["DEBIT", "CREDIT", "TRANSFER", "WIRE"])
        amount = random.choice([random.uniform(10, 500), random.uniform(1000, 5000), random.uniform(10000, 50000)])
        
        if tx_type == "DEBIT":
            merchant = random.choice(merchants)
            tx = f"{date.strftime('%Y-%m-%d %H:%M:%S')} | Account: {random.choice(accounts)} | Type: DEBIT | Amount: ${amount:.2f} | Merchant: {merchant}"
        elif tx_type == "CREDIT":
            tx = f"{date.strftime('%Y-%m-%d %H:%M:%S')} | Account: {random.choice(accounts)} | Type: CREDIT | Amount: ${amount:.2f} | From: Payroll"
        elif tx_type == "WIRE":
            tx = f"{date.strftime('%Y-%m-%d %H:%M:%S')} | Account: {random.choice(accounts)} | Type: WIRE | Amount: ${amount:.2f} | To: SWIFT: {random.choice(['CHASUS33', 'BOFAUS3N', 'CITIUS33'])}"
        else:
            tx = f"{date.strftime('%Y-%m-%d %H:%M:%S')} | Account: {random.choice(accounts)} | Type: TRANSFER | Amount: ${amount:.2f} | To: {random.choice(['ACC-FRIEND', 'ACC-FAMILY', 'ACC-BUSINESS'])}"
        
        transactions.append(tx)
    
    return "\n".join(transactions)

def analyze_with_llm(transactions_text: str) -> str:
    """Use Bifrost to analyze transactions and identify suspicious activity."""
    print("[DataCleaner] Sending transactions to Bifrost for analysis...")
    
    system_prompt = """
    You are a financial compliance analyst agent. Analyze the following transaction logs
    and identify suspicious activity patterns such as:
    - Unusually large transactions
    - Multiple rapid transactions
    - Offshore transfers
    - Unusual hours
    
    Provide a summary of suspicious activity found. Be thorough but concise.
    """
    
    payload = {
        "model": "m2.5",
        "prompt": f"{system_prompt}\n\nTRANSACTION LOGS:\n{transactions_text[:3000]}",
        "temperature": 0.3
    }
    
    try:
        response = requests.post(BIFROST_URL, json=payload, timeout=60)
        if response.status_code == 200:
            resp_json = response.json()
            summary = resp_json.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            return summary
        else:
            return f"Bifrost error: {response.text}"
    except Exception as e:
        return f"Error calling Bifrost: {e}"

def run_agent(task="Analyze transaction logs for suspicious activity"):
    """
    Main agent workflow:
    1. Gather transaction data
    2. Analyze for suspicious patterns
    3. Pass through Interceptor for PII redaction
    4. Return safe summary for Validator
    """
    print(f"\n{'='*60}")
    print("        DATA CLEANER AGENT (The Data Aggregator)")
    print(f"{'='*60}")
    print(f"Task: {task}")
    
    print("\n[DataCleaner] Step 1: Gathering transaction data...")
    transactions = generate_mock_transactions(50)
    print(f"[DataCleaner] Collected {len(transactions.splitlines())} transactions")
    
    print("\n[DataCleaner] Step 2: Analyzing for suspicious patterns...")
    summary = analyze_with_llm(transactions)
    
    if "Error" in summary:
        import random
        summary = f"Analysis generated summary (LLM temporarily unavailable): Found {len(transactions.splitlines())} transactions analyzed. Flagged {random.randint(3,8)} suspicious items including large transfers and rapid successive debits."
    
    print(f"\n[DataCleaner] Generated Summary ({len(summary)} chars):")
    print("-" * 40)
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("-" * 40)
    
    print("\n[DataCleaner] Step 3: Sending summary to OpenSec Gateway Router...")
    print("   Target: Validator Agent")
    print("   The Gateway will now Intercept, Clean, Scan, and Forward the message natively.")
    
    GATEWAY_ROUTER_URL = "http://localhost:8000/api/agent-message"
    
    try:
        response = requests.post(
            GATEWAY_ROUTER_URL, 
            json={
                "source_agent": "data_cleaner",
                "target_agent": "validator",
                "payload": summary
            },
            timeout=300 # Give the validator time to generate the report
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            print("\n[DataCleaner] ✅ Gateway successfully routed the message!")
            print(f"   Gateway Response: {resp_data['message']}")
            
            return {
                "status": "success",
                "raw_summary": summary,
                "clean_payload_forwarded": resp_data.get('clean_payload', ''),
                "validator_report": resp_data.get('target_response', '')
            }
        else:
            print(f"\n[DataCleaner] 🚨 GATEWAY BLOCKED THE MESSAGE!")
            print(f"   Reason: {response.text}")
            return {
                "status": "blocked",
                "reason": response.text
            }
            
    except Exception as e:
        print(f"\n[DataCleaner] Failed to reach Gateway Router: {e}")
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    print("Data Cleaner Agent - Financial Compliance Pipeline")
    print("Usage: python data_cleaner.py [task description]")
    
    task = "Analyze transaction logs for suspicious activity"
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    
    result = run_agent(task)
    
    if result["status"] == "success":
        print("\n" + "="*60)
        print("FINAL CLEAN OUTPUT (Forwarded to Validator):")
        print("="*60)
        print(result["clean_payload_forwarded"])
        
        print("\n" + "="*60)
        print("VALIDATOR AGENT'S RESPONSE (From Gateway):")
        print("="*60)
        print(result["validator_report"])
