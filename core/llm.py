from langchain_community.llms import Ollama
from core.config import settings

def get_llm():
    """Returns an instance of the configured LLM."""
    return Ollama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL_NAME
    )
