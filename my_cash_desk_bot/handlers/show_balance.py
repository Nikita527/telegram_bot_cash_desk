from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from models.crud import get_user_cash_balance, get_user_non_cash_balance
from sqlalchemy.orm import Session


async def show_balance_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Показать текущий баланс."""

    keybord = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Наличная касса")],
            [types.KeyboardButton(text="Безналичная касса")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите кассу:", reply_markup=keybord)


async def show_cash_balance_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Показатель баланс наличной кассы пользователя."""

    user_id = str(message.from_user.id)
    cash_balance = get_user_cash_balance(db, user_id)
    await message.answer(f"Ваш баланс наличной кассы {cash_balance} руб.")


async def show_noncash_balance_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Показатель баланс безналичной кассы пользователя."""

    user_id = str(message.from_user.id)
    noncash_balance = get_user_non_cash_balance(db, user_id)
    await message.answer(f"Ваш баланс наличной кассы {noncash_balance} руб.")


def reqister_handlers_show_balance(db: Dispatcher):
    db.message.register(
        show_balance_handler,
        F.text == "Проверить баланс",
    )
    db.message.register(show_cash_balance_handler, F.text == "Наличная касса")
    db.message.register(
        show_noncash_balance_handler, F.text == "Безналичная касса"
    )
