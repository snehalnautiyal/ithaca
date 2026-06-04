from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_bind: str = "127.0.0.1"
    app_port: int = 7860
    secret_key: str = "change-me"
    auth_enabled: bool = True
    database_url: str = "sqlite:///data/app.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
