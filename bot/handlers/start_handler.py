import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import question_button

logger = logging.getLogger(__name__)

start_router = Router()

msg = """
Приветствую, я бот–нейросеть для твоих вопросов по поводу <b>Flipper Zero</b>.
<i>Нажми кнопку ниже и задай интересующий тебя вопрос</i>.
"""


@start_router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(text=msg, reply_markup=question_button())
