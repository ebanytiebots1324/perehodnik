import os
import sqlite3
from datetime import datetime
import pytz
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = '8692515951:AAFoPto-22C9rilnMJHAif36bXvUDm08nP4'

ADMINS = ['CH4EBYRAHKA', 'Kyrsanik', 'dmitriiiy_22']
HIDE_CHEBURASHKA = ['ch4ebyrahka', 'annaapanfilova1', 'kyrsanik', 'pepechili']

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Бот работает!'

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('./users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def save_user(user_id, username, first_name):
    try:
        conn = sqlite3.connect('./users.db')
        conn.execute('INSERT OR REPLACE INTO users (user_id, username, first_name, last_seen) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
                     (user_id, username or '', first_name or ''))
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
    return username and username in ADMINS

def hide_cheburashka(username):
    return username and username in HIDE_CHEBURASHKA

# ========== КЛАВИАТУРЫ (ТОЧНО КАК НА СКРИНШОТЕ) ==========
def get_menu(username):
    keyboard = [
        [InlineKeyboardButton('👻 Духлес | Поиск по номеру 📱', url='https://t.me/Vospominaniybazabot')],
        [InlineKeyboardButton('🕵️ Шерлок | Поиск по фото 👁', url='https://t.me/HahochnyuBot')],
        [InlineKeyboardButton('🔐 RuVPN | Безопасный VPN 🌐', url='https://t.me/ruvpn?start=partner_1860340689')],
        [InlineKeyboardButton('👗 Раздеватор | AI раздевалка 🔥', url='https://t.me/razdevator_bot?start=ref')],
        [
            InlineKeyboardButton('📸 Инста Шпион', url='https://instashpion.ru'),
            InlineKeyboardButton('👥 ВК Шпион', url='https://kogdavseti.ru')
        ],
        [InlineKeyboardButton('🎲 Генератор потех 18+ 🔞', url='https://gratzbot.app/?start=ref-7497345483')],
    ]
    
    # Глаз Чебурашки (скрыто для некоторых)
    if not hide_cheburashka(username):
        keyboard.append([InlineKeyboardButton('👁 Глаз Чебурашки 🔍', url='https://t.me/search_ot_cheburashki_bot')])
    
    # ПОЛЕЗНЫЕ БОТЫ (заголовок)
    keyboard.append([InlineKeyboardButton('⭐ ПОЛЕЗНЫЕ БОТЫ ⭐', callback_data='noop')])
    
    # 9 ботов в 2 колонки (как на скриншоте)
    bots = [
        ("💰 ПОЛУЧИТЬ ROBUX", "https://t.me/Poluchitrobux_bot?start=ref"),
        ("🥇 СТЕНДОФФ2 ГОЛДА", "https://t.me/Goldsstandoff2fbot?start=ref"),
        ("💎 BRAWL STARS ГЕМЫ", "https://t.me/Brawlgemhalyvabot?start=ref"),
        ("🎬 КИНОПОИСК/PREMIER", "https://t.me/TRIALS_for_free_bot?start=ref"),
        ("🛒 KUPER ALIEXPRESS", "https://t.me/Kuper_Aliexpress_bot?start=ref"),
        ("🔫 CS2 ХАЛЯВНЫЕ СКИНЫ", "https://t.me/Cs2skinsorbit_bot?start=ref"),
        ("⭐ TG STARS | NFT | PREMIUM", "https://t.me/Tg_stars_NFT_Tg_premium_bot?start=ref"),
        ("💳 СБЕРПРАЙМ ЗА РУБЛЬ", "https://t.me/SberPrime_Za_rub_bot?start=ref"),
        ("🎮 CS2 ПРАЙМ СТАТУС", "https://t.me/Cs2primestatus_bot?start=ref"),
    ]
    
    for i in range(0, len(bots), 2):
        row = []
        row.append(InlineKeyboardButton(bots[i][0], url=bots[i][1]))
        if i + 1 < len(bots):
            row.append(InlineKeyboardButton(bots[i+1][0], url=bots[i+1][1]))
        keyboard.append(row)
    
    # Админ-панель (только для админов)
    if is_admin(username):
        keyboard.append([InlineKeyboardButton('👑 АДМИН-ПАНЕЛЬ', callback_data='admin_panel')])
    
    return InlineKeyboardMarkup(keyboard)

# ========== ОБРАБОТЧИКИ ==========
async def start(update, context):
    user = update.effective_user
    save_user(user.id, user.username, user.first_name)
    
    text = f"""🔍 <b>ВЫБЕРИТЕ НУЖНЫЙ СЕРВИС</b> 🔍

Привет, {user.first_name or 'друг'}! 👋

👇 <b>Нажми на кнопку:</b>"""
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=get_menu(user.username))

async def callback(update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    
    if data == 'noop':
        await query.answer('⬇️ Боты ниже ⬇️', show_alert=False)
    
    elif data == 'admin_panel':
        if not is_admin(user.username):
            await query.answer('⛔ Только для админов', show_alert=True)
            return
        
        total, today, week, month, recent = get_stats()
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        
        text = f"""👑 <b>АДМИН-ПАНЕЛЬ</b>
МСК {now.strftime('%d.%m %H:%M')}

📊 Всего: <b>{total}</b> | Сегодня: <b>{today}</b>
📅 Неделя: <b>{week}</b> | Месяц: <b>{month}</b>

🕐 <b>Последние 5:</b>"""
        
        for i, (username, first_name, last_seen) in enumerate(recent, 1):
            name = first_name or 'Без имени'
            uname = f"@{username}" if username else 'нет'
            text += f"\n{i}. {name} ({uname})"
        
        keyboard = [[InlineKeyboardButton('◀️ НАЗАД', callback_data='back')]]
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'back':
        await query.edit_message_text(
            "🔍 <b>ВЫБЕРИТЕ НУЖНЫЙ СЕРВИС</b> 🔍\n\n👇 <b>Нажми на кнопку:</b>",
            parse_mode='HTML',
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
    
    print('🤖 ПЕРЕХОДНИК ЗАПУЩЕН!')
    print('👑 Админы:', ', '.join(ADMINS))
    
    app.run_polling()

if __name__ == '__main__':
    main()
