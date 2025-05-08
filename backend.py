from fastapi import FastAPI, Form
from database import get_users, save_prompt, get_prompt
from bot import bot, WEBHOOK_URL, application
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

@app.get("/")
def index():
    return {"message": "GPT Bot Backend Running"}

@app.post("/broadcast")
def broadcast(message: str = Form(...)):
    users = get_users()
    for user_id in users:
        try:
            bot.send_message(chat_id=user_id, text=message)
        except:
            pass
    return {"status": "sent", "count": len(users)}

@app.post("/prompt")
def update_prompt(prompt: str = Form(...)):
    save_prompt(prompt)
    return {"status": "updated"}

@app.get("/prompt")
def read_prompt():
    return {"prompt": get_prompt()}