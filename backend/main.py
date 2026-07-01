import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# Add parent directory to sys.path to allow importing ai_layer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_layer.orchestrator import AIOrchestrator
from ai_layer.approval.hitl import hitl_manager
from ai_layer.tools.db_mock import load_db, save_db, DEFAULT_STATE
from ai_layer.rag.knowledge_base import seed_knowledge_base

app = FastAPI(title="AI-Native Operations Copilot Backend", version="1.0.0")

# Enable CORS for Next.js frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend port/origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed knowledge base and database on startup
@app.on_event("startup")
def startup_event():
    print("[Backend] Initializing databases...")
    seed_knowledge_base()
    # Initialize DB state
    load_db()
    print("[Backend] Setup complete.")

class ChatRequest(BaseModel):
    query: str

class ApprovalActionRequest(BaseModel):
    pass

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
    save_db(DEFAULT_STATE)
    return {"success": True, "message": "Database reset to defaults."}

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
