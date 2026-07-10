from typing import List
from ai_layer.rag.models import Chunk
from ai_layer.rag.interfaces.llm import BaseLLMProvider


class RAGGenerator:
    """
    The Generator Pipeline is responsible for constructing the final prompt
    from retrieved chunks and generating the answer via the LLM.
    """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider
        
    def build_context(self, chunks: List[Chunk]) -> str:
        """
        Combines the text of multiple chunks into a single context string.
        """
        if not chunks:
            return "Không có ngữ cảnh nào được cung cấp."
            
        context_parts = []
        for i, chunk in enumerate(chunks):
            # We can optionally include metadata like document_id or domain here
            context_parts.append(f"[Tài liệu {i+1}]: {chunk.text}")
            
        return "\n\n".join(context_parts)
        
    def build_prompt(self, query: str, context: str) -> str:
        """
        Constructs the final prompt to be sent to the LLM.
        """
        prompt = (
            "Dựa vào các thông tin ngữ cảnh dưới đây, hãy trả lời câu hỏi của người dùng.\n"
            "Nếu thông tin trong ngữ cảnh không đủ để trả lời, hãy nói rõ là bạn không biết, "
            "đừng cố bịa đặt thêm thông tin.\n\n"
            "--- NGỮ CẢNH ---\n"
            f"{context}\n"
            "----------------\n\n"
            f"Câu hỏi: {query}\n"
            "Câu trả lời:"
        )
        return prompt

    def generate_answer(self, query: str, chunks: List[Chunk]) -> str:
        """
        Orchestrates the context building and LLM generation.
        """
        context_str = self.build_context(chunks)
        final_prompt = self.build_prompt(query, context_str)
        
        system_prompt = (
            "Bạn là một trợ lý AI chuyên nghiệp và hữu ích. "
            "Bạn luôn phân tích kỹ ngữ cảnh được cung cấp trước khi đưa ra câu trả lời."
        )
        
        return self.llm_provider.generate(prompt=final_prompt, system_prompt=system_prompt)
