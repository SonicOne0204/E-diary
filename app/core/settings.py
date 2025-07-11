from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    ALGORITHM: str

    class Config:
        env_file = '.env'

settings = Settings()