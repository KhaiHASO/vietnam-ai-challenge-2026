from typing import TypedDict, List, Dict, Any, Optional
from ai_layer.rag.models import Chunk

class AgentState(TypedDict):
    """
    State object passed between nodes in the Agentic RAG graph.
    """
    session_id: str
    original_question: str
    current_query: str
    chat_history: List[Dict[str, str]]
    
    # Retrieval
    documents: List[Chunk]
    
    # Decisions and reflections
    needs_retrieval: bool
    is_relevant: bool
    reflection_feedback: str
    loop_count: int
    
    # Generation
    answer: str
    citations: List[str]
    tenant_id: str
    system_prompt: str
    prompt_version: str
