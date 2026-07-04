import os
import sys
import argparse

# Allow imports from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_layer.config import settings
from ai_layer.rag.knowledge_base import seed_knowledge_base
from ai_layer.tools.db_mock import load_db

def seed_domain(domain: str, train: bool = False):
    domain = domain.lower().strip()
    if domain not in ["sme", "education", "agriculture"]:
        print(f"Error: Invalid domain '{domain}'.")
        return
        
    print(f"\n==========================================")
    print(f"  SEEDING DOMAIN: {domain.upper()}")
    print(f"==========================================")
    
    # 1. Temporarily switch ACTIVE_DOMAIN
    settings.ACTIVE_DOMAIN = domain
    
    # 2. Seed RAG database
    # This will write to domains/{domain}/data/vector_store.json
    print("[Seed] Initializing RAG Knowledge Base...")
    seed_knowledge_base()
    
    # 3. Seed Mock Database State
    # This will write to domains/{domain}/data/db_state.json
    print("[Seed] Initializing Mock Database State...")
    load_db()
    
    # 4. Optional: Train/warmup PyTorch model
    if train:
        print("[Seed] Training baseline PyTorch model (3 epochs)...")
        from ai_layer.pytorch_engine.train import train_model
        train_model(domain, epochs=3, batch_size=8)
    else:
        print("[Seed] PyTorch model training skipped. Run with --train flag to auto-train baseline weights.")
        
    print(f"[Seed] Seeding complete for '{domain.upper()}'. Paths:")
    print(f"  - DB: {settings.db_path}")
    print(f"  - Vector DB: {settings.vector_db_path}")
    print("==========================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed RAG and DB mock data for domains.")
    parser.add_argument("--domain", type=str, default="all", choices=["all", "sme", "education", "agriculture"], help="Domain to seed")
    parser.add_argument("--train", action="store_true", help="Auto-train baseline PyTorch weights during seed")
    args = parser.parse_args()
    
    if args.domain == "all":
        for d in ["sme", "education", "agriculture"]:
            seed_domain(d, args.train)
    else:
        seed_domain(args.domain, args.train)
