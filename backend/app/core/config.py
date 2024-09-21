from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool
    ALLOWED_HOSTS: List[str]
    CORS_ORIGINS: List[str]
    ENVIRONMENT: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Create an instance of Settings
settings = Settings()
