import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RepoMind"
    ENDEE_HOST: str = "localhost"
    ENDEE_PORT: int = 8080
    ENDEE_COLLECTION_NAME: str = "repomind_codebase"
    
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    LLM_MODEL_NAME: str = "mistral"  # For Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()
