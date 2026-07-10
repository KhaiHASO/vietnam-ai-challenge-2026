from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract interface for Large Language Models (LLM).
    Can be implemented using OpenAI, Anthropic, or Local LLMs (via LM Studio/Ollama).
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Sends a prompt to the LLM and returns the generated text.
        
        Args:
            prompt: The user query combined with context.
            system_prompt: Optional instructions on how the LLM should behave.
            
        Returns:
            str: The text response from the LLM.
        """
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: str = ""):
        """
        Sends a prompt to the LLM and yields the generated text chunks.
        """
        pass
