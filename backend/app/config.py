from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    CLAUDE_API_KEY: str = ""
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

