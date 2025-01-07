import logging
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
import os


# Токен бота и ваш Telegram ID
API_TOKEN = "8061515205:AAGxh0hfjMtq8zFZMf2rA-RZrznM7tTAWaQ" # Замените на токен вашего бота
ADMIN_ID = "1940474065"  # Замените на ваш Telegram ID

# Создание бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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

# Кнопки для вопросов
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

# Стартовый хендлер
@dp.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Чтобы стать частью команды Bright English, вам нужно заполнить анкету. "
        "После заполнения с вами свяжется владелец.\n\n"
        "1. Гражданином какой страны вы являетесь?",
    )
    await state.set_state(Form.country)

# Обработка страны
@dp.message(Form.country)
async def handle_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("2. Кем вы хотите работать в нашей команде?", reply_markup=work_kb)
    await state.set_state(Form.work)

# Обработка работы
@dp.message(Form.work)
async def handle_work(message: types.Message, state: FSMContext):
    await state.update_data(work=message.text)
    await message.answer("3. Сколько вам лет?")
    await state.set_state(Form.age)

# Обработка возраста
@dp.message(Form.age)
async def handle_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, укажите ваш возраст цифрами.")
        return
    await state.update_data(age=message.text)
    await message.answer("4. Вы ответственный и пунктуальный человек?", reply_markup=yes_no_kb)
    await state.set_state(Form.responsible)

# Обработка ответственности
@dp.message(Form.responsible)
async def handle_responsible(message: types.Message, state: FSMContext):
    await state.update_data(responsible=message.text)
    await message.answer("5. Сколько времени у вас есть на вашу работу?")
    await state.set_state(Form.work_time)

# Обработка времени работы
@dp.message(Form.work_time)
async def handle_work_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    await message.answer("6. Ваш юзер в телеграме (например, @username):")
    await state.set_state(Form.telegram_user)

# Обработка Telegram-юзера
@dp.message(Form.telegram_user)
async def handle_telegram_user(message: types.Message, state: FSMContext):
    await state.update_data(telegram_user=message.text)
    await message.answer("7. Какой ваш уровень английского?", reply_markup=level_kb)
    await state.set_state(Form.level)

# Обработка уровня
@dp.message(Form.level)
async def handle_level(message: types.Message, state: FSMContext):
    await state.update_data(level=message.text)
    await message.answer("8.Назовите ваше имя.")
    await state.set_state(Form.name)

# Обработка имени и завершение анкеты
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


# Обработчик WebHook
async def on_start(request):
    if request.method == 'POST':
        json_str = await request.text()
        update = types.Update.de_json(json_str)
        await dp.process_update(update)
        return web.Response(status=200)
    return web.Response(status=404)


# Устанавливаем WebHook
async def set_webhook():
    webhook_url = f"https://api.telegram.org/bot8061515205:AAGxh0hfjMtq8zFZMf2rA-RZrznM7tTAWaQ/setWebhook?url=https://Team-gate-b3suw4ral-elizavetas-projects-632274a7.vercel.app/webhook"
    async with aiohttp.ClientSession() as session:
        async with session.get(webhook_url) as response:
            return response.status == 200


# Запуск WebHook и обработчик
async def on_start_webhook(request):
    # Установим WebHook
    await set_webhook()
    return web.Response(status=200)


# Создаем aiohttp приложение
app = web.Application()
app.router.add_post('/webhook', on_start)
app.router.add_get('/set-webhook', on_start_webhook)

if __name__ == "__main__":
    web.run_app(app)