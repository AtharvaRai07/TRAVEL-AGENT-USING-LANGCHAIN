from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Go Bharat"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    supabase_url: str = ""
    supabase_key: str = ""

    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
