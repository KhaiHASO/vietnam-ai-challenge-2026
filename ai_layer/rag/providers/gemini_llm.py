import os
import logging
import time
import uuid
from ai_layer.rag.interfaces.llm import BaseLLMProvider
from observability.context import get_trace_id
from observability.database import TelemetryDB

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiLLM(BaseLLMProvider):
    """
    LLM Provider using Google Gemini API.
    Reads GEMINI_API_KEY from environment.
    """
    
    def __init__(self, model_name: str = None, api_key: str = None):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai is not installed. Run `pip install google-generativeai`")
            
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set.")
            
        genai.configure(api_key=self.api_key)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    def generate(self, prompt: str, system_prompt: str = "Bạn là một trợ lý AI thông minh.", response_mime_type: str = "text/plain") -> str:
        max_retries = 4
        base_delay = 2
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                # Initialize model with system instruction
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_prompt
                )
                
                # Configure safety settings to block none (or default)
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                
                # RAG should be deterministic, so temperature = 0.0
                generation_config = genai.types.GenerationConfig(
                    temperature=0.0,
                    response_mime_type=response_mime_type
                )
                
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                
                # Telemetry tracking
                latency_ms = int((time.time() - start_time) * 1000)
                input_tokens = 0
                output_tokens = 0
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                    output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
                
                # Gemini 1.5 Flash pricing (approx)
                cost = (input_tokens * 0.075 / 1_000_000) + (output_tokens * 0.30 / 1_000_000)
                
                trace_id = get_trace_id()
                if trace_id:
                    span_id = str(uuid.uuid4())
                    TelemetryDB.log_span(
                        span_id=span_id,
                        trace_id=trace_id,
                        step_name="LLM_Generation",
                        latency_ms=latency_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cost_usd=cost
                    )
                
                return response.text
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota" in error_str or "ResourceExhausted" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit (429). Retrying in {delay} seconds... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                logger.error(f"Error generating LLM response from Gemini: {e}")
                raise ValueError(f"Lỗi khi kết nối tới Gemini AI: {str(e)}")

    def generate_stream(self, prompt: str, system_prompt: str = "Bạn là một trợ lý AI thông minh."):
        start_time = time.time()
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            generation_config = genai.types.GenerationConfig(temperature=0.0)
            
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config,
                stream=True
            )
            
            input_tokens = 0
            output_tokens = 0
            
            for chunk in response:
                if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                    input_tokens = getattr(chunk.usage_metadata, "prompt_token_count", input_tokens)
                    output_tokens = getattr(chunk.usage_metadata, "candidates_token_count", output_tokens)
                if chunk.text:
                    yield chunk.text
                    
            latency_ms = int((time.time() - start_time) * 1000)
            cost = (input_tokens * 0.075 / 1_000_000) + (output_tokens * 0.30 / 1_000_000)
            
            trace_id = get_trace_id()
            if trace_id:
                span_id = str(uuid.uuid4())
                TelemetryDB.log_span(
                    span_id=span_id,
                    trace_id=trace_id,
                    step_name="LLM_Generation_Stream",
                    latency_ms=latency_ms,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost
                )
        except Exception as e:
            logger.error(f"Error streaming LLM response from Gemini: {e}")
            raise ValueError(f"Lỗi khi kết nối tới Gemini AI (stream): {str(e)}")
