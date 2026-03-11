from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://autoradar:autoradar@localhost:5432/autoradar"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    poll_interval_min: int = 15
    poll_interval_max: int = 45

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
