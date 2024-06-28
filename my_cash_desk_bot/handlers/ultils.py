from aiogram import Bot, types
from models.crud import get_all_users
from sqlalchemy.orm import Session

PAGE_SIZE = 5


def create_pay_button(
    request_id: int, request_type: str
) -> types.InlineKeyboardMarkup:
    """Создание кнопки 'Оплатить'."""

    pay_button = types.InlineKeyboardButton(
        text="Оплатить", callback_data=f"pay_{request_type}_{request_id}"
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[pay_button]])
    return keyboard


def create_change_button(
    request_id: int, request_type: str
) -> types.InlineKeyboardMarkup:
    """Создание кнопки 'Изменить'."""

    change_button = types.InlineKeyboardButton(
        text="Изменить", callback_data=f"pay_{request_type}_{request_id}"
    )
    keybord = types.InlineKeyboardMarkup(inline_keyboard=[[change_button]])
    return keybord


def create_change_requests_buttons(
    request_id: int, request_type: str
) -> types.InlineKeyboardMarkup:
    """Создание кнопок для изменения полей заявки."""

    buttons = [
        [
            types.InlineKeyboardButton(
                text="Имя контрагента",
                callback_data=f"edit_{request_type}_contractor_{request_id}",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Сумма",
                callback_data=f"edit_{request_type}_amount_{request_id}",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Телефон/Карта",
                callback_data=f"edit_{request_type}_phone_{request_id}",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Банк",
                callback_data=f"edit_{request_type}_bank_{request_id}",
            )
        ],
        [
            types.InlineKeyboardButton(
                text="Комментарий",
                callback_data=f"edit_{request_type}_comment_{request_id}",
            )
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_navigation_buttons(
    page: int, total_requests: int, prefix: str
) -> types.InlineKeyboardMarkup:
    """Создание кнопок навигации для пагинации"""

    navigation_keyboard = types.InlineKeyboardMarkup()
    if page > 0:
        navigation_keyboard.add(
            types.InlineKeyboardButton(
                text="Назад", callback_data=f"{prefix}_page_{page - 1}"
            )
        )
    if (page + 1) * PAGE_SIZE < total_requests:
        navigation_keyboard.add(
            types.InlineKeyboardButton(
                text="Вперед", callback_data=f"{prefix}_page_{page + 1}"
            )
        )
    return navigation_keyboard


async def notify_all_users(bot: Bot, db: Session, message: str):
    """Отправить уведомление всем пользователям."""
    users = get_all_users(db)
    for user in users:
        try:
            await bot.send_message(user.telegram_id, message)
        except Exception as e:
            print(
                f"Не удалось отправить сообщение пользователю"
                f" {user.telegram_id}: {e}"
            )
