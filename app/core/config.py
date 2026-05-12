from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Travel Paglu"
    environment: str = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    # Supabase Config
    supabase_url: str = ""
    supabase_key: str = ""

    # Groq Config
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
