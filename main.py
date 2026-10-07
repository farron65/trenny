import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from trenden_client import import_workout, is_awake, wait_for_trenden

import sys

import re

from config import BOT_TOKEN, ALLOWED_USER_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

if not BOT_TOKEN:
    sys.exit("BOT_TOKEN is not set. Add it to your .env file.")

only_me = filters.User(user_id=ALLOWED_USER_ID)

SET_LINE = re.compile(r"^Set \d+:", re.MULTILINE)

def looks_like_workout(text: str) -> bool:
    return "\n" in text and bool(SET_LINE.search(text))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text("Hi! I'm Trenny")
    
async def post_workout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return
    
    if not looks_like_workout(update.message.text):
        await update.message.reply_text("That doesn't look like a Strong workout.")
        return
    
    if not await is_awake():
        await update.message.reply_text(
            "Trenden is waking up, this can take a couple of minutes...⌛"
        )
        if not await wait_for_trenden():
            await update.message.reply_text(
                "Trenden isn't responding. Check render."
            )
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