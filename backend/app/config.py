from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List

# Get the backend directory (parent of app/)
backend_dir = Path(__file__).parent.parent
env_file_path = backend_dir / ".env"

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str = ""  # Used by anthropic_client.py
    CLAUDE_API_KEY: str = ""  # Alias/alternative name
    GITHUB_TOKEN: str = ""
    JIRA_URL: str = ""
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=str(env_file_path),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env that aren't in the model
    )

settings = Settings()

