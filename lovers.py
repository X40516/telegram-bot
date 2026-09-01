"""
Sevishganlar (juftliklar) uchun funksiyalar:
- Bir-biriga ulanish (pairing) kod orqali
- Sevgi xabari / kompliment yuborish
- Romantik iqtiboslar
- Uchrashuv g'oyalari
- Yodgorlik sanasi (anniversary) va "necha kun birgamiz" hisoblagichi
- 18+ yosh tasdiqlash

Ma'lumotlar couples.json faylida saqlanadi.
"""

import json
import os
import random
import string
from datetime import date, datetime

DATA_FILE = "couples.json"


# ---------- Ma'lumotlar bilan ishlash ----------

def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"users": {}}


def _save(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _generate_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def get_or_create_user(user_id: int) -> dict:
    data = _load()
    uid = str(user_id)
    if uid not in data["users"]:
        code = _generate_code()
        # Kodning takrorlanmasligini ta'minlash
        existing_codes = {u.get("code") for u in data["users"].values()}
        while code in existing_codes:
            code = _generate_code()
        data["users"][uid] = {
            "code": code,
            "partner_id": None,
            "anniversary": None,
            "is_adult": False,
        }
        _save(data)
    return data["users"][uid]


def find_user_by_code(code: str) -> str | None:
    data = _load()
    for uid, info in data["users"].items():
        if info.get("code") == code.upper():
            return uid
    return None


def pair_users(user_id: int, partner_uid: str) -> bool:
    """Ikki foydalanuvchini bir-biriga ulaydi. Muvaffaqiyatli bo'lsa True qaytaradi."""
    if str(user_id) == partner_uid:
        return False
    data = _load()
    uid = str(user_id)
    if uid not in data["users"] or partner_uid not in data["users"]:
        return False
    data["users"][uid]["partner_id"] = partner_uid
    data["users"][partner_uid]["partner_id"] = uid
    _save(data)
    return True


def unpair_user(user_id: int) -> None:
    data = _load()
    uid = str(user_id)
    if uid in data["users"]:
        partner_id = data["users"][uid].get("partner_id")
        data["users"][uid]["partner_id"] = None
        data["users"][uid]["anniversary"] = None
        if partner_id and partner_id in data["users"]:
            data["users"][partner_id]["partner_id"] = None
            data["users"][partner_id]["anniversary"] = None
        _save(data)


def is_adult(user_id: int) -> bool:
    data = _load()
    uid = str(user_id)
    return bool(data["users"].get(uid, {}).get("is_adult", False))


def confirm_adult(user_id: int) -> None:
    data = _load()
    uid = str(user_id)
    if uid in data["users"]:
        data["users"][uid]["is_adult"] = True
        _save(data)


def get_partner_id(user_id: int) -> str | None:
    data = _load()
    uid = str(user_id)
    if uid in data["users"]:
        return data["users"][uid].get("partner_id")
    return None


def set_anniversary(user_id: int, date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return False
    data = _load()
    uid = str(user_id)
    partner_id = data["users"].get(uid, {}).get("partner_id")
    data["users"][uid]["anniversary"] = date_str
    if partner_id and partner_id in data["users"]:
        data["users"][partner_id]["anniversary"] = date_str
    _save(data)
    return True


def get_anniversary(user_id: int) -> str | None:
    data = _load()
    uid = str(user_id)
    if uid in data["users"]:
        return data["users"][uid].get("anniversary")
    return None


def days_together(anniversary_str: str) -> int:
    anniversary = datetime.strptime(anniversary_str, "%Y-%m-%d").date()
    return (date.today() - anniversary).days


# ---------- Kontent: xabarlar, iqtiboslar, g'oyalar ----------

LOVE_MESSAGES = [
    "Sen mening kunimni yorug' qilasan ☀️💕",
    "Seni o'ylab kulib qo'ydim 😊❤️",
    "Sen bilan bo'lgan har bir lahza qadrli 💖",
    "Seni sog'indim 🥰",
    "Sen mening baxtimsan 💗",
    "Qalbimda faqat sen bor 💘",
    "Sensiz kun kunga o'xshamaydi 🌙💕",
    "Sen mening eng chiroyli tasodifimsan ✨❤️",
]

COMPLIMENTS = [
    "Sen ajoyibsan, buni bilasanmi? 😍",
    "Tabassuming kunimni yasaydi 😊",
    "Sen bilan hamma narsa osonroq 💪❤️",
    "Sen juda mehribonsan 🥰",
    "Sen menga ilhom berasan ✨",
    "Sen bilan faxrlanaman 💖",
    "Sen mukammal emassan, lekin men uchun mukammalsan 😄💕",
]

ROMANTIC_QUOTES = [
    "\"Sevgi — ikki qalbning bir urishi.\"",
    "\"Baxt — bu sevgan insoning yonida bo'lish.\"",
    "\"Sevgi masofani bilmaydi, faqat yurakni biladi.\"",
    "\"Har bir kun sen bilan yangi sarguzasht.\"",
    "\"Sevgi — sabr, ishonch va bir-birini tushunish.\"",
    "\"Eng chiroyli manzara — sevgan insoning tabassumi.\"",
]

DATE_IDEAS = [
    "🎬 Uyda kino kechasi uyushtiring, sevimli filmlaringizni tomosha qiling",
    "🍳 Birga ovqat pishiring — yangi retsept sinab ko'ring",
    "🌅 Ertalab sayrga chiqib, quyosh chiqishini birga kuzating",
    "📸 Eski suratlaringizni ko'rib, xotiralarni eslang",
    "🎨 Ikkalangiz rasm chizib, kim yaxshiroq chizishini bilib oling",
    "🚶 Yangi joyni birga kashf qiling — hali bormagan mahalla yoki park",
    "✉️ Bir-biringizga qo'lda xat yozing",
    "🎲 Birga stol o'yini o'ynang",
    "🍫 Shirinliklar bilan romantik oqshom uyushtiring",
    "🕯️ Sham yoqib, tinch oqshom o'tkazing",
]


def random_love_message() -> str:
    return random.choice(LOVE_MESSAGES)


def random_compliment() -> str:
    return random.choice(COMPLIMENTS)


def random_quote() -> str:
    return random.choice(ROMANTIC_QUOTES)


def random_date_idea() -> str:
    return random.choice(DATE_IDEAS)
