from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dependency_injector import containers, providers

from src.config import Config, TelegramBotConfig


class BotContainer(containers.DeclarativeContainer):
    config = providers.Dependency(TelegramBotConfig)

    client = providers.Singleton(
        Bot,
        token=config.provided.token,
        parse_mode=ParseMode.HTML,
    )

    dispatcher = providers.Singleton(
        Dispatcher,
        storage=None,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Factory(
        Config,
        _env_file=(".env", ".env.prod"),
    )

    bot = providers.Container(
        BotContainer,
        config=config.provided.bot,
    )

    states = providers.List(
    )

    state_machine = providers.Singleton(
        StateMachine,
        states=states,
        default_state_code=default_state.code,
        storage=providers.Singleton(
            PGStateMachineStorage,
            db=_db,
        ),
    )
