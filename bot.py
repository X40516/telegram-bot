"""
Ko'p funksiyali Telegram bot
- Suhbat / javob berish
- Buyurtma / so'rovnoma yig'ish (conversation)
- Eslatma yuborish (reminder)

Ishga tushirish:
    1. .env faylida BOT_TOKEN ni to'ldiring
    2. pip install -r requirements.txt
    3. python bot.py
"""

import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from chat_responses import get_response
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "orders.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Yordamchi funksiyalar ----------

def save_order(order: dict) -> None:
    """Buyurtmani JSON faylga saqlash."""
    orders = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                orders = json.load(f)
            except json.JSONDecodeError:
                orders = []
    orders.append(order)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)


# ---------- /start va /help ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Salom! 👋 Men ko'p funksiyali botman.\n\n"
        "Buyruqlar:\n"
        "/order - Buyurtma / so'rovnoma berish\n"
        "/remind <daqiqa> <matn> - Eslatma qo'yish\n"
        "/help - Yordam\n\n"
        "Yoki menga shunchaki xabar yozing, javob beraman."
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


# ---------- Oddiy suhbat / javob ----------

async def echo_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    reply = get_response(user_text)
    await update.message.reply_text(reply)


# ---------- Buyurtma / so'rovnoma (Conversation) ----------

NAME, PHONE, PRODUCT = range(3)


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Buyurtma berish uchun ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return NAME


async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return PHONE


async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Qaysi mahsulot/xizmat kerak?")
    return PRODUCT


async def order_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["product"] = update.message.text

    order = {
        "user_id": update.effective_user.id,
        "username": update.effective_user.username,
        "name": context.user_data["name"],
        "phone": context.user_data["phone"],
        "product": context.user_data["product"],
        "created_at": datetime.now().isoformat(),
    }
    save_order(order)

    await update.message.reply_text(
        "Rahmat! Buyurtmangiz qabul qilindi ✅\n\n"
        f"Ism: {order['name']}\n"
        f"Telefon: {order['phone']}\n"
        f"Mahsulot: {order['product']}"
    )
    return ConversationHandler.END


async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ---------- Eslatma (Reminder) ----------

async def remind_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=f"⏰ Eslatma: {job.data}")


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanish: /remind 5 Suvni o'chirishni unutma"""
    try:
        minutes = float(context.args[0])
        text = " ".join(context.args[1:])
        if not text:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Foydalanish: /remind <daqiqa> <matn>\nMasalan: /remind 10 Uchrashuvga borish"
        )
        return

    chat_id = update.effective_message.chat_id
    context.job_queue.run_once(
        remind_callback, minutes * 60, chat_id=chat_id, data=text
    )
    await update.message.reply_text(f"✅ {minutes} daqiqadan keyin eslataman: {text}")


# ---------- Asosiy ishga tushirish ----------

def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi. .env faylini tekshiring.")

    application = Application.builder().token(BOT_TOKEN).build()

    # Asosiy buyruqlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("remind", remind))

    # Buyurtma conversation
    order_conv = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_product)],
        },
        fallbacks=[CommandHandler("cancel", order_cancel)],
    )
    application.add_handler(order_conv)

    # Oddiy xabarlarga javob (eng oxirida bo'lishi kerak)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_reply))

    logger.info("Bot ishga tushdi...")
    application.run_polling()


if __name__ == "__main__":
    main()
