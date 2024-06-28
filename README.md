### Описание проекта.
Кассовый помошник - это бот, который поможет компании ввести финансовые операции. Чтобы заявки на оплату не терялись, данные о клиентах не путались, оплаты не дублировались.

## Технологии.

- Python 3.11
- Aiogram 3.8
- Postgesql 13.10
- Docker
- SQLAlchemy
- Alembic

## Иструкция по установке:

***- Клонируйте репозиторий:***
```
https://github.com/Nikita527/telegram_bot_cash_desk
```
***- Установите и активируйте виртуальное окружение:***
- для MacOS
```
python3 -m venv venv
```
- для Windows
```
python -m venv venv
source venv/Scripts/activate
```

***- Установите зависимости из файла requirements.txt:***
```
pip install -r requirements/requirements.txt

***- Создать и заполнить .env файл:***
```
API_TOKEN=api-token-of-your-bot
PASSWORD=your-password

POSTGRES_PASSWORD='your-password'
POSTGRES_USER='bot-name'
POSTGRES_DB='db-name'
DB_HOST='localhost'
DB_PORT='5432'
```

***- Запустить Docker:***
```
docker-compose up -d
```

***- Примените миграции:***
```
alembic upgrade head
```

***- Для запуска бота перейти в директорию:***
```
cd my_cash_desk_bot/
python cd_bot.py
```

***- Или скриптом через Powershell на Windows:***
```
start python watchdog_script.py
```

### Принцип работы:
/start - команда для запуска бота, а также оснавная для начала работы, при первом вводе требует ввести пароль для аутификации пользователя.
/cancel - команда для отмены операций.
Осатльные операции проводятся с помощью кнопок или введение информации. Бот в процессе доработки и функционируют только базовые функции.
