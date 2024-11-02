from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'password')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_NAME: str = os.getenv('DB_NAME', 'blacklist_db')

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"

settings = Settings()
