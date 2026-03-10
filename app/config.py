from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    key: str = ""
    timeout_max: int = 120
    stealth_timeout_max: int = 180
    max_concurrent: int = 10

    model_config = {"env_prefix": "API_", "env_file": ".env"}


settings = Settings()
