from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def question_button() -> InlineKeyboardMarkup:
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🔍 Задать вопрос", switch_inline_query_current_chat=""
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
