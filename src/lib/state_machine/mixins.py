import typing
from abc import ABC, abstractmethod

from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dependency_injector.wiring import inject, Provide

from .state_machine import StateCode, Action, Context, ChatId


Keyboard: typing.TypeAlias = ReplyKeyboardMarkup | ReplyKeyboardRemove


class RenderedViewOnEnter(ABC):
    @abstractmethod
    async def render_text(self, chat_id: ChatId, context: Context) -> str: ...

    @abstractmethod
    async def render_keyboard(self, chat_id: ChatId, context: Context) -> Keyboard: ...

    @inject
    @typing.final
    async def send_view(self, chat_id: ChatId, context: Context, bot: Bot = Provide["bot.client"]) -> None:
        text = await self.render_text(chat_id, context)
        keyboard = await self.render_keyboard(chat_id, context)
        await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html")

    async def on_enter(self, chat_id: ChatId, context: Context) -> None:
        await self.send_view(chat_id, context)


class StaticViewOnEnter(RenderedViewOnEnter, ABC):
    @property
    @abstractmethod
    def text(self) -> str: ...

    @property
    @abstractmethod
    def keyboard(self) -> Keyboard: ...

    @typing.final
    async def render_text(self, chat_id: ChatId, context: Context) -> str:
        return self.text

    @typing.final
    async def render_keyboard(self, chat_id: ChatId, context: Context) -> Keyboard:
        return self.keyboard


ValidatorReturnType = typing.TypeVar("ValidatorReturnType")


class ValidateOnMessage(typing.Generic[ValidatorReturnType], ABC):
    @abstractmethod
    async def validator(self, message: Message) -> ValidatorReturnType | None: ...

    async def on_correct(self, result: ValidatorReturnType, chat_id: ChatId, context: Context) -> None:
        pass

    @inject
    async def on_incorrect(
        self,
        message: Message,
        chat_id: ChatId,
        context: Context,
        bot: Bot = Provide["bot.client"],
    ) -> None:
        await bot.send_message(chat_id, "Недопустимый ввод!")

    @typing.final
    async def validate(self, message: Message, chat_id: ChatId, context: Context) -> None:
        value = await self.validator(message)
        if value is not None:
            await self.on_correct(value, chat_id=chat_id, context=context)
        else:
            await self.on_incorrect(message, chat_id=chat_id, context=context)

    async def message_handler(self, message: Message, chat_id: ChatId, context: Context) -> None:
        return await self.validate(message, chat_id, context)


class ChoiceByMessage(ValidateOnMessage, ABC):
    """
    Обработка выбора по тексту сообщения. Атрибут options – варианты выбора.
    Если текст – это один из вариантов, то вызовется on_correct, иначе – on_incorrect.
    """

    @abstractmethod
    async def options(self) -> typing.Sequence[str]: ...

    @typing.final
    async def validator(self, message: Message) -> str | None:
        options = await self.options()
        if message.text in options:
            return message.text


class SwitchStateByMessage(ChoiceByMessage, ABC):
    """
    Переключает состояние в соответствии с текстом получаемого сообщения.
    Атрибут options_switcher – словарь, где ключ – текст сообщения, значение – название состояния.
    """

    _switch_options: dict[str, StateCode] | None = None

    @abstractmethod
    async def switch_options(self) -> dict[str, StateCode]: ...

    async def _get_switch_options(self) -> dict[str, StateCode]:
        if self._switch_options is None:
            self._switch_options = await self.switch_options()
        return self._switch_options

    async def options(self):
        switch_options = await self._get_switch_options()
        return switch_options.keys()

    @typing.final
    async def after_action_switcher(self, action: Action, context: Context) -> StateCode | None:
        if not isinstance(action, Message):
            return

        switch_options = await self._get_switch_options()
        if state_code := switch_options.get(action.text):
            return state_code


class ClearVarsOnExit(ABC):
    """Удаляет переменные контекста, перечисленные в атрибуте clearing_vars."""

    @property
    @abstractmethod
    def clearing_context_keys(self) -> typing.Collection[str]: ...

    async def on_exit(self, chat_id: ChatId, context: Context) -> None:
        context.delete_keys(*self.clearing_context_keys)
