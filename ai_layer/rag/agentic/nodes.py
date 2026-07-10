import json
import logging
from typing import List, Dict, Any
from ai_layer.rag.agentic.state import AgentState
from ai_layer.rag.interfaces.llm import BaseLLMProvider
from ai_layer.rag.interfaces.retriever import BaseRetriever

logger = logging.getLogger(__name__)

class AgenticNodes:
    def __init__(self, llm: BaseLLMProvider, retriever: BaseRetriever):
        self.llm = llm
        self.retriever = retriever
        
    def planner_node(self, state: AgentState) -> AgentState:
        """Determines if the question needs retrieval or can be answered directly."""
        logger.info("[AgenticNodes] Running planner_node")
        
        facts = state.get("facts", [])
        facts_str = f"Thông tin đã biết về người dùng:\n- " + "\n- ".join(facts) + "\n" if facts else ""

        prompt = (
            f"Bạn là một hệ thống phân loại câu hỏi.\n"
            f"{facts_str}"
            f"Câu hỏi: '{state['original_question']}'\n"
            f"Nếu câu hỏi là lời chào hỏi thông thường (như xin chào, cảm ơn, bạn là ai) hoặc câu hỏi không cần kiến thức chuyên môn, hãy trả lời bằng JSON: {{\"needs_retrieval\": false}}.\n"
            f"Nếu câu hỏi cần kiến thức chuyên môn nông nghiệp, thủ tục pháp lý, hoặc dữ liệu thực tế, hãy trả lời bằng JSON: {{\"needs_retrieval\": true}}.\n"
            f"Chỉ trả về JSON hợp lệ, không kèm giải thích."
        )
        
        try:
            response = self.llm.generate(prompt=prompt)
            # Dọn dẹp markdown json block nếu có
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(response)
            state['needs_retrieval'] = result.get('needs_retrieval', True)
        except Exception as e:
            logger.warning(f"Planner node failed: {e}. Defaulting to true.")
            state['needs_retrieval'] = True
            
        return state

    def retrieve_node(self, state: AgentState) -> AgentState:
        """Retrieves documents based on the current query."""
        logger.info(f"[AgenticNodes] Running retrieve_node with query: {state['current_query']}")
        
        filters = {"tenant_id": state.get("tenant_id", "default")}
        chunks = self.retriever.retrieve(state['current_query'], top_k=5, filters=filters)
        state['documents'] = chunks
        return state

    def reflect_node(self, state: AgentState) -> AgentState:
        """Evaluates if the retrieved documents are relevant to the query."""
        logger.info("[AgenticNodes] Running reflect_node")
        
        if not state['documents']:
            state['is_relevant'] = False
            state['reflection_feedback'] = "Không tìm thấy tài liệu nào."
            return state
            
        docs_text = "\n\n".join([f"Tài liệu {i+1}: {chunk.text}" for i, chunk in enumerate(state['documents'])])
        
        prompt = (
            f"Bạn là một người đánh giá mức độ liên quan của tài liệu.\n"
            f"Câu hỏi của người dùng: '{state['current_query']}'\n"
            f"Tài liệu tìm được:\n{docs_text}\n"
            f"Tài liệu trên có đủ thông tin để trả lời câu hỏi không?\n"
            f"Trả về JSON với định dạng: {{\"is_relevant\": true/false, \"feedback\": \"Lý do tại sao\"}}.\n"
            f"Chỉ trả về JSON hợp lệ."
        )
        
        try:
            response = self.llm.generate(prompt=prompt)
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()
                
            result = json.loads(response)
            state['is_relevant'] = result.get('is_relevant', True)
            state['reflection_feedback'] = result.get('feedback', "")
        except Exception as e:
            logger.warning(f"Reflect node failed: {e}. Defaulting to true.")
            state['is_relevant'] = True
            state['reflection_feedback'] = ""
            
        return state

    def rewrite_node(self, state: AgentState) -> AgentState:
        """Rewrites the query if documents were not relevant."""
        logger.info("[AgenticNodes] Running rewrite_node")
        
        prompt = (
            f"Câu hỏi gốc: '{state['original_question']}'\n"
            f"Lần tìm kiếm trước với câu hỏi: '{state['current_query']}' không thành công.\n"
            f"Lý do: {state['reflection_feedback']}\n"
            f"Hãy viết lại câu hỏi tìm kiếm này một cách rõ ràng, chi tiết hơn hoặc dùng các từ khóa khác để có thể tìm được tài liệu tốt hơn.\n"
            f"Chỉ trả về câu hỏi mới, không giải thích gì thêm."
        )
        
        try:
            new_query = self.llm.generate(prompt=prompt).strip()
            state['current_query'] = new_query
            state['loop_count'] += 1
        except Exception as e:
            logger.warning(f"Rewrite node failed: {e}.")
            state['loop_count'] += 1
            
        return state

    def generate_node(self, state: AgentState) -> AgentState:
        """Generates the final answer with citations."""
        logger.info("[AgenticNodes] Running generate_node")
        
        if not state.get('needs_retrieval', True):
            # Chit chat
            prompt = (
                f"Hãy trả lời câu hỏi sau một cách thân thiện và ngắn gọn.\n"
                f"Câu hỏi: {state['original_question']}"
            )
            try:
                state['answer'] = self.llm.generate(prompt=prompt)
            except Exception as e:
                state['answer'] = "Xin lỗi, tôi đang gặp sự cố kết nối."
            return state

        # Retrieval based generation
        if not state['documents']:
            state['answer'] = "Xin lỗi, tôi không tìm thấy thông tin nào liên quan đến câu hỏi của bạn trong cơ sở dữ liệu."
            return state
            
        context = ""
        citations = []
        for i, chunk in enumerate(state['documents']):
            context += f"\n--- TÀI LIỆU {i+1} ---\n{chunk.text}\n"
            citations.append(f"Tài liệu {i+1}: ID={chunk.id}, Nguồn={chunk.metadata.get('document_type', 'Unknown')}")
            
        state['citations'] = citations
        
        system_prompt = state.get('system_prompt', "Bạn là trợ lý AI chuyên về Nông nghiệp và EUDR.")
        
        facts = state.get("facts", [])
        if facts:
            system_prompt += "\n\nThông tin đã biết về người dùng:\n- " + "\n- ".join(facts) + "\nHãy sử dụng thông tin này để cá nhân hóa câu trả lời nếu phù hợp."

        # Ensure it instructs to use context
        system_prompt += (
            "\n\nHãy trả lời câu hỏi dựa TRÊN CÁC TÀI LIỆU ĐƯỢC CUNG CẤP. "
            "Khi sử dụng thông tin từ tài liệu nào, hãy trích dẫn bằng [Tài liệu X]. "
            "Nếu tài liệu không có thông tin để trả lời, hãy nói rõ là không có thông tin."
        )
        
        prompt = (
            f"CÂU HỎI: {state['original_question']}\n\n"
            f"TÀI LIỆU:\n{context}\n\n"
            f"CÂU TRẢ LỜI:"
        )
        
        try:
            state['answer'] = self.llm.generate(prompt=prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"Generate node failed: {e}")
            state['answer'] = "Đã xảy ra lỗi khi tạo câu trả lời."
            
        return state
