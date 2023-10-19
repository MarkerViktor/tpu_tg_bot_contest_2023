import json
import typing

import asyncpg
from databases import Database


async def asyncpg_init(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
    await connection.set_type_codec("json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


async def database_pool(url: str, **kwargs) -> typing.AsyncGenerator[Database, None]:
    """Получить пул соединений к базе данных."""
    async with Database(url, init=asyncpg_init, **kwargs) as db:
        yield db
