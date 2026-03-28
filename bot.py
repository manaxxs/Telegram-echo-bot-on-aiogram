import logging
import os
from typing import Final

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BotStates(StatesGroup):
    """States for bot conversation."""

    echo: State = State()


BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")


class EchoBot:
    """Echo bot implementation with aiogram 3.x."""

    def __init__(self, token: str) -> None:
        self.bot: Bot = Bot(token=token, parse_mode="HTML")
        self.storage: MemoryStorage = MemoryStorage()
        self.dispatcher: Dispatcher = Dispatcher(storage=self.storage)
        self.router: Router = Router()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all message handlers."""
        self.router.message.register(self.handle_start, Command("start"))
        self.router.message.register(self.handle_help, Command("help"))
        self.router.message.register(self.handle_echo, BotStates.echo)
        self.router.message.register(self.handle_any_message)
        self.dispatcher.include_router(self.router)

    @staticmethod
    async def handle_start(message: Message) -> None:
        """Handle /start command."""
        await message.answer(
            f"Привет, <b>{message.from_user.first_name}</b>!\n\n"
            "Я эхо-бот. Напиши что-нибудь, и я повторю."
        )

    @staticmethod
    async def handle_help(message: Message) -> None:
        """Handle /help command."""
        await message.answer(
            "<b>Доступные команды:</b>\n"
            "/start - Запустить бота\n"
            "/help - Показать справку\n"
            "/echo - Включить режим эхо"
        )

    @staticmethod
    async def handle_echo(message: Message, state: FSMContext) -> None:
        """Handle echo mode messages."""
        user_text = message.text

        if user_text.startswith("/"):
            await state.clear()
            return

        await message.answer(f"Эхо: {user_text}")

    @staticmethod
    async def handle_any_message(message: Message) -> None:
        """Handle any other messages."""
        await message.answer(
            f"Я получил: <i>{message.text}</i>\n\n"
            "Используй /help для списка команд."
        )

    async def start(self) -> None:
        """Start polling for updates."""
        logger.info("Starting bot...")
        await self.dispatcher.start_polling(self.bot)

    async def close(self) -> None:
        """Close bot connections."""
        await self.bot.session.close()
        logger.info("Bot stopped")


async def main() -> None:
    """Main entry point."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    bot = EchoBot(BOT_TOKEN)

    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
