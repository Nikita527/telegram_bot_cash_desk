from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from handlers.create_requests import RequestStates
from handlers.ultils import (PAGE_SIZE, create_change_button,
                             create_navigation_buttons, create_pay_button)
from models.crud import get_unpaid_cash_request, get_unpaid_no_cash_request
from sqlalchemy.orm import Session


async def show_unpaid_requests_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Показать текущие неоплаченные заявки."""

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Наличные заявки")],
            [types.KeyboardButton(text="Безналичные заявки")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите тип заявки:", reply_markup=keyboard)


async def show_unpaid_cash_requests_handler(
    message: types.Message, state: FSMContext, db: Session, page: int = 0
):
    """Показать неоплаченные наличные заявки."""

    unpaid_cash_requests = get_unpaid_cash_request(db)
    if not unpaid_cash_requests:
        await message.answer("Нет текущих неоплаченных заявок.")
        await state.set_state(RequestStates.choosing_request_type)
        return

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    requests_page = unpaid_cash_requests[start:end]

    response = "Текущие неоплаченные заявки:\n\n"
    for request in requests_page:
        response += (
            f"Контрагент: {request.counterparty.name}\n"
            f"Сумма: {request.amount}\n"
            f"Комментарий: {request.comment}\n"
        )

        keyboard = create_pay_button(request.id, "cash")
        if str(request.user.telegram_id) == str(message.from_user.id):
            change_button = create_change_button(request.id, "cash")
            keyboard.inline_keyboard.append(change_button.inline_keyboard[0])
        await message.answer(response, reply_markup=keyboard)
        response = ""
    navigation_keyboard = create_navigation_buttons(
        page, len(unpaid_cash_requests), "cash"
    )
    if navigation_keyboard.inline_keyboard:
        await message.answer(
            "Навигация по страницам:", reply_markup=navigation_keyboard
        )


async def show_unpaid_noncash_requests_handler(
    message: types.Message, state: FSMContext, db: Session, page: int = 0
):
    """Показать неоплаченные безналичные оплаты."""

    unpaid_nocash_requests = get_unpaid_no_cash_request(db)
    if not unpaid_nocash_requests:
        await message.answer("Нет текущих неоплаченных заявок.")
        await state.set_state(RequestStates.choosing_request_type)
        return

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    requests_page = unpaid_nocash_requests[start:end]

    response = "Текущие неоплаченные заявки:\n\n"
    for request in requests_page:
        response += (
            f"Контрагент: {request.counterparty.name}\n"
            f"Сумма: {request.amount}\n"
            f"Комментарий: {request.comment}\n"
            f"Счет на оплату:{request.invoice_path}"
        )

        keyboard = create_pay_button(request.id, "noncash")
        if str(request.user.telegram_id) == str(message.from_user.id):
            change_button = create_change_button(request.id, "noncash")
            keyboard.inline_keyboard.append(change_button.inline_keyboard[0])
        await message.answer(response, reply_markup=keyboard)
        response = ""
    navigation_keyboard = create_navigation_buttons(
        page, len(unpaid_nocash_requests), "cash"
    )
    if navigation_keyboard.inline_keyboard:
        await message.answer(
            "Навигация по страницам:", reply_markup=navigation_keyboard
        )


async def choose_cash_request_type_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Обработчик выбора наличной заявки"""

    await show_unpaid_cash_requests_handler(message, state, db)


async def choose_noncash_request_type_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Обработчик выбора безналичной заявки"""

    await show_unpaid_noncash_requests_handler(message, state, db)


def register_handlers_show_requests(dp: Dispatcher):
    dp.message.register(
        show_unpaid_requests_handler,
        F.text == "Посмотреть текущие не оплаченные заявки",
    )
    dp.message.register(
        choose_cash_request_type_handler,
        F.text == "Наличные заявки",
    )
    dp.message.register(
        choose_noncash_request_type_handler,
        F.text == "Безналичные заявки",
    )
