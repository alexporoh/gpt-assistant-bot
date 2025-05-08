import logging
import os
from fastapi import Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TG_TOKEN, WEBHOOK_URL
from openai_handler import chat_with_gpt
from database import init_db, add_user

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TG_TOKEN)
application = Application.builder().token(TG_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    await update.message.reply_text("Привет! Я GPT-ассистент.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = chat_with_gpt(user_message)
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

init_db()

async def set_webhook():
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL + "/webhook"
    )