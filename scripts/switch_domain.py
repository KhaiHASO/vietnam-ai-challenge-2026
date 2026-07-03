import os
import sys
import argparse
import requests

def switch_domain(domain: str):
    domain = domain.lower().strip()
    if domain not in ["sme", "education", "agriculture"]:
        print(f"Error: Invalid domain '{domain}'. Choose 'sme', 'education', or 'agriculture'.")
        sys.exit(1)
        
    print(f"\n[Switch Domain] Switching active workspace domain to: {domain.upper()}...")
    
    # 1. Update the .env file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    
    lines = []
    updated = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("ACTIVE_DOMAIN="):
                    lines.append(f"ACTIVE_DOMAIN={domain}\n")
                    updated = True
                else:
                    lines.append(line)
                    
    if not updated:
        lines.append(f"\nACTIVE_DOMAIN={domain}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"[Switch Domain] Updated .env file (ACTIVE_DOMAIN={domain}).")
    
    # 2. Try to notify running backend API
    try:
        url = "http://localhost:8000/api/domain/switch"
        response = requests.post(url, json={"domain": domain}, timeout=3)
        if response.status_code == 200:
            print("[Switch Domain] Running FastAPI backend notified. Live-reloaded database and vector DB.")
            print(response.json().get("message", ""))
        else:
            print(f"[Switch Domain] Failed to notify live backend (Status {response.status_code}).")
    except Exception:
        print("[Switch Domain] Live backend not running. Domain config will be loaded on backend startup.")
        
    print(f"[Switch Domain] Domain switch complete.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Switch AI-Native Operations Copilot active domain.")
    parser.add_argument("domain", type=str, choices=["sme", "education", "agriculture"], help="Domain name")
    args = parser.parse_args()
    switch_domain(args.domain)
