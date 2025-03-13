# app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
import dotenv
import os


class Settings(BaseSettings):
    db_url: str = Field(env="DATABASE_URL")


dotenv.load_dotenv()
settings = Settings(db_url=os.getenv("DATABASE_URL"))