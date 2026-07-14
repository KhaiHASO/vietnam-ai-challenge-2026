import json
import requests
import os
from typing import Dict, Any, List, Tuple
from ai_layer.config import settings
from ai_layer.tools.registry import tool_registry

class AgentPlanner:
    def __init__(self, domain_id: str = "agriculture"):
        self.domain_id = domain_id
        self.provider = settings.PROVIDER
        self.model_name = settings.MODEL_NAME
        self.api_key = settings.API_KEY
        self.base_url = settings.BASE_URL

    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Helper to invoke LLM based on provider with simulation fallback."""
        if self.provider == "ollama":
            try:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {"temperature": settings.TEMPERATURE}
                }
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    return response.json().get("response", "")
            except Exception as e:
                print(f"[Planner] Local Ollama call failed ({e}). Falling back to Simulation Engine.")
                
        elif self.provider == "openai" and self.api_key:
            try:
                # Direct HTTP call to avoid SDK import dependency errors
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": settings.TEMPERATURE
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[Planner] OpenAI API failed ({e}). Falling back to Simulation Engine.")

        # SIMULATION FALLBACK (Extremely useful for development and off-line testing)
        return self._simulate_llm_response(prompt)

    def _simulate_llm_response(self, prompt: str) -> str:
        """Simulates agent thoughts and actions if LLM is offline or not configured (Agriculture only)."""
        lower_prompt = prompt.lower()
        
        if "get_farm_details" in lower_prompt or "frm-" in lower_prompt or "nông trại" in lower_prompt:
            return (
                "Thought: Người dùng muốn kiểm tra thông tin vườn trồng hoặc nông trại. Tôi cần gọi get_farm_details.\n"
                "Action: get_farm_details\n"
                "Action Input: {\"farm_id\": \"FRM-501\"}\n"
                "Observation: [Will be populated by executor]"
            )
        elif "treatment" in lower_prompt or "phun thuốc" in lower_prompt or "bón phân" in lower_prompt:
            return (
                "Thought: Người dùng muốn lưu nhật ký điều trị vườn. Tôi cần gọi log_treatment.\n"
                "Action: log_treatment\n"
                "Action Input: {\"crop_id\": \"CRP-304\", \"treatment_type\": \"irrigation\", \"notes\": \"Tưới nước bổ sung 2 giờ liên tục\"}\n"
                "Observation: [Will be populated by executor]"
            )
        return (
            "Thought: Không cần gọi công cụ.\n"
            "Final Answer: Chào bạn, tôi có thể hỗ trợ giám sát sức khỏe cây trồng, theo dõi độ ẩm đất và kiểm tra lịch sử tưới nước/bón phân."
        )

    def plan_and_execute(self, query: str, context: List[str] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Executes a 1-step ReAct planning loop.
        Returns:
            final_answer (str): The final textual answer.
            trace_steps (list): The trace history for visual debugging.
        """
        trace_steps = []
        
        # Build tool context instructions for the request-scoped domain.
        tool_schemas = tool_registry.get_tool_schemas(domain=self.domain_id)
        tools_desc = "\n".join([f"- {t['function']['name']}: {t['function']['description']}. Args Schema: {t['function']['parameters']}" for t in tool_schemas])
        
        system_prompt = (
            "Bạn là một AI Operations Agent chuyên nghiệp điều phối hệ thống. Quy tắc phản hồi:\n"
            "Nếu bạn cần gọi một công cụ, hãy trả về định dạng chính xác sau:\n"
            "Thought: <suy nghĩ của bạn>\n"
            "Action: <tên công cụ>\n"
            "Action Input: <JSON chứa tham số đầu vào>\n\n"
            "Nếu bạn đã có đủ câu trả lời hoặc không cần dùng công cụ nào nữa, hãy trả về:\n"
            "Thought: <suy nghĩ>\n"
            "Final Answer: <câu trả lời hoàn chỉnh bằng Tiếng Việt>\n"
        )
        
        prompt = f"Ngữ cảnh chính sách (RAG):\n"
        if context:
            prompt += "\n".join([f"- {c}" for c in context]) + "\n\n"
        prompt += f"Công cụ khả dụng:\n{tools_desc}\n\nYêu cầu người dùng: {query}\n"
        
        # Run 1-step iteration of ReAct loop
        llm_response = self._call_llm(prompt, system_prompt)
        
        thought = ""
        action = None
        action_input = {}
        final_answer = ""
        
        # Parse ReAct format
        lines = llm_response.split("\n")
        for line in lines:
            if line.startswith("Thought:"):
                thought = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                try:
                    arg_str = line.replace("Action Input:", "").strip()
                    action_input = json.loads(arg_str)
                except Exception:
                    action_input = {}
            elif line.startswith("Final Answer:"):
                final_answer = line.replace("Final Answer:", "").strip()
                
        # Record step
        trace_steps.append({
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "raw_response": llm_response
        })
        
        # Execute tool if required
        if action and action in tool_registry.tools:
            try:
                # Restrict/Flag high risk actions
                if action == "cancel_booking" or "refund" in query.lower():
                    # High risk check handled in orchestrator/hitl
                    observation = "High risk action requires Human approval."
                else:
                    result = tool_registry.execute(action, action_input)
                    observation = json.dumps(result, ensure_ascii=False)
            except Exception as e:
                observation = f"Error executing tool: {e}"
                
            trace_steps[-1]["observation"] = observation
            
            # Post-execution completion request to LLM
            follow_up_prompt = (
                f"{prompt}\n"
                f"Bước trước:\n"
                f"Thought: {thought}\n"
                f"Action: {action}\n"
                f"Action Input: {action_input}\n"
                f"Observation: {observation}\n\n"
                f"Hãy đưa ra câu trả lời cuối cùng dựa trên kết quả trên bằng Tiếng Việt."
            )
            follow_up_response = self._call_llm(follow_up_prompt, system_prompt)
            
            # Extract final answer
            for line in follow_up_response.split("\n"):
                if line.startswith("Final Answer:"):
                    final_answer = line.replace("Final Answer:", "").strip()
            if not final_answer:
                # Fallback if LLM doesn't follow instructions on follow-up
                final_answer = follow_up_response.replace("Thought:", "").replace("Final Answer:", "").strip()
                
            trace_steps.append({
                "thought": "Tổng hợp kết quả công cụ và trả lời người dùng.",
                "action": None,
                "observation": None,
                "raw_response": follow_up_response
            })
            
        if not final_answer:
            final_answer = "Tôi xin lỗi, tôi không thể tìm thấy câu trả lời chính xác vào lúc này."
            
        return final_answer, trace_steps
