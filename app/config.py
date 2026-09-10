"""Central application settings (12-factor: everything via environment)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Airline Customer Support System"
    env: str = "dev"
    database_url: str = "sqlite:///./support.db"

    # LLM provider: mock | openai | ollama
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # n8n webhook notified on new tickets (fire-and-forget, optional)
    n8n_webhook_url: str = ""

    # SLA thresholds in minutes
    sla_minutes_urgent: int = 30
    sla_minutes_high: int = 120
    sla_minutes_normal: int = 480

    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
