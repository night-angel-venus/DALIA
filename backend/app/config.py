from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str = ""
    ALGORITHM:str = "HS256"
    TOKEN_EXPIRATION_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()