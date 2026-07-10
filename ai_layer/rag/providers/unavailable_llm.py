from ai_layer.rag.interfaces.llm import BaseLLMProvider


class UnavailableLLMProvider(BaseLLMProvider):
    """
    Safe fallback used when no configured cloud LLM provider is available.
    It keeps RAG routes importable and returns a clear operational message.
    """

    provider_name = "unavailable"

    def __init__(self, reason: str = "No LLM provider is configured."):
        self.reason = reason

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return (
            "AI provider is not configured for this environment. "
            f"{self.reason}"
        )

    def generate_stream(self, prompt: str, system_prompt: str = ""):
        yield self.generate(prompt=prompt, system_prompt=system_prompt)
