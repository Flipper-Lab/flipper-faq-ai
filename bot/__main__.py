import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Settings
from bot.handlers import info_router, inline_router, start_router

logger = logging.getLogger(__name__)
settings = Settings()
bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(
        link_preview_is_disabled=True, parse_mode=ParseMode.HTML
    ),
)
dp = Dispatcher()

dp.include_routers(start_router, info_router, inline_router)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.warning("Бот остановлен пользователем")
