# ---- ЭТА ЧАСТЬ ДЛЯ RENDER (ВЕБ-СЕРВЕР) ----
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---- ОСНОВНОЙ КОД БОТА ----
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import AsyncOpenAI

# --- НАСТРОЙКИ (бери из переменных окружения Render) ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# -------------------------------------------------------

# Проверка, что переменные заданы
if not TELEGRAM_TOKEN:
    raise ValueError("Ошибка: не найден TELEGRAM_TOKEN в переменных окружения")
if not OPENAI_API_KEY:
    raise ValueError("Ошибка: не найден OPENAI_API_KEY в переменных окружения")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и клиента OpenAI
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я GPT бот. Просто напиши мне любое сообщение, и я отвечу.")

# Обработка текстовых сообщений
@dp.message()
async def gpt_answer(message: types.Message):
    user_text = message.text
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты полезный и вежливый ассистент. Отвечай кратко и по делу."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        await message.reply(answer)
        
    except Exception as e:
        await message.reply(f"Ошибка: {e}. Проверь ключ OpenAI или баланс.")

# Запуск бота
async def main():
    print("Бот запущен и работает на Render...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()  # Запускаем Flask-сервер для Render
    asyncio.run(main())
