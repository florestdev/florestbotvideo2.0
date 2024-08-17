import telebot # pip install pyTelegramBotAPI
from telebot import TeleBot, types
import sqlite3, sys, pathlib
from mcrcon import MCRcon # pip install mcrcon
from MukeshAPI import api # pip install MukeshAPI

bot = TeleBot('...', protect_content=True)
path = pathlib.Path(sys.argv[0]).parent
admins = []

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    with sqlite3.connect(path / 'database.db', timeout=3.5, check_same_thread=False) as sql:
        if sql.cursor().execute(f'SELECT id FROM users WHERE id = {message.from_user.id}').fetchone() == None:
            bot.reply_to(message, f'Здарова, новичок! Добавляю тебя в датабазу.')
            sql.cursor().execute(f'INSERT INTO users VALUES (?, ?, ?, ?)', (message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))
            sql.commit()
        else:
            bot.reply_to(message, f'Ты - олд, но все равно привет)')

def rcon_sender(message: types.Message):
    try:
        with MCRcon('135.321.3.1', 'ehkere') as rcon:
            rcon.connect()
            result = rcon.command(message.text)
            bot.reply_to(message, f'Ответ от сервера: {result}')
            bot.clear_step_handler_by_chat_id(message.chat.id)
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка!\nВот она: {e}')
        bot.clear_step_handler_by_chat_id(message.chat.id)

@bot.message_handler(commands=['rcon'])
def rcon_command(message: types.Message):
    if message.from_user.id in admins:
        bot.reply_to(message, f'Пропиши команду, которую ты хочешь прописать.\nПример: tp Dimasik Stepa')
        bot.register_next_step_handler(message, rcon_sender)
    else:
        bot.reply_to(message, f'Ты не админ. Динах.')

def ai_executor(message: types.Message):
    bot.send_photo(message.chat.id, api.ai_image(message.text), 'Изображение по вашему запросу.')
    bot.clear_step_handler_by_chat_id(message.chat.id)

@bot.message_handler(commands=['ai'])
def ai_command(message: types.Message):
    bot.reply_to(message, f'Напиши запрос, по которому мы будем рисовать изображение.')
    bot.register_next_step_handler(message, ai_executor)

bot.infinity_polling()