import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from dependency_injector.wiring import inject, Provide

from src.container import Container
from src.bot.handlers.common import router as common_router


@inject
async def start_bot(bot: Bot = Provide["bot.client"], dp: Dispatcher = Provide["bot.dispatcher"]) -> None:
    dp.include_routers(common_router)
    await dp.start_polling(bot)


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
