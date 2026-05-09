from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://fcp:fcp@localhost:5432/fcp"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 480
    openweather_api_key: str = ""
    weather_city: str = "Paris"
    environment: str = "development"


settings = Settings()
