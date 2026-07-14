import logging
import json
import hashlib
import inspect
from typing import List, Dict, Any
from ai_layer.rag.agentic.state import AgenticState
from ai_layer.rag.contracts.memory import Evidence

logger = logging.getLogger(__name__)

class AgenticNodes:
    def __init__(self, retriever, provider_gateway, registry_catalog=None):
        self.retriever = retriever
        self.gateway = provider_gateway
        self.catalog = registry_catalog

    async def retrieve_node(self, state: AgenticState) -> AgenticState:
        """Retrieves documents based on the current query."""
        request = state["request"]
        query = state.get("current_query") or request.query
        logger.info(f"[AgenticNodes] Running retrieve_node for query: {query}")
        
        top_k = 5
        filters = {"tenant_id": request.tenant_id, "domain_id": request.domain_id}
        
        # Self retriever has retrieve method
        chunks = self.retriever.retrieve(query, top_k=top_k, filters=filters)
        if inspect.isawaitable(chunks):
            chunks = await chunks
        
        evidence_list = []
        for c in chunks:
            metadata = c.metadata
            extra = getattr(metadata, "extra", {})
            content = c.text
            ev = Evidence(
                chunk_id=c.id,
                document_id=getattr(metadata, "source_id", "doc"),
                source_uri=extra.get("source_uri", "kb://"),
                tenant_id=request.tenant_id,
                domain_id=request.domain_id,
                index_revision=extra.get("index_revision", "default"),
                score=float(getattr(metadata, "rerank_score", None) or extra.get("score", 0.9)),
                content=content,
                checksum=extra.get("checksum") or hashlib.sha256(content.encode()).hexdigest(),
                source_title=extra.get("source_title", "Document"),
                page_or_section=extra.get("page_or_section"),
                document_status=extra.get("document_status", "active"),
            )
            evidence_list.append(ev)
            
        state["evidence"] = evidence_list
        state["current_query"] = query
        return state

    async def reflect_node(self, state: AgenticState) -> AgenticState:
        """Evaluates if the retrieved documents are relevant to the query."""
        logger.info("[AgenticNodes] Running reflect_node")
        evidence = state.get("evidence", [])
        if not evidence:
            state["is_relevant"] = False
            state["reflection_feedback"] = "Không tìm thấy tài liệu nào."
            return state

        query = state["current_query"]
        context_str = "\n".join([f"- {ev.content}" for ev in evidence])
        
        prompt = (
            f"Hãy đánh giá xem tài liệu dưới đây có đủ thông tin để trả lời câu hỏi '{query}' hay không.\n"
            f"Tài liệu:\n{context_str}\n\n"
            f"Trả về JSON dạng: {{\"is_relevant\": true/false, \"feedback\": \"Lý do tại sao\"}}\n"
            f"Chỉ trả về JSON hợp lệ."
        )
        
        try:
            res_text = await self.gateway.generate(prompt, [])
            if "```" in res_text:
                res_text = res_text.split("```")[1]
                if res_text.startswith("json"):
                    res_text = res_text[4:]
            res = json.loads(res_text.strip())
            state["is_relevant"] = bool(res.get("is_relevant", True))
            state["reflection_feedback"] = res.get("feedback", "")
        except Exception as e:
            logger.warning(f"Reflect node failed: {e}. Defaulting to True.")
            state["is_relevant"] = True
            state["reflection_feedback"] = ""
            
        state["reflect_count"] = state.get("reflect_count", 0) + 1
        return state

    async def rewrite_node(self, state: AgenticState) -> AgenticState:
        """Rewrites the query if documents were not relevant."""
        logger.info("[AgenticNodes] Running rewrite_node")
        query = state["current_query"]
        feedback = state.get("reflection_feedback", "")
        
        prompt = (
            f"Câu hỏi gốc: '{query}'\n"
            f"Phản hồi từ lần tìm kiếm trước: '{feedback}'\n"
            f"Hãy viết lại câu hỏi tìm kiếm này rõ ràng và chi tiết hơn để thu được kết quả tốt hơn. Chỉ trả về câu hỏi mới."
        )
        
        try:
            new_query = await self.gateway.generate(prompt, [])
            state["current_query"] = new_query.strip()
        except Exception as e:
            logger.warning(f"Rewrite query failed: {e}")
            
        state["rewrite_count"] = state.get("rewrite_count", 0) + 1
        return state
