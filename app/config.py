from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "boilerworks-fastapi-micro"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/boilerworks"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_default: str = "100/minute"
    admin_bootstrap_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
