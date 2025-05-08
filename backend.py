from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from database import get_users, save_prompt, get_prompt
from bot import WEBHOOK_URL, application
from telegram import Update, error
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
async def broadcast(message: str = Form(...)):
    users = get_users()
    print(f"📦 Рассылка запущена. Пользователей в базе: {len(users)}")

    success, failed = 0, 0

    for user_id in users:
        try:
            msg = await application.bot.send_message(chat_id=user_id, text=f"[Рассылка] {message}")
            print(f"✅ Отправлено: {user_id} | msg_id: {msg.message_id}")
            success += 1
        except error.Forbidden as e:
            print(f"⛔️ Пользователь {user_id} заблокировал бота или удалён: {e}")
            failed += 1
        except error.TelegramError as e:
            print(f"❌ Telegram ошибка при отправке {user_id}: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️ Другая ошибка у {user_id}: {e}")
            failed += 1
        await asyncio.sleep(0.1)

    print(f"📊 Результат рассылки: Успешно: {success}, Ошибок: {failed}")
    return {"status": "done", "sent": success, "failed": failed}

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