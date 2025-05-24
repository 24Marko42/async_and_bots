# @test_method2_programming_bot
# Импорт всех необходимых модулей и библиотек
import asyncio
import random
import json
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties

from conf import token_tg  

# Инициализация бота 
bot = Bot(token=token_tg, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Классы состояний для FSM
class EchoState(StatesGroup):
    active = State()

class TranslateStates(StatesGroup):
    choosing_lang = State()
    translating = State()

class QuizStates(StatesGroup):
    waiting_answer = State()

class GeocodeState(StatesGroup):
    active = State()

class PriceState(StatesGroup):
    active = State()

# клава

def build_kb(*rows):
    builder = ReplyKeyboardBuilder()
    for row in rows:
        builder.row(*[KeyboardButton(text=text) for text in row])
    return builder.as_markup(resize_keyboard=True)

# Главное меню
main_menu_kb = build_kb(
    ["🔄 Эхо", "⏰ Время", "📅 Дата"],
    ["🎲 Игровой помощник", "❓ Викторина"],
    ["🗺️ Геокодер", "🌐 Переводчик"],
    ["💰 Поиск товара", "🏛️ Музей"]
)

game_menu_kb = build_kb(["🎲 Кубики", "⏱️ Таймер"], ["🔙 Назад"])
dice_menu_kb = build_kb(["1d6", "2d6"], ["1d20", "🔙 Назад"])
timer_menu_kb = build_kb(["30 сек", "1 мин"], ["5 мин", "🔙 Назад"])

# Команда /start и возврат в главное меню
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=main_menu_kb)

@dp.message(F.text == "🔙 Назад")
async def cmd_back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu_kb)

# Эхо-функция
@dp.message(F.text == "🔄 Эхо")
async def echo_prompt(message: types.Message, state: FSMContext):
    await message.answer("Введите сообщение для повтора:")
    await state.set_state(EchoState.active)

@dp.message(EchoState.active)
async def echo(message: types.Message, state: FSMContext):
    await message.answer(f"Я получил сообщение: {message.text}")
    await state.clear()

# Отправка текущего времени и даты
@dp.message(F.text == "⏰ Время")
async def show_time(message: types.Message):
    await message.answer(f"Текущее время: {datetime.now():%H:%M:%S}")

@dp.message(F.text == "📅 Дата")
async def show_date(message: types.Message):
    await message.answer(f"Сегодняшняя дата: {datetime.now():%d.%m.%Y}")

# Помощник по играм: выбор действия
@dp.message(F.text == "🎲 Игровой помощник")
async def game_helper(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=game_menu_kb)

@dp.message(F.text == "🎲 Кубики")
async def choose_dice(message: types.Message):
    await message.answer("Выберите кубик:", reply_markup=dice_menu_kb)

@dp.message(F.text.in_(["1d6", "2d6", "1d20"]))
async def roll_dice(message: types.Message):
    result = {
        "1d6": random.randint(1, 6),
        "2d6": f"{random.randint(1, 6)} и {random.randint(1, 6)}",
        "1d20": random.randint(1, 20)
    }[message.text]
    await message.answer(f"Результат: {result}")

@dp.message(F.text == "⏱️ Таймер")
async def choose_timer(message: types.Message):
    await message.answer("Выберите длительность таймера:", reply_markup=timer_menu_kb)

@dp.message(F.text.in_(["30 сек", "1 мин", "5 мин"]))
async def set_timer(message: types.Message):
    seconds = {"30 сек": 30, "1 мин": 60, "5 мин": 300}[message.text]
    await message.answer(f"Таймер на {message.text} установлен")
    await asyncio.sleep(seconds)
    await message.answer(f"⏰ {message.text} истекло")

# Музей 
museum_rooms = {
    "вход": ("Добро пожаловать! Сдайте верхнюю одежду в гардероб.", ["Зал 1"]),
    "Зал 1": ("Зал древнего искусства.", ["Зал 2", "вход", "выход"]),
    "Зал 2": ("Зал средневековья.", ["Зал 3"]),
    "Зал 3": ("Зал нового времени.", ["Зал 4", "Зал 1"]),
    "Зал 4": ("Зал современного искусства.", ["выход", "Зал 1"]),
}

@dp.message(F.text == "🏛️ Музей")
async def start_museum(message: types.Message):
    await message.answer(museum_rooms["вход"][0], reply_markup=build_kb(museum_rooms["вход"][1]))

@dp.message(F.text.in_(museum_rooms))
async def museum_nav(message: types.Message):
    desc, options = museum_rooms[message.text]
    await message.answer(desc, reply_markup=build_kb(options))


# Викторина (из файла quiz.json) (не работает)
@dp.message(F.text == "❓ Викторина")
async def start_quiz(message: types.Message, state: FSMContext):
    try:
        with open("quiz.json", encoding="utf-8") as f:
            data = list(json.load(f).items())
            random.shuffle(data)
            await state.update_data(questions=data[:10], score=0, index=0)
            await ask_question(message, state)
    except Exception:
        await message.answer("Ошибка чтения файла викторины.")

async def ask_question(message, state):
    data = await state.get_data()
    if data["index"] < len(data["questions"]):
        q, _ = data["questions"][data["index"]]
        await message.answer(f"Вопрос {data['index']+1}: {q}")
        await state.set_state(QuizStates.waiting_answer)
    else:
        await message.answer(f"Результат: {data['score']}/10", reply_markup=main_menu_kb)
        await state.clear()

@dp.message(QuizStates.waiting_answer)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    _, correct = data["questions"][data["index"]]
    if message.text.strip().lower() == correct.strip().lower():
        data["score"] += 1
        await message.answer("✅ Верно!")
    else:
        await message.answer(f"❌ Неверно. Ответ: {correct}")
    data["index"] += 1
    await state.update_data(**data)
    await ask_question(message, state)

# Геокодер ("город", "улица" "номер")
@dp.message(F.text == "🗺️ Геокодер")
async def geocoder_prompt(message: types.Message, state: FSMContext):
    await message.answer("Введите адрес:")
    await state.set_state(GeocodeState.active)

@dp.message(GeocodeState.active)
async def geocoder(message: types.Message, state: FSMContext):
    query = message.text
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if not data:
                    await message.answer("Ничего не найдено")
                else:
                    lat, lon = data[0]["lat"], data[0]["lon"]
                    map_url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&size=450,450&z=15&l=map&pt={lon},{lat},pm2rdm"
                    await message.answer_photo(map_url, caption=f"📍 {query}\nКоординаты: {lat}, {lon}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
    await state.clear()

# Переводчик
@dp.message(F.text == "🌐 Переводчик")
async def translate_start(message: types.Message, state: FSMContext):
    await message.answer("Выберите направление:", reply_markup=build_kb(["🇷🇺 → 🇬🇧", "🇬🇧 → 🇷🇺"]))
    await state.set_state(TranslateStates.choosing_lang)

@dp.message(TranslateStates.choosing_lang)
async def choose_lang(message: types.Message, state: FSMContext):
    lang = "ru|en" if "🇷🇺" in message.text else "en|ru"
    await state.update_data(lang=lang)
    await message.answer("Введите текст для перевода:")
    await state.set_state(TranslateStates.translating)

@dp.message(TranslateStates.translating)
async def do_translate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mymemory.translated.net/get?q={message.text}&langpair={data['lang']}") as resp:
            result = await resp.json()
            translated = result["responseData"]["translatedText"]
            await message.answer(f"Перевод: {translated}", reply_markup=main_menu_kb)
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
