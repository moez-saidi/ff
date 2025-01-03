from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Settings(BaseSettings):
    POSTGRES_USER: str
    PGPORT: int
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PASSWORD: SecretStr


config = Settings()
DATABASE_URI: PostgresDsn = (
    "postgresql+asyncpg://"
    f"{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD.get_secret_value()}@{config.POSTGRES_HOST}:{config.PGPORT}/{config.POSTGRES_DB}"
)


engine = create_async_engine(DATABASE_URI)
db_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db_session() -> AsyncSession:
    async with db_session() as session:
        yield session
