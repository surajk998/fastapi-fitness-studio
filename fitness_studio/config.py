import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV: Optional[str] = None
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        extra="ignore",
        frozen=True,
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: str = None
    DB_FORCE_ROLL_BACK: bool = False


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    DB_FORCE_ROLL_BACK: bool = True
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


@lru_cache
def get_config(env: str) -> GlobalConfig:
    return {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}[env.lower()]()


config: GlobalConfig = get_config(BaseConfig().ENV)
