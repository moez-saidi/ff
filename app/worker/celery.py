from celery import Celery
from pydantic import SecretStr
from pydantic_settings import BaseSettings


class RabbitMQSettings(BaseSettings):
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: SecretStr
    RABBITMQ_PORT: int


config = RabbitMQSettings()

celery = Celery(
    "worker",
    broker=f"pyamqp://{config.RABBITMQ_DEFAULT_USER}:{config.RABBITMQ_DEFAULT_PASS.get_secret_value()}@rabbitmq:{config.RABBITMQ_PORT}//",
    backend="rpc://",
)
