import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.callback import register_handlers_callback
from handlers.create_requests import register_handlers_create_requests
from handlers.show_balance import reqister_handlers_show_balance
from handlers.show_requests import register_handlers_show_requests
from handlers.edit_requests import register_handlers_edit_request
from handlers.start import DatabaseMiddleware, register_handlers_start

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация middleware для базы данных
dp.update.middleware(DatabaseMiddleware())


async def set_commands(bot: Bot):

    commands = [
        types.BotCommand(command="/start", description="Запустить бота"),
        types.BotCommand(
            command="/cancel", description="Отменить текущее действие"
        ),
    ]

    await bot.set_my_commands(commands)


# Регистрация обработчиков
register_handlers_start(dp)
register_handlers_create_requests(dp, bot)
register_handlers_show_requests(dp)
register_handlers_callback(dp)
reqister_handlers_show_balance(dp)
register_handlers_edit_request(dp)


async def on_startup(dp: Dispatcher):
    await set_commands(bot)


async def main():
    # Запуск поллинга
    await on_startup(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
