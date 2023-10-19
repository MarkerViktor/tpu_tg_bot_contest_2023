import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from dependency_injector.wiring import inject, Provide

from src.lib.state_machine import StateMachine
from src.container import Container


@inject
async def start_bot(bot: Bot = Provide["bot.client"], state_machine: StateMachine = Provide["state_machine"]) -> None:
    dp = Dispatcher()
    dp.message()(state_machine.handle_action)
    dp.callback_query()(state_machine.handle_action)
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


def start():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    container = Container()
    container.wire(
        modules=[__name__],
        packages=[
            "src.bot.handlers",
        ],
    )

    asyncio.run(start_bot(), debug=True)
