import logging
import sqlite3
from geo_name import get_location_name
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    phone_number TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    gender TEXT,
    address TEXT,
    latitude REAL,
    longitude REAL
)
""")
conn.commit()
conn.close()


# ====== STATES ======
PHONE_NUMBER, FIRST_NAME, LAST_NAME, AGE, GENDER, GEOLOCATION = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Telefon kontaktingizni ulashing", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        text="Salom! Telefon raqamingizni kiriting:",
        reply_markup=reply_markup
    )

    logging.info(f"user - {update.effective_user.id} started")
    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone_number'] = update.message.contact.phone_number
    await update.message.reply_text("Rahmat! Ismingiz nima?")
    return FIRST_NAME


async def first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['first_name'] = update.message.text
    await update.message.reply_text("Rahmat! Familyangiz nima?")
    return LAST_NAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_name'] = update.message.text
    await update.message.reply_text("Rahmat! Yoshingiz?")
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['age'] = update.message.text
        await update.message.reply_text("Rahmat! Jinsingiz (erkak/ayol)?")
        return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['gender'] = update.message.text
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Lokatsiyangizni ulashing", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            text="Lokatsiyangizni ulashing:",
            reply_markup=reply_markup
        )
        return GEOLOCATION

async def geolocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    address = get_location_name(latitude, longitude)

    context.user_data.update({
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
    })

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?)",
        (
            context.user_data['phone_number'],
            context.user_data['first_name'],
            context.user_data['last_name'],
            context.user_data['age'],
            context.user_data['gender'],
            context.user_data['address'],
            context.user_data['latitude'],
            context.user_data['longitude'],
        )
    )
    conn.commit()
    conn.close()

    logging.info("User Registered")

    await update.message.reply_text("Ro'yxatdan o'tganingiz uchun rahmat! ✅")
    await update.message.reply_text(
        f"""
    📱 Phone: {context.user_data['phone_number']}
    👤 First name: {context.user_data['first_name']}
    👤 Last name: {context.user_data['last_name']}
    🎂 Age: {context.user_data['age']}
    👫 Gender: {context.user_data['gender']}
    📍 Address: {context.user_data['address']}
    """
    )
    return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi!")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(
        "8376846773:AAFQRY2nfzPbjW7NI_Oza-4PXk41jargC1E"
    ).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start",start)],
        states={
            PHONE_NUMBER: [MessageHandler(filters.CONTACT, phone_number)],
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            GEOLOCATION: [MessageHandler(filters.LOCATION, geolocation)],
        },
        fallbacks=[CommandHandler("cancel",cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()