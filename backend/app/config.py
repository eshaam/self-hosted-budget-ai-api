import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Development mode
    DEV_MODE: bool = os.getenv("DEV_MODE", "true").lower() == "true"
    
    # File paths
    API_KEYS_FILE: str = os.getenv("API_KEYS_FILE", "config/api_keys.txt")
    WHITELIST_FILE: str = os.getenv("WHITELIST_FILE", "config/whitelist.txt")
    
    # Model settings
    MODEL_NAME: str = "Qwen/Qwen2-0.5B-Instruct"
    MODEL_CACHE_DIR: str = os.getenv("MODEL_CACHE_DIR", "models")
    MAX_NEW_TOKENS: int = int(os.getenv("MAX_NEW_TOKENS", "512"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
Path(settings.API_KEYS_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.WHITELIST_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(settings.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)