from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotConfig(BaseModel):
    token: str


class SQLiteConfig(BaseModel):
    path: Path

    @property
    def get_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.path}"


class Config(BaseSettings):
    bot: TelegramBotConfig

    db: SQLiteConfig

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        env_nested_delimiter=".",
    )
