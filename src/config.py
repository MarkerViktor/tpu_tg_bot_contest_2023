from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramBotConfig(BaseModel):
    token: str


class SQLiteConfig(BaseModel):
    path: Path

    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.path}"


class PostgreSQLConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Config(BaseSettings):
    bot: TelegramBotConfig

    db: PostgreSQLConfig

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        env_nested_delimiter=".",
    )
