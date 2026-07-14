import os
import httpx
import logging
from typing import List, AsyncGenerator
from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.providers.gateway import ProviderConfigurationError

logger = logging.getLogger(__name__)

class FPTAIChatAdapter:
    provider_name = "fpt-ai-factory"

    def __init__(self, endpoint: str | None = None, model_id: str | None = None, api_key: str | None = None):
        self.endpoint = endpoint or os.getenv("FPT_AI_FACTORY_ENDPOINT", "https://api.fpt.ai/v1/chat/completions")
        self.model_id = model_id or os.getenv("FPT_AI_FACTORY_MODEL_ID", "qwen2.5-72b-instruct")
        self.api_key = api_key or os.getenv("FPT_AI_FACTORY_API_KEY", "")

    async def generate(self, query: str, evidence: List[Evidence]) -> str:
        if not self.api_key:
            raise ProviderConfigurationError("FPT AI Factory API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        context_str = "\n".join([f"- {ev.content}" for ev in evidence])
        system_prompt = "Bạn là trợ lý nông nghiệp chuyên nghiệp. Hãy trả lời câu hỏi dựa trên các tài liệu được cung cấp dưới đây."
        user_content = f"Tài liệu:\n{context_str}\n\nCâu hỏi: {query}"
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            res_data = response.json()
            return res_data["choices"][0]["message"]["content"]

    async def generate_stream(self, query: str, evidence: List[Evidence]) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise ProviderConfigurationError("FPT AI Factory API key is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        context_str = "\n".join([f"- {ev.content}" for ev in evidence])
        system_prompt = "Bạn là trợ lý nông nghiệp chuyên nghiệp. Hãy trả lời câu hỏi dựa trên các tài liệu được cung cấp dưới đây."
        user_content = f"Tài liệu:\n{context_str}\n\nCâu hỏi: {query}"
        
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,
            "max_tokens": 1024,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            async with client.stream("POST", self.endpoint, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):].strip()
                        if data_str == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data_str)
                            choice = chunk.get("choices", [{}])[0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
