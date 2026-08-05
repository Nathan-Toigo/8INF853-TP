from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "sqlite:///./app.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()