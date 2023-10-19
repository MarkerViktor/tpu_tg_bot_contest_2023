import abc
import typing
from collections import UserDict
from contextlib import asynccontextmanager

from aiogram.types import Message, CallbackQuery

__all__ = [
    "ChatId",
    "State",
    "StateCode",
    "StateMachine",
    "StateMachineStorage",
    "Context",
    "Action",
    "SwitcherResult",
]

from lib.state_machine.storages.base import StateMachineStorage

ChatId = typing.NewType("ChatId", int)
StateCode = typing.NewType("StateCode", str)
SwitcherResult = StateCode | None
Action = Message | CallbackQuery


class Context(UserDict[str, typing.Any]):
    def delete_keys(self, *keys: str) -> None:
        """Удаляет перечисленные ключи."""
        for key in keys:
            try:
                del self.data[key]
            except KeyError:
                pass


class State(abc.ABC):

    @property
    def code(self) -> StateCode:
        return StateCode(self.__class__.__name__)

    async def on_enter(self, chat_id: ChatId, context: Context) -> None:
        """Вызывается при переходе в это состояние."""
        ...

    async def on_exit(self, chat_id: ChatId, context: Context) -> None:
        """Вызывается при выходе из этого состояния."""
        ...

    async def message_handler(self, message: Message, chat_id: ChatId, context: Context) -> None:
        """
        Вызывается при получении сообщения от пользователя.
        Может изменить контекст пользователя.
        """
        ...

    async def callback_handler(self, query: CallbackQuery, chat_id: ChatId, context: Context) -> None:
        """
        Вызывается при обратном вызове встроенной клавиатуры.
        Может изменить контекст пользователя.
        """
        ...

    async def after_action_switcher(self, action: Action, context: Context) -> SwitcherResult:
        """
        Вызывается при получении сообщения или обратного вызова (после соответствующего обработчика).
        Может переключить состояние, вернув его название.
        """
        ...

    async def after_enter_switcher(self, context: Context) -> SwitcherResult:
        """
        Вызывается при переходе в это состояние (после on_enter и до обработчиков).
        Может переключить состояние, вернув его название.
        """
        ...


def _make_states_dict(states: typing.Iterable[State]) -> dict[str, State]:
    states_dict = {}
    for state in states:
        assert state.code not in states_dict, f"Несколько состояний имеют один код «{state.code}»."
        states_dict[state.code] = state
    return states_dict


class StateMachine:
    def __init__(
        self,
        states: typing.Collection[State],
        default_state_code: StateCode,
        storage: StateMachineStorage,
    ):
        self._states = _make_states_dict(states)
        assert default_state_code in self._states, f"Неизвестное состояние по умолчанию «{default_state_code}»"
        self._default_state = self._states[default_state_code]
        self._storage = storage

    async def _get_state(self, chat_id: ChatId) -> State | None:
        """Получить текущее состояние по идентификатору чата."""
        state_code = await self._storage.get_state(chat_id)
        return self._states.get(state_code)

    async def _set_state(self, chat_id: ChatId, state: State) -> None:
        """Установить состояние по идентификатору чата."""
        await self._storage.set_state(chat_id, state.code)

    @asynccontextmanager
    async def _context(self, chat_id: ChatId) -> typing.AsyncGenerator[Context, None]:
        """Контекстный менеджер редактирования контекстных переменных пользователя."""
        context = await self._storage.get_context(chat_id) or {}
        try:
            yield context
        finally:
            await self._storage.set_context(chat_id, context)

    async def _switch_state(
        self, chat_id: ChatId, current_state: State | None, next_state: State, context: Context
    ) -> None:
        """Переключить состояние пользователя, вызвав все надлежащие обработчики."""
        if current_state is not None:
            await current_state.on_exit(chat_id=chat_id, context=context)
        await next_state.on_enter(chat_id=chat_id, context=context)
        await self._set_state(chat_id, next_state)
        next_state_name = await next_state.after_enter_switcher(context=context)
        while next_state_name is not None:
            current_state, next_state = next_state, self._states[next_state_name]
            await current_state.on_exit(chat_id=chat_id, context=context)
            await next_state.on_enter(chat_id=chat_id, context=context)
            await self._set_state(chat_id, next_state)
            next_state_name = await next_state.after_enter_switcher(context=context)

    async def handle_action(self, action: Action):
        """Обработать действие (сообщение или обратный вызов)."""
        chat_id = ChatId(action.from_user.id)

        async with self._context(chat_id) as context:
            # Получение текущего состояния
            current_state = await self._get_state(chat_id)
            if current_state is None:
                # Новый пользователь или пользователь с состоянием, которое больше не доступно
                await self._switch_state(chat_id, None, self._default_state, context)
                return

            # Вызов обработчиков
            if isinstance(action, Message):
                await current_state.message_handler(message=action, chat_id=chat_id, context=context)
            elif isinstance(action, CallbackQuery):
                await current_state.callback_handler(query=action, chat_id=chat_id, context=context)

            # Переключение состояния
            if next_state_code := await current_state.after_action_switcher(action, context):
                next_state = self._states[next_state_code]
                await self._switch_state(chat_id, current_state, next_state, context)
