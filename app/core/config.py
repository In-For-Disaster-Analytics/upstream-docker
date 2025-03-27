from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    POSTGRES_PASSWORD: str
    tasUser: str
    tasSecret: str
    jwtSecret: str
    tasURL: str
    DATABASE_URL: str
    ENV: str
    ENVIRONMENT: str
    alg: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()