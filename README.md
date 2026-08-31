# Telegram Bot

Ko'p funksiyali Telegram bot: suhbat, buyurtma/so'rovnoma yig'ish va eslatmalar.

## Imkoniyatlar

- **Suhbat**: har qanday xabarga javob beradi (o'zingizning logikangizni qo'shishingiz mumkin)
- **Buyurtma / so'rovnoma**: `/order` buyrug'i orqali ism, telefon va mahsulotni qadam-baqadam so'raydi, natijani `orders.json` ga saqlaydi
- **Eslatma**: `/remind <daqiqa> <matn>` orqali belgilangan vaqtdan keyin xabar yuboradi

## O'rnatish

1. Repozitoriyani yuklab oling:
   ```bash
   git clone <repo-url>
   cd telegram-bot
   ```

2. Virtual muhit yarating va kutubxonalarni o'rnating:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa oling va bot tokeningizni kiriting:
   ```bash
   cp .env.example .env
   ```
   `.env` faylini oching va `BOT_TOKEN` qiymatini [@BotFather](https://t.me/BotFather) dan olingan token bilan almashtiring.

4. Botni ishga tushiring:
   ```bash
   python bot.py
   ```

## Buyruqlar

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni boshlash |
| `/help` | Yordam matni |
| `/order` | Buyurtma berish jarayonini boshlash |
| `/remind <daqiqa> <matn>` | Eslatma qo'yish |
| `/cancel` | Joriy jarayonni bekor qilish |

## Deploy qilish (ishga tushirib qo'yish)

GitHub faqat kodni saqlaydi — botni doimiy ishlatish uchun uni serverga joylashtirish kerak. Tavsiya etiladigan bepul/arzon variantlar:

- [Railway](https://railway.com/)
- [Render](https://render.com/)
- VPS (masalan DigitalOcean, Timeweb) + `systemd` yoki `screen`/`tmux`

## Texnologiyalar

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21
