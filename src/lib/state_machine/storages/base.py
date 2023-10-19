import abc

from ..state_machine import ChatId, Context


class StateMachineStorage(abc.ABC):
    @abc.abstractmethod
    async def get_state(self, chat_id: ChatId) -> str | None:
        """Получить имя состояния пользователя или None если пользователь не существует."""
        ...

    @abc.abstractmethod
    async def set_state(self, chat_id: ChatId, state_name: str) -> None:
        """Установить имя состояния пользователю. Пользователь будет добавлен, если не существовал."""
        ...

    @abc.abstractmethod
    async def get_context(self, chat_id: ChatId) -> Context | None:
        """Получить контекстные переменные пользователя, если он существует."""
        ...

    @abc.abstractmethod
    async def set_context(self, chat_id: ChatId, context: Context) -> None:
        """Установить контекстные переменные пользователя. Пользователь будет добавлен, если не существовал."""
        ...
