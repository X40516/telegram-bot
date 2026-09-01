"""
Oddiy, bepul (API'siz) kalit so'zga asoslangan suhbat javoblari.
Har bir qoida: (qidiriladigan so'zlar ro'yxati, mumkin bo'lgan javoblar ro'yxati)
Mos kelmasa, DEFAULT_RESPONSES dan tasodifiy javob qaytariladi.
"""

import random

RULES: list[tuple[list[str], list[str]]] = [
    (
        ["salom", "assalomu", "hi", "hello", "salom!"],
        [
            "Salom! 😊 Qandaysiz?",
            "Salom-salom! Sizga qanday yordam bera olaman?",
            "Assalomu alaykum! Xush kelibsiz 👋",
        ],
    ),
    (
        ["qalaysiz", "qalesiz", "yaxshimisiz", "ahvol"],
        [
            "Rahmat, yaxshiman! Siz-chi?",
            "Zo'r, hammasi joyida 😊 Sizning ahvolingiz qanday?",
        ],
    ),
    (
        ["ismi", "isming", "kimsan", "sen kim", "siz kim"],
        [
            "Men sizning yordamchi botingizman 🤖",
            "Men Telegram bot bo'laman, savollaringizga javob berishga harakat qilaman.",
        ],
    ),
    (
        ["rahmat", "tashakkur", "raxmat"],
        [
            "Arzimaydi! 😊",
            "Doim xizmatingizdaman!",
            "Marhamat!",
        ],
    ),
    (
        ["xayr", "ko'rishguncha", "bye", "xayrli"],
        [
            "Xayr! Yana yozing 👋",
            "Ko'rishguncha! Kuningiz yaxshi o'tsin.",
        ],
    ),
    (
        ["yordam", "help", "nima qila olasan"],
        [
            "Men /order orqali buyurtma qabul qilaman, /remind orqali eslatma qo'yaman. Yoki shunchaki suhbatlashishimiz mumkin!",
        ],
    ),
    (
        ["kim yaratdi", "seni kim yozgan", "developer", "dasturchi"],
        [
            "Meni bir dasturchi Python yordamida yaratgan 🛠️",
        ],
    ),
    (
        ["zerikdim", "zerikarli", "charchadim"],
        [
            "Unda biroz dam oling 😊 Yoki /order orqali biror narsa buyurtma qilib ko'rasizmi?",
        ],
    ),
]

DEFAULT_RESPONSES: list[str] = [
    "Tushunarli! Davom eting.",
    "Qiziq ekan, ko'proq aytib bering.",
    "Hmm, buni tushunolmadim, lekin tinglayapman 🙂",
    "Rostdanmi? Batafsilroq yozing.",
    "Bu haqida ko'proq bilishni xohlayman.",
    "Aha, davom eting!",
]


def get_response(text: str) -> str:
    """Foydalanuvchi matniga mos javobni qaytaradi."""
    lowered = text.lower()
    for keywords, responses in RULES:
        if any(keyword in lowered for keyword in keywords):
            return random.choice(responses)
    return random.choice(DEFAULT_RESPONSES)
