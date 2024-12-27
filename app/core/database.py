from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    PGPORT: int
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: SecretStr


config = Settings()
DATABASE_URI: PostgresDsn = (
    "postgresql+asyncpg://"
    f"{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.PGPORT}/{config.POSTGRES_DB}"
)
