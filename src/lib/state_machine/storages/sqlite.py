import json
import sqlite3
from textwrap import dedent

from .base import StateMachineStorage, Context, ChatId
from ..state_machine import StateCode


sqlite3.register_adapter(dict, json.dumps)
sqlite3.register_converter("json", json.loads)


class SQLiteInMemoryStorage(StateMachineStorage):
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = sqlite3.Row
        self._create_state_table()  # if not exist
        self._create_context_table()

    async def get_state(self, chat_id: ChatId) -> StateCode | None:
        query = "select state_name from chat_state where chat_id = :chat_id"
        record = self._conn.execute(query, {"chat_id": chat_id}).fetchone()
        return record["state_name"] if record is not None else None

    async def set_state(self, chat_id: ChatId, state_name: str) -> None:
        query = dedent("""
            insert into chat_state (chat_id, state_name) values (:chat_id, :state_name)
            on conflict (chat_id) do update set state_name = :state_name;
        """)
        self._conn.execute(query, {"chat_id": chat_id, "state_name": state_name})
        self._conn.commit()

    async def get_context(self, chat_id: ChatId) -> Context | None:
        query = "select context from chat_context where chat_id = :chat_id"
        record = self._conn.execute(query, {"chat_id": chat_id}).fetchone()
        return record["context"] if record is not None else None

    async def set_context(self, chat_id: ChatId, context: Context) -> None:
        query = dedent("""
            insert into chat_context (chat_id, context) values (:chat_id, :context)
            on conflict(chat_id) do update 
            set context =: context;
        """)
        self._conn.execute(query, {"chat_id": chat_id, "context": context})
        self._conn.commit()

    def _create_context_table(self) -> None:
        query = dedent("""
            create table chat_context (
                chat_id INTEGER PRIMARY KEY,
                context json    NOT NULL
            );
        """)
        try:
            self._conn.execute(query)
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def _create_state_table(self) -> None:
        query = dedent("""
            create table chat_state (
                chat_id    INTEGER PRIMARY KEY,
                state_name TEXT    NOT NULL
            );
        """)
        try:
            self._conn.execute(query)
            self._conn.commit()
        except sqlite3.OperationalError:
            pass
