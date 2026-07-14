from typing import TypedDict, List, Dict, Any, Literal
from ai_layer.rag.contracts.request import CopilotRequest
from ai_layer.rag.contracts.memory import Evidence

class AgenticState(TypedDict, total=False):
    request: CopilotRequest
    memory_context: Any
    route_class: Literal["fast", "standard", "complex"]
    evidence: List[Evidence]
    rewrite_count: int
    reflect_count: int
    loop_count: int
    generated_draft: str | None
    validation_verdicts: List[Any]
    versions: Dict[str, str]
    degraded_state: bool
    trace_id: str
    
    # compatibility fields for old nodes/tests
    original_question: str
    current_query: str
    needs_retrieval: bool
    documents: List[Any]
    is_relevant: bool
    reflection_feedback: str
    answer: str
    citations: List[str]
    system_prompt: str
    facts: List[str]
    tenant_id: str

# Alias for compatibility with nodes.py
AgentState = AgenticState
