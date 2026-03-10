from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_key: str = ""
    api_timeout_max: int = 120
    api_stealth_timeout_max: int = 180
    api_max_concurrent: int = 10

    model_config = {"env_prefix": "API_", "env_file": ".env"}


settings = Settings()
