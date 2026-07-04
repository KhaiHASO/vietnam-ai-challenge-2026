import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Add parent directory to sys.path to allow importing ai_layer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_layer.config import settings
from ai_layer.orchestrator import AIOrchestrator
from ai_layer.approval.hitl import hitl_manager
from ai_layer.tools.db_mock import load_db, save_db
from ai_layer.rag.knowledge_base import seed_knowledge_base
from ai_layer.cropdoctor.api.router import router as cropdoctor_router

app = FastAPI(title="AI-Native Operations Copilot Backend", version="1.0.0")

# Enable CORS for Next.js frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend port/origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cropdoctor_router)

# Seed knowledge base and database on startup
@app.on_event("startup")
def startup_event():
    print(f"[Backend] Initializing databases for domain '{settings.ACTIVE_DOMAIN}'...")
    seed_knowledge_base()
    load_db()
    print("[Backend] Setup complete.")

class ChatRequest(BaseModel):
    query: str

class SwitchDomainRequest(BaseModel):
    domain: str

class ApprovalActionRequest(BaseModel):
    pass

@app.post("/api/domain/switch")
def switch_domain(request: SwitchDomainRequest):
    """
    Switch the active domain of the AI system dynamically.
    """
    domain = request.domain.lower().strip()
    if domain not in ["sme", "education", "agriculture"]:
        raise HTTPException(status_code=400, detail="Invalid domain. Choose 'sme', 'education', or 'agriculture'.")
        
    settings.ACTIVE_DOMAIN = domain
    
    # Re-seed vector db and load/create db state file
    seed_knowledge_base()
    current_db = load_db()
    
    return {
        "success": True,
        "active_domain": domain,
        "db_path": settings.db_path,
        "vector_db_path": settings.vector_db_path,
        "message": f"Successfully switched to domain '{domain.upper()}'."
    }

@app.get("/api/domain/status")
def get_domain_status():
    """
    Get the currently active domain and model configuration.
    """
    return {
        "active_domain": settings.ACTIVE_DOMAIN,
        "model_name": settings.MODEL_NAME,
        "db_path": settings.db_path,
        "vector_db_path": settings.vector_db_path
    }

@app.post("/api/chat")
def chat(request: ChatRequest):
    """
    Process user chat request through the 9-step AI-Native Orchestrator.
    """
    try:
        orchestrator = AIOrchestrator()
        result = orchestrator.process_request(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")

@app.get("/api/database")
def get_database_state():
    """
    Retrieve the current simulated database state.
    """
    return load_db()

@app.post("/api/database/reset")
def reset_database_state():
    """
    Reset the simulated database to defaults.
    """
    from ai_layer.tools.db_mock import DEFAULT_SME_STATE, DEFAULT_EDUCATION_STATE, DEFAULT_AGRICULTURE_STATE
    domain = settings.ACTIVE_DOMAIN
    if domain == "education":
        default_state = DEFAULT_EDUCATION_STATE
    elif domain == "agriculture":
        default_state = DEFAULT_AGRICULTURE_STATE
    else:
        default_state = DEFAULT_SME_STATE
    save_db(default_state)
    return {"success": True, "message": f"Database for domain '{domain.upper()}' reset to defaults."}

@app.get("/api/approvals")
def get_approvals():
    """
    Get all pending human-in-the-loop approvals.
    """
    return hitl_manager.get_pending_approvals()

@app.post("/api/approvals/{approval_id}/approve")
def approve_approval(approval_id: str):
    """
    Approve a pending action.
    """
    result = hitl_manager.approve_action(approval_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/api/approvals/{approval_id}/reject")
def reject_approval(approval_id: str):
    """
    Reject a pending action.
    """
    result = hitl_manager.reject_action(approval_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
