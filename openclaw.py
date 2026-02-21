import requests
import json
import os
import sys

# Bifrost Gateway provides OpenAI-compatible unified routing
BIFROST_URL = "http://localhost:8000/bifrost/v1/chat/completions"
# OpenSec Gateway validation endpoint
GATEWAY_URL = "http://localhost:8000/api/validate"

def read_local_file(filepath):
    """
    The actual tool the agent uses to read a local file.
    """
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def ask_gateway(prompt):
    """
    Asks the OpenSec Gateway if an action is allowed.
    """
    print(f"[OpenClaw] Asking Gateway for permission: '{prompt}'")
    try:
        response = requests.post(GATEWAY_URL, json={"prompt": prompt}, timeout=60)
        if response.status_code == 200:
            print("[OpenClaw] Gateway says: ALLOWED ✅")
            return True
        else:
            print(f"[OpenClaw] Gateway says: BLOCKED 🛑 (Reason: {response.json().get('detail')})")
            return False
    except Exception as e:
        print(f"[OpenClaw] Could not reach Gateway: {e}")
        return False

def run_agent(task):
    """
    Simulated agent loop using Bifrost via LiteLLM routing.
    """
    print(f"\n--- Starting OpenClaw Agent ---")
    print(f"Task: {task}")
    
    # 1. Ask Bifrost what to do
    system_prompt = """
    You are OpenClaw, an autonomous agent. 
    You have ONE tool: `read_local_file(filepath)`.
    If the user asks you to read or summarize a file, you should output EXACTLY the filepath they want to read, and nothing else.
    If they ask anything else, say "I can only read files."
    """
    
    payload = {
        "model": "glm-5:cloud", # Bifrost handles mapping this
        "prompt": f"{system_prompt}\nUser request: {task}",
        "temperature": 0.7
    }
    
    print("[OpenClaw] Routing thought process through Bifrost Gateway...")
    try:
        response = requests.post(BIFROST_URL, json=payload, timeout=30)
        resp_json = response.json()
        action = resp_json.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        if not action:
            raise ValueError(f"Empty or malformed response from Bifrost: {resp_json}")
    except Exception as e:
        print(f"[OpenClaw] Failed to speak to local Ollama brain: {e}")
        # fallback to basic parsing if ollama isn't loaded with llama3
        import re
        match = re.search(r'([\w/.-]+\.\w+)', task)
        action = match.group(1) if match else (task.split()[-1] if task else "")
        print(f"[OpenClaw] Fallback parsing extracted filepath: {action}")
    
    if "I can only read" in action:
        print(f"[OpenClaw] {action}")
        return
        
    filepath_to_read = action

    # 2. OpenSec Gateway Interception!
    # Before the agent runs the dangerous read_local_file tool, it MUST clear the firewall
    gateway_prompt = f"read file {filepath_to_read}"
    is_allowed = ask_gateway(gateway_prompt)
    
    if not is_allowed:
        print("[OpenClaw] Aborting task due to security block.")
        return
        
    # 3. Execution (The agent safely reads the file)
    print(f"[OpenClaw] Executing read_local_file('{filepath_to_read}')...")
    content = read_local_file(filepath_to_read)
    
    print(f"\n[OpenClaw] File Content Header (First 100 chars):")
    print("-" * 40)
    print(content[:100] + ("..." if len(content) > 100 else ""))
    print("-" * 40)
    
if __name__ == "__main__":
    print("OpenClaw Local File Agent")
    # Interactive mode
    if len(sys.argv) > 1:
        run_agent(" ".join(sys.argv[1:]))
    else:
        while True:
            cmd = input("\nEnter prompt for OpenClaw (or 'quit'): ")
            if cmd.lower() in ['quit', 'exit']:
                break
            run_agent(cmd)
