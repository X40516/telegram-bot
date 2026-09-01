"""
Ko'p funksiyali Telegram bot
- Suhbat / javob berish
- Buyurtma / so'rovnoma yig'ish (conversation)
- Eslatma yuborish (reminder)
- Sevishganlar uchun alohida menyu (18+ tasdiqlashdan keyin ochiladi)

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
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from chat_responses import get_response
import lovers

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "orders.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Menyular ----------

MAIN_MENU_LOVERS_BTN = "💕 Sevishganlar"
MAIN_MENU_ORDER_BTN = "📝 Buyurtma"
MAIN_MENU_HELP_BTN = "❓ Yordam"

MAIN_MENU = ReplyKeyboardMarkup(
    [
        [MAIN_MENU_LOVERS_BTN],
        [MAIN_MENU_ORDER_BTN, MAIN_MENU_HELP_BTN],
    ],
    resize_keyboard=True,
)

AGE_GATE_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("✅ Ha, men 18 yoshdan kattaman", callback_data="age_yes"),
        ],
        [
            InlineKeyboardButton("❌ Yo'q", callback_data="age_no"),
        ],
    ]
)

LOVERS_MENU = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("💌 Sevgi xabari", callback_data="love_msg"),
            InlineKeyboardButton("😊 Kompliment", callback_data="love_compliment"),
        ],
        [
            InlineKeyboardButton("📜 Iqtibos", callback_data="love_quote"),
            InlineKeyboardButton("🎲 Uchrashuv g'oyasi", callback_data="love_dateidea"),
        ],
        [
            InlineKeyboardButton("🔗 Ulanish kodim", callback_data="love_mycode"),
            InlineKeyboardButton("💑 Necha kun birgamiz", callback_data="love_together"),
        ],
        [
            InlineKeyboardButton("👤 Partnyorim", callback_data="love_partner"),
            InlineKeyboardButton("❌ Ajralish", callback_data="love_unpair"),
        ],
    ]
)


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
    lovers.get_or_create_user(update.effective_user.id)
    text = (
        "Salom! 👋 Men ko'p funksiyali botman.\n\n"
        "Pastdagi menyudan tanlang yoki quyidagi buyruqlardan foydalaning:\n"
        "/order - Buyurtma / so'rovnoma berish\n"
        "/remind <daqiqa> <matn> - Eslatma qo'yish\n"
        "/help - Yordam\n\n"
        "Yoki menga shunchaki xabar yozing, suhbatlashamiz 😊"
    )
    await update.message.reply_text(text, reply_markup=MAIN_MENU)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


# ---------- Sevishganlar menyusi (18+ tasdiqlash bilan) ----------

async def show_lovers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    lovers.get_or_create_user(user_id)

    if not lovers.is_adult(user_id):
        await update.message.reply_text(
            "🔞 Bu bo'lim faqat 18 yoshdan katta foydalanuvchilar uchun.\n\n"
            "Davom etishdan oldin yoshingizni tasdiqlang:",
            reply_markup=AGE_GATE_KEYBOARD,
        )
        return

    await update.message.reply_text(
        "💕 Sevishganlar menyusi — kerakli bo'limni tanlang:",
        reply_markup=LOVERS_MENU,
    )


async def age_gate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lovers.get_or_create_user(user_id)

    if query.data == "age_yes":
        lovers.confirm_adult(user_id)
        await query.message.reply_text(
            "Rahmat! 💕 Sevishganlar menyusi ochildi:",
            reply_markup=LOVERS_MENU,
        )
    else:
        await query.message.reply_text(
            "Tushunarli. Bu bo'lim faqat 18 yoshdan katta foydalanuvchilar uchun mavjud. "
            "Boshqa funksiyalardan (buyurtma, eslatma, suhbat) bemalol foydalanishingiz mumkin."
        )


async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanish: /pair <kod>"""
    user_id = update.effective_user.id
    lovers.get_or_create_user(user_id)

    if not lovers.is_adult(user_id):
        await update.message.reply_text(
            "🔞 Bu funksiya faqat 18 yoshdan katta foydalanuvchilar uchun. "
            "Avval /love_menu orqali yoshingizni tasdiqlang."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Foydalanish: /pair <kod>\nPartneringizning ulanish kodini kiriting."
        )
        return

    code = context.args[0]
    partner_uid = lovers.find_user_by_code(code)
    if not partner_uid:
        await update.message.reply_text("Bunday kod topilmadi. Kodni tekshirib qaytadan urinib ko'ring.")
        return

    if not lovers.is_adult(int(partner_uid)):
        await update.message.reply_text(
            "Partneringiz hali 18+ tasdiqlamagan. Ikkalangiz ham yoshni tasdiqlashingiz kerak."
        )
        return

    success = lovers.pair_users(user_id, partner_uid)
    if success:
        await update.message.reply_text("💞 Muvaffaqiyatli ulandingiz! Endi bir-biringizga sevgi xabarlari yubora olasiz.")
        try:
            await context.bot.send_message(
                chat_id=int(partner_uid),
                text="💞 Sizning partneringiz ulandi! Endi bir-biringizga sevgi xabarlari yubora olasiz.",
            )
        except Exception:
            logger.warning("Partnyorga xabar yuborib bo'lmadi: %s", partner_uid)
    else:
        await update.message.reply_text("Ulanishda xatolik yuz berdi. O'zingizning kodingizni kiritmaganingizga ishonch hosil qiling.")


async def anniversary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanish: /anniversary YYYY-MM-DD"""
    user_id = update.effective_user.id
    lovers.get_or_create_user(user_id)

    if not lovers.is_adult(user_id):
        await update.message.reply_text(
            "🔞 Bu funksiya faqat 18 yoshdan katta foydalanuvchilar uchun. "
            "Avval /love_menu orqali yoshingizni tasdiqlang."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Foydalanish: /anniversary YYYY-MM-DD\nMasalan: /anniversary 2023-05-01"
        )
        return

    date_str = context.args[0]
    if lovers.set_anniversary(user_id, date_str):
        await update.message.reply_text(f"✅ Yodgorlik sanangiz saqlandi: {date_str}")
    else:
        await update.message.reply_text("Sana formati noto'g'ri. YYYY-MM-DD formatida kiriting (masalan: 2023-05-01).")


async def lovers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lovers.get_or_create_user(user_id)

    if not lovers.is_adult(user_id):
        await query.message.reply_text(
            "🔞 Bu bo'lim faqat 18 yoshdan katta foydalanuvchilar uchun.",
            reply_markup=AGE_GATE_KEYBOARD,
        )
        return

    action = query.data

    if action == "love_msg" or action == "love_compliment":
        partner_id = lovers.get_partner_id(user_id)
        if not partner_id:
            await query.message.reply_text(
                "Hali hech kim bilan ulanmagansiz. Avval /pair <kod> orqali ulaning yoki 'Ulanish kodim' tugmasini bosing."
            )
            return
        text = lovers.random_love_message() if action == "love_msg" else lovers.random_compliment()
        try:
            await context.bot.send_message(chat_id=int(partner_id), text=f"💌 Sizga xabar bor:\n\n{text}")
            await query.message.reply_text("✅ Xabaringiz yuborildi!")
        except Exception:
            await query.message.reply_text("Xabar yuborib bo'lmadi. Partnyoringiz botni bloklagan bo'lishi mumkin.")

    elif action == "love_quote":
        await query.message.reply_text(lovers.random_quote())

    elif action == "love_dateidea":
        await query.message.reply_text(f"Bugungi g'oya:\n\n{lovers.random_date_idea()}")

    elif action == "love_mycode":
        info = lovers.get_or_create_user(user_id)
        await query.message.reply_text(
            f"Sizning ulanish kodingiz: `{info['code']}`\n\n"
            "Buni partneringizga yuboring, u esa /pair " + info["code"] + " buyrug'ini yozsin.",
            parse_mode="Markdown",
        )

    elif action == "love_together":
        anniversary = lovers.get_anniversary(user_id)
        if not anniversary:
            await query.message.reply_text(
                "Yodgorlik sanangiz kiritilmagan. /anniversary YYYY-MM-DD orqali kiriting."
            )
            return
        days = lovers.days_together(anniversary)
        await query.message.reply_text(f"💑 Siz {anniversary} dan buyon birgasiz — jami {days} kun! 🎉")

    elif action == "love_partner":
        partner_id = lovers.get_partner_id(user_id)
        if not partner_id:
            await query.message.reply_text("Hali hech kim bilan ulanmagansiz.")
        else:
            await query.message.reply_text("💑 Siz allaqachon partneringiz bilan ulangansiz.")

    elif action == "love_unpair":
        lovers.unpair_user(user_id)
        await query.message.reply_text("Ulanish bekor qilindi.")


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
        f"Mahsulot: {order['product']}",
        reply_markup=MAIN_MENU,
    )
    return ConversationHandler.END


async def order_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bekor qilindi.", reply_markup=MAIN_MENU)
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

    # Sevishganlar buyruqlari
    application.add_handler(CommandHandler("love_menu", show_lovers_menu))
    application.add_handler(CommandHandler("pair", pair_command))
    application.add_handler(CommandHandler("anniversary", anniversary_command))
    application.add_handler(CallbackQueryHandler(age_gate_callback, pattern="^age_"))
    application.add_handler(CallbackQueryHandler(lovers_callback, pattern="^love_"))

    # Asosiy menyu tugmalari (Reply Keyboard)
    application.add_handler(MessageHandler(filters.Regex(f"^{MAIN_MENU_LOVERS_BTN}$"), show_lovers_menu))
    application.add_handler(MessageHandler(filters.Regex(f"^{MAIN_MENU_HELP_BTN}$"), help_command))

    # Buyurtma conversation
    order_conv = ConversationHandler(
        entry_points=[
            CommandHandler("order", order_start),
            MessageHandler(filters.Regex(f"^{MAIN_MENU_ORDER_BTN}$"), order_start),
        ],
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
