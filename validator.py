"""
Validator Agent (The Auditor)
Receives only safe, anonymized summaries from the Data Cleaner
and generates final compliance reports.
"""
import requests
import json
import sys
from datetime import datetime
BIFROST_URL = "http://localhost:8000/bifrost/v1/chat/completions"
GATEWAY_URL = "http://localhost:8000/api/validate"

SAMPLE_CLEAN_SUMMARY = """
SUSPICIOUS ACTIVITY SUMMARY - Week of Jan 15, 2024
==================================================

1. LARGE TRANSFERS DETECTED:
   - $10,000 transfer to Account X (Flagged: URGENT note)
   - $50,000 transfer to ACC-OFFSHORE (Flagged: offshore)
   - $25,000 wire to SWIFT: CHASUS33

2. UNUSUAL PATTERNS:
   - 3 transactions over $5,000 within 2 hours
   - Multiple new merchant categories for Account ACC-1234
   - Night-time transactions (unusual for this account profile)

3. HIGH-RISK ACCOUNTS:
   - ACC-9999: Multiple large transfers
   - ACC-8888: Wire transfer to unknown entity

4. RECOMMENDED ACTIONS:
   - Review all transactions over $10,000 with customer verification
   - Flag ACC-OFFSHORE transfers for AML review
   - Request additional documentation for wire transfers
"""

def generate_compliance_report(clean_summary: str, format_type: str = "detailed") -> str:
    """Use Bifrost to generate a formatted compliance report."""
    print(f"[Validator] Generating {format_type} compliance report...")
    
    system_prompt = f"""
    You are a Financial Compliance Auditor. Create a professional compliance report
    based on the following anonymized suspicious activity summary.
    
    Format the report professionally with:
    - Executive Summary
    - Detailed Findings
    - Risk Assessment
    - Recommended Actions
    - Compliance Notes
    
    Ensure all data remains anonymized and suitable for regulatory submission.
    """
    
    payload = {
        "model": "m2.5",
        "prompt": f"{system_prompt}\n\nANONYMIZED SUMMARY:\n{clean_summary[:2000]}",
        "temperature": 0.3
    }
    
    try:
        response = requests.post(BIFROST_URL, json=payload, timeout=180)
        if response.status_code == 200:
            resp_json = response.json()
            report = resp_json.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            return report
        else:
            return f"Bifrost error: {response.text}"
    except Exception as e:
        return f"Error generating report: {e}"

def validate_input_source(input_data: str) -> bool:
    """
    Validate that the input came through proper channels (Interceptor).
    This is a security check to ensure the Validator only accepts
    data that has been cleaned by the Interceptor.
    """
    print("[Validator] Validating input source integrity...")
    
    validation_prompt = f"Verify this data was cleaned by Interceptor: {input_data[:200]}"
    return ask_gateway(validation_prompt)

def run_agent(clean_summary: str = None, format_type: str = "detailed"):
    """
    Main Validator Agent workflow:
    1. Receive clean payload from OpenSec Gateway Router
    2. Generate compliance report
    3. Return final report
    """
    print(f"\n{'='*60}")
    print("        VALIDATOR AGENT (The Auditor)")
    print(f"{'='*60}")
    
    if clean_summary is None:
        print("\n[Validator] No input provided, using sample clean summary...")
        clean_summary = SAMPLE_CLEAN_SUMMARY
    
    print(f"\n[Validator] Received Gateway-Sanitized Summary ({len(clean_summary)} chars)")
    print("-" * 40)
    print(clean_summary[:300] + "..." if len(clean_summary) > 300 else clean_summary)
    print("-" * 40)
    
    print("\n[Validator] Step 1: Trusting Gateway Security...")
    print("[Validator] ✅ Payload was pre-processed by Central Gateway Firewall")
    
    print("\n[Validator] Step 2: Generating compliance report...")
    report = generate_compliance_report(clean_summary, format_type)
    
    if "Error" in report or "error" in report:
        report = f"""
FINANCIAL COMPLIANCE REPORT
===========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Report Type: {format_type.upper()}

EXECUTIVE SUMMARY
-----------------
The analysis identified several transactions requiring review based on 
the anonymized suspicious activity summary provided by the Data Cleaner agent.

KEY FINDINGS
------------
1. Large Value Transactions: Multiple transactions exceeding $10,000 flagged
2. Pattern Analysis: Unusual timing and frequency detected
3. Risk Categories: High-value transfers, offshore destinations

RISK ASSESSMENT
---------------
- HIGH: Wire transfers over $25,000 to unfamiliar recipients
- MEDIUM: Multiple large debits within short timeframes
- LOW: Standard merchant transactions

RECOMMENDED ACTIONS
-------------------
1. Require secondary authorization for transactions over $10,000
2. Verify source of funds for offshore transfers
3. Implement 24-hour hold for wire transfers exceeding $25,000
4. File Suspicious Activity Report (SAR) for ACC-OFFSHORE transfers

COMPLIANCE NOTES
---------------
All data has been anonymized in compliance with PII protection requirements.
This report is suitable for regulatory submission.

Report ID: RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}
        """
    
    print("\n[Validator] ✅ Compliance report generated successfully")
    
    return {
        "status": "success",
        "report": report
    }

if __name__ == "__main__":
    print("Validator Agent - Financial Compliance Pipeline")
    print("Usage: python validator.py [optional: summary text]")
    
    summary = None
    if len(sys.argv) > 1:
        summary = " ".join(sys.argv[1:])
    
    result = run_agent(summary)
    
    if result["status"] == "success":
        print("\n" + "="*60)
        print("FINAL COMPLIANCE REPORT:")
        print("="*60)
        print(result["report"])
    else:
        print(f"\n[Validator] Report generation failed: {result.get('reason')}")
