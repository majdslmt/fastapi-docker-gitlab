"""config"""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings"""
    db_url: str = Field(..., env='')


settings = Settings(db_url='')
