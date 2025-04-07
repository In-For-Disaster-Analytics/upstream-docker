from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    POSTGRES_PASSWORD: str
    TAS_USER: str
    TAS_SECRET: str
    JWT_SECRET: str
    TAS_URL: str
    DATABASE_URL: str
    ENV: str
    ENVIRONMENT: str
    ALG: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()