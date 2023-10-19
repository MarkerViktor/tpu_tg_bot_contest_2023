from textwrap import dedent

from databases import Database

from .base import StateMachineStorage, Context, ChatId
from ..state_machine import StateCode


class PGStateMachineStorage(StateMachineStorage):
    def __init__(self, db: Database):
        self._db = db

    async def get_state(self, chat_id: ChatId) -> StateCode | None:
        stmt = dedent("""
            select s.state_code 
            from bot.chat_state as s 
            where s.chat_id = (:chat_id)::bigint
        """)
        return await self._db.fetch_val(stmt, {"chat_id": chat_id})

    async def set_state(self, chat_id: ChatId, state_name: StateCode) -> None:
        stmt = dedent("""
            insert into bot.chat_state (chat_id, state_code) values ((:chat_id)::bigint, (:state_code)::text)
            on conflict (chat_id) do update set state_code = excluded.state_code;
        """)
        await self._db.execute(stmt, {"chat_id": chat_id, "state_code": state_name})

    async def get_context(self, chat_id: ChatId) -> Context | None:
        stmt = dedent("""
            select c.context
            from bot.chat_context as c
            where c.chat_id = (:chat_id)::bigint
        """)
        record = await self._db.fetch_val(stmt, {"chat_id": chat_id})
        if record is None:
            return None
        return Context(record)

    async def set_context(self, chat_id: ChatId, context: Context) -> None:
        stmt = dedent("""
            insert into bot.chat_context (chat_id, context) values ((:chat_id)::bigint, (:context)::jsonb)
            on conflict (chat_id) do update set context = excluded.context;
        """)
        await self._db.execute(stmt, {"chat_id": chat_id, "context": context})
