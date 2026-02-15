from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    Автоматически считывает переменные из .env или окружения.
    """

    db_url: str = Field(..., alias="DATABASE_URL")

    # --- AI SETTINGS ---
    gemini_api_key: SecretStr = Field(..., alias="GEMINI_API_KEY")
    model_name: str = Field("gemini-1.5-flash", alias="AI_MODEL_NAME")
    temperature: float = Field(0.8, alias="AI_TEMPERATURE")

    # --- TELEGRAM ---
    bot_token: SecretStr | None = Field(None, alias="TELEGRAM_BOT_TOKEN")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать лишние переменные в .env
    )

# Создаем экземпляр настроек (Singleton)
settings = Settings()
