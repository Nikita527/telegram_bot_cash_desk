import os

from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from handlers.create_requests import RequestStates
from handlers.show_requests import (show_unpaid_cash_requests_handler,
                                    show_unpaid_noncash_requests_handler)
from models.crud import (get_cash_request, get_no_cash_request,
                         update_cash_request_status,
                         update_no_cash_request_status)
from sqlalchemy.orm import Session


async def pay_cash_request_handler(
    callback_query: types.CallbackQuery, state: FSMContext, db: Session
):
    """Обработчик нажатия на кнопку 'Оплатить' для наличных заявок"""

    request_id = int(callback_query.data.split("_")[-1])
    request = get_cash_request(db, request_id)

    if request:
        await callback_query.message.answer(
            f"Вы выбрали оплатить наличную заявку:\n"
            f"Контрагент: {request.counterparty.name}\n"
            f"Сумма: {request.amount}\n"
            f"Реквезиты для оплаты: \n{request.counterparty.bank}\n"
            f"{request.counterparty.phone_or_card}\n"
            f"Пожалуйста, отправьте чек для подтверждения оплаты."
        )
        await state.update_data(request_id=request_id, request_type="cash")
        await state.set_state(RequestStates.awaiting_check)
    await callback_query.answer()


async def pay_noncash_request_handler(
    callback_query: types.CallbackQuery, state: FSMContext, db: Session
):
    """Обработчик нажатия на кнопку 'Оплатить' для безналичных заявок"""

    request_id = int(callback_query.data.split("_")[-1])
    request = get_no_cash_request(db, request_id)

    if request:
        await callback_query.message.answer(
            f"Вы выбрали оплатить безналичную заявку:\n"
            f"Контрагент: {request.counterparty.name}\n"
            f"Сумма: {request.amount}\n"
            f"Пожалуйста, отправьте чек для подтверждения оплаты."
        )
        if request.invoice_path:
            await callback_query.message.answer_document(
                types.FSInputFile(request.invoice_path),
                caption="Счет на оплату",
            )
        else:
            callback_query.message.answer(
                "Счет на оплату не был добавлен или нет доступа к нему!"
            )
        await state.update_data(request_id=request_id, request_type="noncash")
        await state.set_state(RequestStates.awaiting_check)
    await callback_query.answer()


async def get_check_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Обработчик получения чека или платежного поручения"""

    data = await state.get_data()
    request_id = data.get("request_id")
    request_type = data.get("request_type")

    if message.photo or message.document:
        # Сохраняем чек и обновляем статус заявки
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            file_name = f"./checks/{file_id}.jpg"
        else:
            file_id = message.document.file_id
            file_info = await message.bot.get_file(file_id)
            file_path = file_info.file_path
            file_name = f"./checks/{message.document.file_name}"

        if not os.path.exists("./checks"):
            os.makedirs("./checks")

        await message.bot.download_file(file_path, file_name)

        if request_type == "cash":
            update_cash_request_status(db, request_id, True, file_id)
        else:
            update_no_cash_request_status(db, request_id, True, file_id)
        await message.answer(
            "Чек/платежное поручение получено. Заявка успешно оплачена."
        )
        await state.clear()
    else:
        await message.answer("Пожалуйста, отправьте фото чека или документ.")


async def pagination_callback_handler(
    callback_query: types.CallbackQuery, state: FSMContext, db: Session
):
    """Обработчик коллбэков для пагинации"""

    data = callback_query.data
    if data.startswith("cash_page_"):
        page = int(data.split("_")[2])
        await show_unpaid_cash_requests_handler(
            callback_query.message, state, db, page
        )
    elif data.startswith("noncash_page_"):
        page = int(data.split("_")[2])
        await show_unpaid_noncash_requests_handler(
            callback_query.message, state, db, page
        )
    await callback_query.answer()


def register_handlers_callback(dp: Dispatcher):
    dp.callback_query.register(
        pay_cash_request_handler, F.data.startswith("pay_cash_")
    )
    dp.callback_query.register(
        pay_noncash_request_handler, F.data.startswith("pay_noncash_")
    )
    dp.message.register(get_check_handler, RequestStates.awaiting_check)
    dp.callback_query.register(
        pagination_callback_handler,
        F.data.startswith("cash_page_") | F.data.startswith("noncash_page_"),
    )
