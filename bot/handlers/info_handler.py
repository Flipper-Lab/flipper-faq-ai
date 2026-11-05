import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)

info_router = Router()

info_text = """
<i>Информация о боте</i>

• <i>Категорий FAQ:</i> <code>1</code>
• <i>Всего вопросов:</i> <code>1</code>

<i>GitHub:</i> <i>github.com/FlipperAI-Lab/flipper-faq-ai</i>
"""


@info_router.message(Command("info"))
async def info_command(message: Message) -> None:
    await message.answer(text=info_text)
