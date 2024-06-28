import os

from aiogram import BaseMiddleware, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from models.crud import create_user, get_user
from models.deps import get_db
from sqlalchemy.orm import Session

load_dotenv()

VALID_PASSWORD = os.getenv("PASSWORD")


class AuthStates(StatesGroup):
    waiting_for_password = State()
    waiting_for_cash_balance = State()
    waiting_for_non_cash_balance = State()


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with get_db() as db:
            data["db"] = db
            return await handler(event, data)


async def start_handler(
    message: types.Message, state: FSMContext, db: Session
):
    telegram_id = str(message.from_user.id)
    user = get_user(db, telegram_id)

    if user:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Создать заявку")],
                [
                    types.KeyboardButton(
                        text="Посмотреть текущие не оплаченные заявки"
                    )
                ],
                [types.KeyboardButton(text="Проверить баланс")],
            ],
            resize_keyboard=True,
        )
        await message.answer(
            "Добро пожаловать обратно! Выберите действие:",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            "Вас привествует кассовый помощник. Для продолжения, пожалуйста, "
            + "введите пароль:"
        )
        await state.set_state(AuthStates.waiting_for_password)


async def password_handler(
    message: types.Message, state: FSMContext, db: Session
):
    if message.text == VALID_PASSWORD:
        await state.update_data(
            telegram_id=str(message.from_user.id),
            username=message.from_user.username,
        )
        await message.answer("Введите начальный баланс в кассе (наличные):")
        await state.set_state(AuthStates.waiting_for_cash_balance)
    else:
        await message.answer("Неверный пароль. Попробуйте снова:")


async def cash_balance_handler(
    message: types.Message, state: FSMContext, db: Session
):
    try:
        cash_balance = int(message.text)
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число для начального баланса "
            + "в кассе (наличные):"
        )
        return
    await state.update_data(cash_balance=cash_balance)
    await message.answer("Введите начальный баланс в кассе (безналичные):")
    await state.set_state(AuthStates.waiting_for_non_cash_balance)


async def non_cash_balance_handler(
    message: types.Message, state: FSMContext, db: Session
):
    try:
        non_cash_balance = int(message.text)
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число для начального баланса "
            + "в кассе (безналичные):"
        )
        return
    user_data = await state.get_data()
    telegram_id = user_data["telegram_id"]
    username = user_data["username"]
    cash_balance = user_data["cash_balance"]
    create_user(db, telegram_id, username, cash_balance, non_cash_balance)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Создать заявку")],
            [
                types.KeyboardButton(
                    text="Посмотреть текущие не оплаченные заявки"
                )
            ],
            [types.KeyboardButton(text="Проверить баланс")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "Пользователь создан. Выберите действие:", reply_markup=keyboard
    )
    await state.clear()


async def cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /cancel."""
    await state.clear()
    await message.answer(
        "Действие отменено.", reply_markup=types.ReplyKeyboardRemove()
    )


def register_handlers_start(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(password_handler, AuthStates.waiting_for_password)
    dp.message.register(
        cash_balance_handler, AuthStates.waiting_for_cash_balance
    )
    dp.message.register(
        non_cash_balance_handler, AuthStates.waiting_for_non_cash_balance
    )
    dp.message.register(cancel_handler, Command(commands=["cancel"]))
