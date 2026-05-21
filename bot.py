import os
import sqlite3
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = '8692515951:AAFoPto-22C9rilnMJHAif36bXvUDm08nP4'

ADMINS = ['annaapanfilova1', 'PepeChilI', 'CH4EBYRAHKA', 'dmitriiiy_22']
EXCLUDED_USERS = ['ch4ebyrahka', 'annaapanfilova1', 'kyrsanik', 'pepechili']

# ========== ВЕБ-СЕРВЕР ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Бот работает!'

def run_flask():
    port = int(os.environ.get('PORT', 3000))
    flask_app.run(host='0.0.0.0', port=port)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('./users.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect('./users.db')
        conn.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_seen)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username or '', first_name or ''))
        conn.commit()
        conn.close()
    except:
        pass

def get_stats():
    conn = sqlite3.connect('./users.db')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM users WHERE DATE(last_seen) = DATE("now")')
    today = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM users WHERE last_seen >= datetime("now", "-7 days")')
    week = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM users WHERE last_seen >= datetime("now", "-30 days")')
    month = cur.fetchone()[0]
    cur.execute('SELECT username, first_name, last_seen FROM users ORDER BY last_seen DESC LIMIT 5')
    recent = cur.fetchall()
    conn.close()
    return total, today, week, month, recent

def is_admin(username):
    return username and username.lower() in [a.lower() for a in ADMINS]

def hide_button(username):
    return username and username.lower() in [e.lower() for e in EXCLUDED_USERS]

# ========== КЛАВИАТУРЫ ==========
def get_menu(username):
    keyboard = [
        [InlineKeyboardButton('👻 Поиск по номеру', url='https://t.me/Vospominaniybazabot')],
        [InlineKeyboardButton('🕵️ Поиск по фото', url='https://t.me/HahochnyuBot')],
        [InlineKeyboardButton('🔐 VPN', url='https://t.me/ruvpn?start=partner_1860340689')],
        [InlineKeyboardButton('📸 Instagram', url='https://instashpion.ru')],
        [InlineKeyboardButton('👥 ВКонтакте', url='https://kogdavseti.ru')],
        [InlineKeyboardButton('🎲 Генератор', url='https://gratzbot.app')],
    ]
    
    if not hide_button(username):
        keyboard.append([InlineKeyboardButton('🔍 Секретный поиск', url='https://t.me/search_ot_cheburashki_bot')])
    
    if is_admin(username):
        keyboard.append([InlineKeyboardButton('👑 АДМИН', callback_data='admin')])
    
    return InlineKeyboardMarkup(keyboard)

# ========== ОБРАБОТЧИКИ ==========
async def start(update, context):
    user = update.effective_user
    save_user(user.id, user.username, user.first_name)
    
    text = f"""
🔍 <b>ВЫБЕРИ СЕРВИС</b> 🔍

Привет, {user.first_name or 'друг'}! 👋

👇 Нажми на кнопку:
"""
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=get_menu(user.username))

async def callback(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == 'admin' and is_admin(user.username):
        total, today, week, month, recent = get_stats()
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        
        text = f"👑 АДМИН-ПАНЕЛЬ\n{now.strftime('%d.%m %H:%M')}\n\n"
        text += f"📊 Всего: {total} | Сегодня: {today}\n"
        text += f"📅 Неделя: {week} | Месяц: {month}\n\n"
        text += "🕐 Последние:\n"
        
        for i, (username, first_name, last_seen) in enumerate(recent, 1):
            name = first_name or 'Без имени'
            uname = f"@{username}" if username else 'нет'
            text += f"{i}. {name} ({uname})\n"
        
        keyboard = [[InlineKeyboardButton('◀️ НАЗАД', callback_data='back')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'back':
        await query.edit_message_text(
            "🔍 ВЫБЕРИ СЕРВИС",
            reply_markup=get_menu(user.username)
        )

# ========== ЗАПУСК ==========
def main():
    init_db()
    
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(callback))
    
    print('🤖 Переходник запущен!')
    app.run_polling()

if __name__ == '__main__':
    main()