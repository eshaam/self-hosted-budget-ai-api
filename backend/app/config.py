import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Development mode
    DEV_MODE: bool = os.getenv("DEV_MODE", "False").lower() == "true"
    
    # File paths
    API_KEYS_FILE: str = "config/api_keys.txt"
    WHITELIST_FILE: str = "config/whitelist.txt"
    MODEL_CACHE_DIR: str = "models"
    HUGGINGFACE_API_KEY: str = ""
    MAX_NEW_TOKENS: int = 128000
    TEMPERATURE: float = 0.7
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PORT: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
Path(settings.API_KEYS_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.WHITELIST_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)