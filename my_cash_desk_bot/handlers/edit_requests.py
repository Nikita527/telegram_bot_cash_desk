from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from handlers.create_requests import RequestStates, show_summary


async def edit_request_handler(
    callback_query: types.CallbackQuery, state: FSMContext
):
    """Редактирование заявки."""

    field_to_edit = callback_query.data.split("_")[2]
    if field_to_edit == "contractor":
        await callback_query.message.answer("Введите новое имя контрагента:")
        await state.set_state(RequestStates.entering_contractor_name)
    elif field_to_edit == "amount":
        await callback_query.message.answer("Введите новую сумму:")
        await state.set_state(RequestStates.entering_amount)
    elif field_to_edit == "phone":
        await callback_query.message.answer(
            "Введите новый номер телефона или номер банковской карты:"
        )
        await state.set_state(RequestStates.entering_phone_or_card)
    elif field_to_edit == "bank":
        await callback_query.message.answer(
            "Введите новое наименование банка:"
        )
        await state.set_state(RequestStates.entering_bank_name)
    elif field_to_edit == "comment":
        await callback_query.message.answer("Введите новый комментарий:")
        await state.set_state(RequestStates.entering_comment)
    else:
        await callback_query.message.answer(
            "Неверный выбор. Пожалуйста, выберите предложенные поля."
        )
        await state.set_state(RequestStates.editing_request)
    await callback_query.answer()


async def process_contractor_name(message: types.Message, state: FSMContext):
    """Обработка нового имени контрагента."""

    await state.update_data(contractor_name=message.text)
    await message.answer("Имя контрагента обновлено.")
    await show_summary(message, state)
    await state.set_state(RequestStates.awaiting_confirmation)


async def process_amount(message: types.Message, state: FSMContext):
    """Обработка новой суммы."""

    await state.update_data(amount=message.text)
    await message.answer("Сумма обновлена.")
    await show_summary(message, state)
    await state.set_state(RequestStates.awaiting_confirmation)


async def process_phone_or_card(message: types.Message, state: FSMContext):
    """Обработка нового номера телефона или номера банковской карты."""

    await state.update_data(phone_or_card=message.text)
    await message.answer("Номер телефона или номер банковской карты обновлен.")
    await show_summary(message, state)
    await state.set_state(RequestStates.awaiting_confirmation)


async def process_bank_name(message: types.Message, state: FSMContext):
    """Обработка нового наименования банка."""

    await state.update_data(bank_name=message.text)
    await message.answer("Наименование банка обновлено.")
    await show_summary(message, state)
    await state.set_state(RequestStates.awaiting_confirmation)


async def process_comment(message: types.Message, state: FSMContext):
    """Обработка нового комментария."""

    await state.update_data(comment=message.text)
    await message.answer("Комментарий обновлен.")
    await show_summary(message, state)
    await state.set_state(RequestStates.awaiting_confirmation)


def register_handlers_edit_request(dp: Dispatcher):
    dp.callback_query.register(
        edit_request_handler, RequestStates.editing_request
    )
    dp.message.register(
        process_contractor_name, RequestStates.entering_contractor_name
    )
    dp.message.register(process_amount, RequestStates.entering_amount)
    dp.message.register(
        process_phone_or_card, RequestStates.entering_phone_or_card
    )
    dp.message.register(process_bank_name, RequestStates.entering_bank_name)
    dp.message.register(process_comment, RequestStates.entering_comment)
