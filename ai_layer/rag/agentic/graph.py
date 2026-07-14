import logging

from ai_layer.rag.agentic.nodes import AgenticNodes
from ai_layer.rag.agentic.state import AgenticState
from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.contracts.request import CopilotRequest

logger = logging.getLogger(__name__)


class BoundedAgenticRunner:
    def __init__(
        self,
        retriever=None,
        provider_gateway=None,
        *,
        retriever_factory=None,
        max_loops: int = 2,
    ):
        self.retriever = retriever
        self.retriever_factory = retriever_factory
        self.gateway = provider_gateway
        self.max_loops = max_loops

    async def run(
        self, request: CopilotRequest, route_class: str = "standard"
    ) -> list[Evidence]:
        retriever = self.retriever
        if retriever is None and self.retriever_factory is not None:
            retriever = self.retriever_factory(request.domain_id)
        if retriever is None:
            logger.warning("No retriever configured; refusing to fabricate evidence")
            return []
        nodes = AgenticNodes(retriever, self.gateway)
        state = AgenticState(
            request=request,
            current_query=request.query,
            rewrite_count=0,
            reflect_count=0,
            evidence=[],
            is_relevant=True,
            route_class=route_class,
        )
        state = await nodes.retrieve_node(state)
        if route_class == "fast" or self.gateway is None:
            return state.get("evidence", [])

        max_reflect = 1 if route_class == "standard" else self.max_loops
        for _ in range(max_reflect):
            state = await nodes.reflect_node(state)
            if state.get("is_relevant", False):
                break
            if state.get("reflect_count", 0) >= max_reflect:
                break
            state = await nodes.rewrite_node(state)
            state = await nodes.retrieve_node(state)
        return state.get("evidence", [])
