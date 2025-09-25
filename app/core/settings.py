from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    ALGORITHM: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
