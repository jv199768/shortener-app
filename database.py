# shortener_app/models.py

from sqlalchemy import create_engine
from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import lru_cache

class Settings(BaseSettings):
	env_name: str = "Local"
	base_url: str = "http://localhost:8000"
	db_url: str = "sqlite:///./shortener.db"
	class Config:
		env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings

	
engine = create_engine(
    get_settings().db_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()

