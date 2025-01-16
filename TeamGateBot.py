import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from flask import Flask, request
import asyncio

# Загружаем переменные окружения
load_dotenv()

# Токен бота и Telegram ID администратора
API_TOKEN = os.getenv("API_TOKEN")  # Токен вашего бота
ADMIN_ID = os.getenv("ADMIN_ID")  # Telegram ID администратора

# Проверяем наличие токена и ID
if not API_TOKEN or not ADMIN_ID:
    raise ValueError("Необходимо задать API_TOKEN и ADMIN_ID в переменных окружения.")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Flask приложение
app = Flask(__name__)

# Состояния анкеты
class Form(StatesGroup):
    country = State()
    work = State()
    age = State()
    responsible = State()
    work_time = State()
    telegram_user = State()
    level = State()
    name = State()

# Клавиатуры
work_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="SMM-менеджером")],
        [types.KeyboardButton(text="Дизайнером")],
        [types.KeyboardButton(text="Программистом")],
    ],
    resize_keyboard=True,
)

yes_no_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Да")],
        [types.KeyboardButton(text="Нет")],
    ],
    resize_keyboard=True,
)

level_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="A1-A2")],
        [types.KeyboardButton(text="A2-B1")],
        [types.KeyboardButton(text="B1-B2")],
        [types.KeyboardButton(text="B2-C1")],
        [types.KeyboardButton(text="C1-C2")],
    ],
    resize_keyboard=True,
)

# Хэндлеры состояний
@dp.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы стать частью команды Bright English, вам нужно заполнить анкету. "
        "После заполнения с вами свяжется владелец.\n\n"
        "1. Гражданином какой страны вы являетесь?"
    )
    await state.set_state(Form.country)


@dp.message(Form.country)
async def handle_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Кем вы хотите работать в нашей команде?", reply_markup=work_kb)
    await state.set_state(Form.work)


@dp.message(Form.work)
async def handle_work(message: types.Message, state: FSMContext):
    await state.update_data(work=message.text)
    await message.answer("3. Сколько вам лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def handle_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите ваш возраст цифрами.")
        return
    await state.update_data(age=message.text)
    await message.answer("4. Вы ответственный и пунктуальный человек?", reply_markup=yes_no_kb)
    await state.set_state(Form.responsible)


@dp.message(Form.responsible)
async def handle_responsible(message: types.Message, state: FSMContext):
    await state.update_data(responsible=message.text)
    await message.answer("5. Сколько времени у вас есть на вашу работу?")
    await state.set_state(Form.work_time)


@dp.message(Form.work_time)
async def handle_work_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    await message.answer("6. Ваш юзер в телеграме (например, @username):")
    await state.set_state(Form.telegram_user)


@dp.message(Form.telegram_user)
async def handle_telegram_user(message: types.Message, state: FSMContext):
    await state.update_data(telegram_user=message.text)
    await message.answer("7. Какой ваш уровень английского?", reply_markup=level_kb)
    await state.set_state(Form.level)


@dp.message(Form.level)
async def handle_level(message: types.Message, state: FSMContext):
    await state.update_data(level=message.text)
    await message.answer("8. Назовите ваше имя.")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def handle_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()

    # Отправка уведомления владельцу
    await bot.send_message(
        ADMIN_ID,
        f"Новая анкета!\n\n"
        f"Гражданство: {data['country']}\n"
        f"Должность: {data['work']}\n"
        f"Возраст: {data['age']}\n"
        f"Ответственность: {data['responsible']}\n"
        f"Время на работу: {data['work_time']}\n"
        f"Юзер: {data['telegram_user']}\n"
        f"Уровень: {data['level']}\n"
        f"Имя: {data['name']}",
    )
    await message.answer("Спасибо за заполнение анкеты! Мы с вами свяжемся.")
    await state.clear()


# Flask-приложение для работы с WebHook
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = types.Update.de_json(json_str)
    asyncio.run(dp.feed_update(bot, update))  # Асинхронно обрабатываем обновление
    return "OK", 200


# Функция для настройки webhook
async def setup_webhook():
    webhook_url = "https://web-production-6e2b.up.railway.app/webhook"  # Замените на ваш реальный URL
    await bot.set_webhook(webhook_url)

# Запуск Flask
if __name__ == "__main__":
    # Настроим webhook перед запуском Flask
    asyncio.run(setup_webhook())

    # Запускаем Flask сервер
    app.run(host="0.0.0.0", port=5000)