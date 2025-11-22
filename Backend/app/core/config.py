# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Any

class Settings(BaseSettings):
    DATABASE_URL: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # INI YANG BIKIN ERROR HILANG
    model_config = {
        "env_file": ".env",
        "extra": "ignore"      # <--- BARIS INI AJA YANG DITAMBAH
    }

settings = Settings()