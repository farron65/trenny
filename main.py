import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from trenden_client import import_workout

import sys

from config import BOT_TOKEN, ALLOWED_USER_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

if not BOT_TOKEN:
    sys.exit("BOT_TOKEN is not set. Add it to your .env file.")

only_me = filters.User(user_id=ALLOWED_USER_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text("Hi! I'm Trenny")
    
async def post_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    if update.message.text is None:
        return
    await update.message.reply_text(await import_workout(update.message.text))
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(
        CommandHandler("start", start, filters=only_me)
    )    
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & only_me, post_workout)
    )
    
    application.run_polling()