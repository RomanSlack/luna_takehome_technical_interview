from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg://luna:lunapass@db:5432/luna"
    APP_ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000


settings = Settings()
