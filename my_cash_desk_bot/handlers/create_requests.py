import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers.ultils import create_change_requests_buttons, notify_all_users
from models.crud import (
    create_cash_request,
    create_counterparty,
    create_no_cash_request,
    get_counterparty,
    get_user,
)
from sqlalchemy.orm import Session

MIME_TYPES = [
    "application/pdf",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]


class RequestStates(StatesGroup):
    choosing_request_type = State()
    entering_contractor_name = State()
    entering_amount = State()
    entering_phone_or_card = State()
    entering_bank_name = State()
    entering_comment = State()
    uploading_invoice = State()
    confirming_request = State()
    awaiting_confirmation = State()
    editing_request = State()
    show_unpaid_cash_request = State()
    show_unpaid_nocash_request = State()
    awaiting_check = State()


async def create_request_handler(message: types.Message, state: FSMContext):
    """Создать заявку."""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Наличная заявка")],
            [types.KeyboardButton(text="Безналичная заявка")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите тип заявки:", reply_markup=keyboard)
    await state.set_state(RequestStates.choosing_request_type)


async def choose_request_type_handler(
    message: types.Message, state: FSMContext
):
    """Выбор в зависимости от типа заявки."""

    if message.text in ["Наличная заявка", "Безналичная заявка"]:
        await state.update_data(request_type=message.text)
        await message.answer("Введите имя контрагента:")
        await state.set_state(RequestStates.entering_contractor_name)
    else:
        await message.answer(
            "Пожалуйста, выберите один из предложенных вариантов."
        )


async def get_contractor_name_handler(
    message: types.Message, state: FSMContext, db: Session
):
    """Проверка контрагента в базе данных."""

    contractor_name = message.text
    await state.update_data(contractor_name=contractor_name)

    # Проверка наличия контрагента в базе данных
    contractor = get_counterparty(db, contractor_name)

    if contractor:
        # Контрагент найден, сохраняем его данные
        await state.update_data(
            contractor_id=contractor.id,
            contractor_name=contractor.name,
            phone_or_card=contractor.phone_or_card,
            bank_name=contractor.bank,
        )
        await message.answer("Введите сумму для оплаты контрагенту:")
        await state.set_state(RequestStates.entering_amount)
    else:
        # Контрагент не найден
        await state.update_data(contractor_id=None)
        await message.answer("Введите сумму для оплаты контрагенту:")
        await state.set_state(RequestStates.entering_amount)


async def get_amount_to_pay(message: types.Message, state: FSMContext):
    """Сумма к оплате."""

    await state.update_data(amount=message.text)
    data = await state.get_data()
    if data.get("request_type") == "Наличная заявка":
        if data.get("contractor_id") is None:
            # Если контрагент не найден, запрашиваем дополнительную информацию
            await message.answer(
                "Введите номер телефона или номер банковской карты:"
            )
            await state.set_state(RequestStates.entering_phone_or_card)
        else:
            # Если контрагент найден, переходим к комментарию
            await message.answer("Введите комментарий:")
            await state.set_state(RequestStates.entering_comment)
    else:
        # Для безналичной заявки сразу переходим к комментарию
        await message.answer("Введите комментарий:")
        await state.set_state(RequestStates.entering_comment)


async def get_phone_or_card_handler(message: types.Message, state: FSMContext):
    """Ввод информации для оплаты."""

    await state.update_data(phone_or_card=message.text)
    await message.answer("Введите наименование банка:")
    await state.set_state(RequestStates.entering_bank_name)


async def get_bank_name_handler(message: types.Message, state: FSMContext):
    """Уточнение банка для оплаты."""

    await state.update_data(bank_name=message.text)
    await message.answer("Введите дополнительный комментарий:")
    await state.set_state(RequestStates.entering_comment)


async def get_comment_handler(message: types.Message, state: FSMContext):
    """Добавить комментарий."""

    await state.update_data(comment=message.text)
    data = await state.get_data()

    if data.get("request_type") == "Безналичная заявка":
        await message.answer("Загрузите счет на оплату (PDF или Excel):")
        await state.set_state(RequestStates.uploading_invoice)
    else:
        await show_summary(message, state)


async def get_invoice_handler(message: types.Message, state: FSMContext):
    """Добавить счет на оплату."""

    if message.content_type == types.ContentType.DOCUMENT:
        if message.document.mime_type in MIME_TYPES:
            file_info = await message.bot.get_file(message.document.file_id)
            file_path = file_info.file_path
            file_name = os.path.basename(file_path)
            if not os.path.exists("./invoices"):
                os.makedirs("./invoices")
            await message.bot.download_file(
                file_path, f"./invoices/{file_name}"
            )
            await state.update_data(invoice_path=f"./invoices/{file_name}")
            await show_summary(message, state)
        else:
            await message.answer(
                "Пожалуйста, загрузите файл в формате PDF или Excel."
            )
    else:
        await message.answer(
            "Пожалуйста, загрузите счет на оплату (PDF или Excel)."
        )


async def show_summary(message: types.Message, state: FSMContext):
    """Показать заявку."""

    data = await state.get_data()
    summary = (
        f"Имя контрагента: {data['contractor_name']}\n"
        f"Комментарий: {data['comment']}\n"
        f"Сумма: {data.get('amount', 'Не указано')}"
    )
    if data.get("request_type") == "Безналичная заявка":
        summary += f"\nСчет: {data.get('invoice_path', 'Не загружен')}"
    else:
        summary += (
            f"\nТелефон/Карта: {data.get('phone_or_card', 'Не указано')}\n"
            f"Банк: {data.get('bank_name', 'Не указано')}"
        )
    await message.answer(f"Заявка:\n\n{summary}")
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Да", callback_data="confirm_yes"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Нет", callback_data="confirm_no"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Изменить", callback_data="confirm_edit"
                )
            ],
        ]
    )
    await message.answer("Подтвердите заявку:", reply_markup=keyboard)
    await state.set_state(RequestStates.awaiting_confirmation)


async def confirm_request_handler(
    callback_query: types.CallbackQuery,
    state: FSMContext,
    db: Session,
    bot: Bot,
):
    """Подтверждение заявки."""

    data = await state.get_data()
    user = get_user(db, str(callback_query.from_user.id))
    if not user:
        await callback_query.message.answer("Пользователь не найден.")
        await callback_query.answer()
        return

    if callback_query.data == "confirm_yes":
        # Проверка наличия контрагента в базе данных
        contractor = get_counterparty(db, data["contractor_name"])
        if not contractor:
            # Создание нового контрагента
            if data.get("request_type") == "Безналичная заявка":
                contractor = create_counterparty(
                    db,
                    name=data["contractor_name"],
                    phone_or_card=None,
                    bank=None,
                    is_individual=True,
                )
            else:
                contractor = create_counterparty(
                    db,
                    name=data["contractor_name"],
                    phone_or_card=data["phone_or_card"],
                    bank=data["bank_name"],
                    is_individual=True,
                )
            db.add(contractor)
            db.commit()
        if data.get("request_type") == "Безналичная заявка":
            request = create_no_cash_request(
                db,
                user_id=user.id,
                counterparty_id=contractor.id,
                amount=data["amount"],
                invoice_path=data["invoice_path"],
                comment=data["comment"],
                status=False,
            )
        else:
            request = create_cash_request(
                db,
                user_id=user.id,
                counterparty_id=contractor.id,
                amount=data["amount"],
                comment=data["comment"],
                status=False,
            )
        db.add(request)
        db.commit()
        await state.update_data(request_id=request.id)
        summary = (
            f"Имя контрагента: {data['contractor_name']}\n"
            f"Комментарий: {data['comment']}\n"
            f"Сумма: {data.get('amount', 'Не указано')}\n"
        )
        if data.get("request_type") == "Безналичная заявка":
            summary += f"\nСчет: {data.get('invoice_path', 'Не загружен')}"
        else:
            summary += (
                f"Телефон/Карта: {data.get('phone_or_card', 'Не указано')}\n"
                f"Банк: {data.get('bank_name', 'Не указано')}\n"
            )
        await callback_query.message.answer(f"Заявка отправлена:\n\n{summary}")
        await state.clear()
        notification_message = f"Новая заявка создана:\n\n{summary}"
        await notify_all_users(bot, db, notification_message)
    elif callback_query.data == "confirm_edit":
        keyboard = create_change_requests_buttons(0, data["request_type"])
        await callback_query.message.answer(
            "Что вы хотите изменить? Выберите одно из следующих:",
            reply_markup=keyboard,
        )
        await state.set_state(RequestStates.editing_request)
    else:
        await callback_query.message.answer("Заявка отменена.")
        await state.clear()
    await callback_query.answer()


def register_handlers_create_requests(dp: Dispatcher, bot: Bot):
    dp.message.register(create_request_handler, F.text == "Создать заявку")
    dp.message.register(
        choose_request_type_handler, RequestStates.choosing_request_type
    )
    dp.message.register(
        get_contractor_name_handler, RequestStates.entering_contractor_name
    )
    dp.message.register(get_amount_to_pay, RequestStates.entering_amount)
    dp.message.register(
        get_phone_or_card_handler, RequestStates.entering_phone_or_card
    )
    dp.message.register(
        get_bank_name_handler, RequestStates.entering_bank_name
    )
    dp.message.register(get_comment_handler, RequestStates.entering_comment)
    dp.message.register(get_invoice_handler, RequestStates.uploading_invoice)
    dp.callback_query.register(
        confirm_request_handler, RequestStates.awaiting_confirmation
    )
