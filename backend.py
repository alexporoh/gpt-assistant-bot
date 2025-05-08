from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import get_users, save_prompt, get_prompt
from bot import WEBHOOK_URL, application
from telegram import Update
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/broadcast")
def broadcast(message: str = Form(...)):
    users = get_users()
    for user_id in users:
        try:
            application.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Ошибка при отправке {user_id}: {e}")
    return {"status": "sent", "count": len(users)}

@app.post("/prompt")
def update_prompt(prompt: str = Form(...)):
    save_prompt(prompt)
    return {"status": "updated"}

@app.get("/prompt")
def read_prompt():
    return {"prompt": get_prompt()}

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)

    if not application.running:
        await application.initialize()

    await application.process_update(update)
    return {"ok": True}