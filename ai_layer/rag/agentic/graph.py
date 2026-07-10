from langgraph.graph import StateGraph, END
from ai_layer.rag.agentic.state import AgentState
from ai_layer.rag.agentic.nodes import AgenticNodes

def create_agentic_graph(nodes: AgenticNodes):
    """
    Creates and compiles the LangGraph state machine for Agentic RAG.
    """
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", nodes.planner_node)
    workflow.add_node("retrieve", nodes.retrieve_node)
    workflow.add_node("reflect", nodes.reflect_node)
    workflow.add_node("rewrite", nodes.rewrite_node)
    workflow.add_node("generate", nodes.generate_node)
    
    # Define routing logic
    def route_after_plan(state: AgentState) -> str:
        if state.get("needs_retrieval", True):
            return "retrieve"
        return "generate"
        
    def route_after_reflect(state: AgentState) -> str:
        # Nếu đủ tốt hoặc đã loop quá 2 lần thì chuyển sang generate
        if state.get("is_relevant", True) or state.get("loop_count", 0) >= 2:
            return "generate"
        # Ngược lại thì viết lại câu hỏi
        return "rewrite"
        
    # Build edges
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_after_plan,
        {
            "retrieve": "retrieve",
            "generate": "generate"
        }
    )
    
    workflow.add_edge("retrieve", "reflect")
    
    workflow.add_conditional_edges(
        "reflect",
        route_after_reflect,
        {
            "generate": "generate",
            "rewrite": "rewrite"
        }
    )
    
    workflow.add_edge("rewrite", "retrieve")
    workflow.add_edge("generate", END)
    
    # Compile
    return workflow.compile()
