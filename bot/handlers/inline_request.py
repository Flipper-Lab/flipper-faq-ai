import logging

from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from bot.utils.faq_engine import FaqFlipperBot

faq_bot = FaqFlipperBot(faq_dir="faq")

logger = logging.getLogger(__name__)

inline_router = Router()


@inline_router.inline_query()
async def handle_inline_query(inline_query: InlineQuery) -> None:
    query = inline_query.query.strip()

    if not query:
        return

    answers = faq_bot.find_best_matches(query, limit=3)
    results: list[InlineQueryResult] = []

    if answers:
        for i, answer in enumerate(answers):
            item = InlineQueryResultArticle(
                id=str(i),
                title=f"✅ Вариант {i + 1}",
                input_message_content=InputTextMessageContent(message_text=answer),
                description=answer[:100] + "..." if len(answer) > 100 else answer,
            )
            results.append(item)
    else:
        item = InlineQueryResultArticle(
            id="0",
            title="❌ Ответ не найден",
            input_message_content=InputTextMessageContent(
                message_text="Извините, я не нашел ответа на ваш вопрос."
            ),
            description="Попробуйте переформулировать запрос",
        )
        results.append(item)

    await inline_query.answer(results, is_personal=True, cache_time=1)  # type: ignore а потому что разрабы aiogram пидоры
