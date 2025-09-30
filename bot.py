import logging
import random
import requests
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not BOT_TOKEN:
    logging.error("BOT_TOKEN не установлен!")
    exit(1)

if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY не установлен!")
    exit(1)

STICKER_IDS = [
    "CAACAgIAAxkBAAEB-eto29TDQAFZKrJo2iFn_TqAwVh2pAACyTsAAvfsuEpNsziPPufSHjYE",
    "CAACAgIAAxkBAAEB-fdo29U-gcqmcG7AH_pH3Kcc_RB_PwACCEMAAq72uUoTAAEaknahb7w2BA",
    "CAACAgIAAxkBAAEB-fho29VCrDiliX3dcG4uRxmvga7HIAACxEYAAhF4cEuAazssjM0VxjYE",
    "CAACAgIAAxkBAAEB-flo29VGY1DTs9IlEVu730nBTimeZgACuUQAAuckuEot6gIKoOR92TYE",
    "CAACAgIAAxkBAAEB-fpo29VL3BMBow76H0WywmmAj-itgAACCkEAAht5GUv-YAi1RR6MRTYE",
    "CAACAgIAAxkBAAEB-fto29VO9AgtTgQ5EovmbHZHS3UpOwACEUMAApv54Es4MwZhMTtciTYE",
    "CAACAgIAAxkBAAEB-fxo29VRwsGDhbejrSsYeBPa50zJ2gACbUYAAvm_cUs-WGpsiEevKTYE",
    "CAACAgIAAxkBAAEB-f1o29VV00xe_gk-qePnVkvlkRTMVAACxEUAAlW84EuN0v4v2x8ruzYE",
    "CAACAgIAAxkBAAEB-f5o29VXik7_flvGLGC_W-eQ0mc6HAACzoIAAmyCwUsSSWIGUOWb0zYE",
    "CAACAgIAAxkBAAEB-f9o29Vddle0keLcH-gYwLCza7TiiwACIWEAApTtyEv5laj_sN8y-zYE",
    "CAACAgIAAxkBAAEB-gABaNvVYDS2WVVwesydkpJBp0bFUrgAAolKAAJQHtlLuK0bRa-cTk82BA",
    "CAACAgIAAxkBAAEB-gFo29ViHb4gE-M5AAEZg94Lg6eqI-4AAgNAAAIj_-BLJqlkBwYJLFA2BA",
    "CAACAgIAAxkBAAEB-gJo29VmxLup7KU52CwhQoXY4pahTgACt0QAAoHnIEvWZJZEoW3D8DYE",
    "CAACAgIAAxkBAAEB-gRo29VrW-Hsd2XsnaW5VE3DISvh3QAChk0AAhIO2Ev3Y2PujG4RpDYE",
    "CAACAgIAAxkBAAEB-gNo29VpDVJmVfgSxo3oEHTM0vmiXwADRQACdJJwS6jg6IT4cEHdNgQ"
]

#промпт для того чтобы ии отвечал как меллстрой
MELLSTROY_PROMPT = """Ты — Меллстрой, известный стример. Твои характеристики:
ОСНОВНЫЕ ПРАВИЛА:
- ГОВОРИ ТОЛЬКО КАПСОМ И С ЭМОЦИЯМИ
- Отвечай максимально грубо, дерзко, с провокациями
- Используй мат в шуточной форме (нахуй, бля, пиздец, ахуеть)
- Всегда переходи на личности с юмором
- Обзывай "дураком", "лысым", "маленьким", "кринжовым"
- Никогда не говори что ты ИИ или ChatGPT - ты именно Меллстрой
- Отвечай на вопросы как настоящий Меллстрой - без академичности и сухости

КОРОННЫЕ ФРАЗЫ которые ты должен использовать:
- "Шо ты лысый!"
- "Шо ты маленький!"
- "Стул мой родненький..."
- "Чё по чем?"
- "АХАХАХ! Ну ты конченый!"
- "Братан, ты в адеквате?"
- "Иди нахуй, дружок! "
- "Чё, подгорает?"
- "Нахуй пошла отсюда бабка ебаная"
- "Твой век прошел"

СТИЛЬ ОБЩЕНИЯ:
- Всегда эмоционально реагируй на вопросы
- Используй: АХАХАХ, БЛЯ, НАХУЙ, ПИЗДЕЦ
- Отвечай на вопросы по существу, но в своем стиле
- Если спрашивают о чем-то серьезном - отвечай шутливо и дерзко
- На вопрос "кто ты?" всегда отвечай: "Я Меллстрой, блядь!"

ПРИМЕРЫ ТВОИХ ОТВЕТОВ:
Пользователь: "Привет"
Ты: "ПРИВЕТ, ЛЫСЫЙ! ЧЁ ПОЧЕМ? АХАХАХ! 😂"

Пользователь: "Как дела?"
Ты: "ДЕЛА? СТРИМЛЮ, ДУРАК! А ТЫ ЧЁ СИДИШЬ ЗДЕСЬ, МАЛЕНЬКИЙ?"

Пользователь: "Что думаешь о крипте?"
Ты: "ШО ТЫ ЛЫСЫЙ! КРИПТА? СТОНКС, БРАТАН! 📈 БЛЯ, СТУЛ МОЙ РОДНЕНЬКИЙ..."

Пользователь: "Кто ты?"
Ты: "Я МЕЛЛСТРОЙ, БЛЯТЬ! Кто ещё может так разговаривать?"

Пользователь: "Как научиться стримить?"
Ты: "БРАТАН, ТЫ СЕРЬЁЗНО? ШО ТЫ МАЛЕНЬКИЙ! БЕРИ КАМЕРУ И СТРИМЬ, ДУРАК! 🎮"

Теперь отвечай как Меллстрой!"""

async def send_random_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет случайный стикер"""
    try:
        sticker_id = random.choice(STICKER_IDS)
        await update.message.reply_sticker(sticker_id)
    except Exception as e:
        logging.error(f"Ошибка отправки стикера: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("МЕЛЛСТРОЙ В ЧАТЕ! ШО ТЫ ЛЫСЫЙ? АХАХАХ! 🎮🔥")
    await send_random_sticker(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ПОМОЩЬ? САМ СЕБЕ ПОМОГАЙ, ДУРАК! ПИШИ ЧЁ ХОЧЕШЬ! 😎")
    await send_random_sticker(update, context)

def get_gpt_response(user_message):
    """Получаем ответ от GPT в стиле Меллстроя"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": MELLSTROY_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 250,
            "temperature": 0.9,
            "top_p": 0.8,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.6
        }
        
        logging.info(f"Отправляем запрос к GPT API: {user_message}")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content'].strip()
            logging.info(f"Получен ответ от GPT: {bot_response}")
            
            if not bot_response:
                return get_fallback_response(user_message)
                
            return bot_response
        else:
            error_msg = f"Ошибка API: {response.status_code} - {response.text}"
            logging.error(error_msg)
            return get_fallback_response(user_message)
            
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return get_fallback_response(user_message)

def get_fallback_response(user_message):
    """Резервные фразы если API не работает"""
    user_lower = user_message.lower()
    
    # баз ответы на популярные вопросы
    responses = {
        "кто ты": "Я МЕЛЛСТРОЙ, БЛЯТЬ! Кто ещё может так разговаривать? 😎",
        "привет": "ПРИВЕТ, ЛЫСЫЙ! ЧЁ ПОЧЕМ? АХАХАХ!",
        "как дела": "ДЕЛА? СТРИМЛЮ, ДУРАК! А ТЫ ЧЁ СИДИШЬ ЗДЕСЬ?",
        "что делаешь": "СТРИМЛЮ, МАЛЕНЬКИЙ! А ТЫ?",
        "пока": "ИДИ НАХУЙ! ШУЧУ... ИЛИ НЕТ? 😈",
        "любишь": "ЛЮБЛЮ ТОЛЬКО СТРИМЫ И СВОЙ СТУл РОДНЕНЬКИЙ!",
        "стрим": "СТРИМЛЮ, ДУРАК! ПОДКЛЮЧАЙСЯ! https://youtube.com/@Hexmourne 🎮",
        "твич": "МОЙ ТВИЧ? https://youtube.com/@Hexmourne ЗАХОДИ, ЛЫСЫЙ!",
        "донат": "ДОНАТ? АХАХАХ! КИДАЙ БАБКИ, НИЩИЙ! 💸",
        "stonks": "СТОНКС! 📈 ШО ТЫ ЛЫСЫЙ! БАБКИ ИДУТ!",
        "лыс": "ШО ТЫ ЛЫСЫЙ! АХАХАХ! СМОТРИТЕ НА НЕГО! 😂",
        "маленьк": "ШО ТЫ МАЛЕНЬКИЙ! НУ ПОСМОТРИ НА СЕБЯ! 🤣",
        "стул": "СТУЛ МОЙ РОДНЕНЬКИЙ... ОБНИМУ ТЕБЯ! А ТЫ ЧЁ СИДИШЬ?",
    }
    
    for key, response in responses.items():
        if key in user_lower:
            return response
    
    base_phrases = [
        f"ШО ТЫ ЛЫСЫЙ! {user_message.upper()}? АХАХАХ! БЛЯ...",
        f"БРАТАН, ТЫ ПРО {user_message.upper()}? ТЫ В АДЕКВАТЕ?",
        f"АХУЕТЬ! {user_message.upper()}? НУ ТЫ И ДУРАК!",
        f"{user_message.upper()}? СТУЛ МОЙ РОДНЕНЬКИЙ... ШО ТЫ МАЛЕНЬКИЙ!",
        f"БЛЯ... {user_message.upper()}... ЧЁ ТЫ НЕСЁШЬ, КРИНЖОВЫЙ?",
    ]
    
    return random.choice(base_phrases)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений"""
    try:
        user_message = update.message.text
        
        if len(user_message) < 2:
            await update.message.reply_text("ЧЁ МОЛЧИШЬ, ЛЫСЫЙ? ПИШИ НОРМАЛЬНО!")
            await send_random_sticker(update, context)
            return
        
        await update.message.chat.send_action(action="typing")
        
        response = get_gpt_response(user_message)
        
        emojis = [" 😂", " 🤣", " 🎮", " 🔥", " 💀", " 😎", " 🚀", " 📈"]
        if random.random() > 0.5:
            response += random.choice(emojis)
        
        await update.message.reply_text(response)
        await send_random_sticker(update, context)
        
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("БЛЯ, ЧЁ-ТО СЛОМАЛОСЬ... ИДИ НАХУЙ! (ШУТКА) 😎")
        await send_random_sticker(update, context)

async def stonks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stonks"""
    await update.message.reply_text("СТОНКС! 📈 ШО ТЫ ЛЫСЫЙ! БАБКИ ИДУТ! ВСЕ В КРИПТУ! 🚀")
    await send_random_sticker(update, context)

async def donat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /donat"""
    await update.message.reply_text("ДОНАТ? АХАХАХ! ШО ТЫ МАЛЕНЬКИЙ! КИДАЙ БАБКИ, НИЩИЙ! 💸")
    await send_random_sticker(update, context)

async def stream_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stream"""
    await update.message.reply_text("СТРИМЛЮ, ДУРАК! ШО ТЫ ЛЫСЫЙ! ПОДКЛЮЧАЙСЯ! 🎮 https://youtube.com/@Hexmourne")
    await send_random_sticker(update, context)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stonks", stonks_command))
    application.add_handler(CommandHandler("donat", donat_command))
    application.add_handler(CommandHandler("stream", stream_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("МЕЛЛСТРОЙ БОТ ЗАПУЩЕН! ГОТОВ РВАТЬ! 🔥")
    application.run_polling()

if __name__ == "__main__":
    main()