import os

from ai_layer.rag.interfaces.llm import BaseLLMProvider


class OpenAILLM(BaseLLMProvider):
    """
    LLM provider using an OpenAI-compatible API.
    This supports OpenAI, DeepSeek, and local gateways through base_url.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
        provider_name: str = "openai",
    ):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai library is not installed. Run `pip install openai`") from exc

        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.provider_name = provider_name

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)

    def generate(self, prompt: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
            )

            return response.choices[0].message.content
        except Exception as exc:
            return f"AI provider error ({self.provider_name}): {exc}"

    def generate_stream(self, prompt: str, system_prompt: str = "You are a helpful AI assistant."):
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0,
                stream=True,
            )

            for chunk in response:
                choice = chunk.choices[0] if chunk.choices else None
                delta = getattr(choice, "delta", None) if choice else None
                content = getattr(delta, "content", None) if delta else None
                if content:
                    yield content
        except Exception as exc:
            yield f"AI provider stream error ({self.provider_name}): {exc}"
