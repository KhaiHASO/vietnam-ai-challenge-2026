import logging
import json
import os
import datetime
from ai_layer.rag.interfaces.llm import BaseLLMProvider

logger = logging.getLogger(__name__)

class LLMJudgeEvaluator:
    """
    Evaluates RAG results using an LLM-as-a-judge approach.
    Evaluates two main metrics:
    1. Faithfulness: Is the answer derived ONLY from the provided context?
    2. Answer Relevance: Does the answer directly address the query?
    """
    def __init__(self, llm: BaseLLMProvider = None, registry=None):
        if llm is None:
            from ai_layer.rag.core.dependencies import get_llm_provider

            llm = get_llm_provider()
        self.llm = llm
        # We can optionally pass registry, else it imports it.
        if registry is None:
            from ai_layer.rag.registries.capability_registry import get_capability_registry
            self.registry = get_capability_registry()
        else:
            self.registry = registry
            
    def _get_prompt(self, domain: str, prompt_type: str, fallback_prompt: str) -> str:
        if not domain or domain == "default":
            return fallback_prompt
            
        try:
            cap = self.registry.get_capability(domain)
        except Exception as e:
            logger.error(f"Failed to resolve capability prompt for domain {domain}: {e}")
            return fallback_prompt

        if not isinstance(cap, dict):
            return fallback_prompt
            
        pack_path = cap.get("path")
        if not pack_path:
            return fallback_prompt

        pack_path = os.path.abspath(str(pack_path))
        prompt_path = os.path.join(pack_path, "prompts", "evaluator", f"{prompt_type}.md")
        prompt_path = os.path.abspath(prompt_path)
        if os.path.commonpath([pack_path, prompt_path]) != pack_path:
            logger.error(f"Refusing to load evaluator prompt outside pack path: {prompt_path}")
            return fallback_prompt
        
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read prompt file {prompt_path}: {e}")
                
        return fallback_prompt
        
    def evaluate(self, query: str, answer: str, context: str, tenant_id: str = "default", session_id: str = "default", domain: str = "default", prompt_version: str = "v1", latency: float = 0.0):
        """
        Run the evaluation using the LLM and log the result to SQLite.
        Returns a dictionary with scores.
        """
        import jinja2
        
        default_faithfulness = """
Bạn là một giám khảo chuyên nghiệp. Hãy đánh giá xem câu trả lời sau đây có hoàn toàn dựa trên thông tin từ Context được cung cấp hay không.
Trả lời theo định dạng JSON: {"score": <điểm từ 0 đến 10>, "reason": "<lý do ngắn gọn>"}
Context: {{context}}
Answer: {{answer}}
"""
        
        default_relevance = """
Bạn là một giám khảo chuyên nghiệp. Hãy đánh giá xem câu trả lời sau đây có giải quyết trực tiếp và chính xác câu hỏi của người dùng hay không.
Trả lời theo định dạng JSON: {"score": <điểm từ 0 đến 10>, "reason": "<lý do ngắn gọn>"}
Query: {{query}}
Answer: {{answer}}
"""
        
        faithfulness_template_str = self._get_prompt(domain, "faithfulness", default_faithfulness)
        relevance_template_str = self._get_prompt(domain, "relevance", default_relevance)
        
        try:
            faithfulness_template = jinja2.Template(faithfulness_template_str, undefined=jinja2.StrictUndefined)
            relevance_template = jinja2.Template(relevance_template_str, undefined=jinja2.StrictUndefined)
            
            faithfulness_prompt = faithfulness_template.render(context=context, answer=answer)
            relevance_prompt = relevance_template.render(query=query, answer=answer)
        except jinja2.exceptions.UndefinedError as e:
            logger.error(f"Template Variable Error: {e}. Check your prompt template variables.")
            raise ValueError(f"Lỗi định dạng Template: {e}")
            
        try:
            faithfulness_res = self.llm.generate(
                faithfulness_prompt, 
                "Bạn là hệ thống chấm điểm tự động. Luôn trả về định dạng JSON.",
                response_mime_type="application/json"
            )
            relevance_res = self.llm.generate(
                relevance_prompt, 
                "Bạn là hệ thống chấm điểm tự động. Luôn trả về định dạng JSON.",
                response_mime_type="application/json"
            )
            
            f_data = json.loads(faithfulness_res.strip())
            r_data = json.loads(relevance_res.strip())
            
            record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "tenant_id": tenant_id,
                "session_id": session_id,
                "domain": domain,
                "prompt_version": prompt_version,
                "query": query,
                "faithfulness_score": f_data.get("score", 0.0),
                "faithfulness_reason": f_data.get("reason", ""),
                "relevance_score": r_data.get("score", 0.0),
                "relevance_reason": r_data.get("reason", ""),
                "latency": latency
            }
            
            # Save to SQLite
            from ai_layer.rag.memory.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO evaluations (session_id, tenant_id, domain, prompt_version, query, faithfulness_score, relevance_score, latency, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, tenant_id, domain, prompt_version, query, record["faithfulness_score"], record["relevance_score"], latency, record["timestamp"]))
            conn.commit()
            conn.close()
                
            logger.info(f"Evaluated response: Faithfulness={record['faithfulness_score']}, Relevance={record['relevance_score']}")
            return record
            
        except Exception as e:
            logger.error(f"Error during LLM Evaluation: {e}")
            return None
