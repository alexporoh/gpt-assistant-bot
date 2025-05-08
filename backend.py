from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from database import get_users, save_prompt, get_prompt
from bot import WEBHOOK_URL, application
from telegram import Update
import csv
import io
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")

ADMIN_PASSWORD = "supersecret123"

@app.on_event("startup")
async def startup_event():
    await application.bot.set_webhook(WEBHOOK_URL + "/webhook")

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/broadcast")
def broadcast(message: str = Form(...)):
    users = get_users()
    print(f"📦 Рассылка запущена. Пользователей: {len(users)}")

    for user_id in users:
        try:
            application.bot.send_message(chat_id=user_id, text=message)
            print(f"✅ Отправлено: {user_id}")
        except Exception as e:
            print(f"❌ Ошибка {user_id}: {e}")
    return {"status": "sent", "count": len(users)}

@app.post("/prompt")
def update_prompt(prompt: str = Form(...)):
    save_prompt(prompt)
    return {"status": "updated"}

@app.get("/prompt")
def read_prompt():
    return {"prompt": get_prompt()}

@app.get("/export")
def export_users(password: str = ""):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    users = get_users()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_id"])
    for user_id in users:
        writer.writerow([user_id])
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users.csv"})

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)

    if not application.running:
        await application.initialize()

    await application.process_update(update)
    return {"ok": True}