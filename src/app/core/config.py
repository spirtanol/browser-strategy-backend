import os
from functools import lru_cache
from typing import Type

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'
    )

    # Общие настройки приложения
    env: str = Field('development', env='APP_ENV')
    debug: bool = Field(False, env="DEBUG")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env='REDIS_URL')
    dt_multiplier: float = 480
    tick_duration: int = 1
    

class DevelopmentSettings(AppSettings):
    debug: bool = True

class TestingSettings(AppSettings):
    model_config = SettingsConfigDict(env_file=".env.test")
    debug: bool = True
    env: str = 'testing'

class ProductionSettings(AppSettings):
    debug: bool = False
    https: bool = True

_ENV_TO_CLASS: dict[str, Type[AppSettings]] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings
}

@lru_cache
def get_config() -> AppSettings:
    if "APP_ENV" not in os.environ:
        load_dotenv()

    env: str = os.getenv("APP_ENV", "development").strip().lower()
    SettingsClass = _ENV_TO_CLASS.get(env, DevelopmentSettings)
    return SettingsClass(env=env)
