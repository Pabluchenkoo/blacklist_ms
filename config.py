from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')

    class Config:
        env_file = ".env"

settings = Settings()
