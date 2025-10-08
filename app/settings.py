from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    RATE_LIMITING_ENABLE: bool = False
    RATE_LIMITING_FREQUENCY: str = "2/3seconds"
    DEBUG: bool = False
    WHITELISTED_TOKEN: str | None = None
    WEBSHARE_API_KEY: str | None = None
    CACHE_EXPIRY_SECONDS: int = 60 * 60 * 24


settings = Settings()
