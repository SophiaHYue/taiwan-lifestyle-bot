import asyncio
import json
import logging
import os
import random
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@taiwanliving")

DATA_FILE = Path(__file__).with_name("foods.json")

with DATA_FILE.open("r", encoding="utf-8") as f:
    foods = json.load(f)

index = 0


def format_food(food: dict) -> str:
    return (
        f"🍜 {food['name']}\n"
        f"📍 地址：{food['address']}\n"
        f"✨ 特殊：{food['feature']}\n"
        f"⭐ 評價：{food['review']}\n"
        f"🖼️ 圖片：{food['image']}\n"
        f"🎥 影片：{food['video']}"
    )


def get_next_food() -> dict:
    global index
    food = foods[index % len(foods)]
    index += 1
    return food


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(
        "歡迎使用 Taiwan Lifestyle Bot！我會每30分鐘自動推送美食到頻道。"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(
        "指令清單：\n"
        "/start 啟動\n"
        "/help 說明\n"
        "/food 手動推送美食\n"
        "/about Bot簡介\n"
        "/list 顯示資料庫數量\n"
        "/random 隨機美食\n"
        "/next 下一筆美食\n"
        "/stop 停止自動推送"
    )


async def food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = get_next_food()
    await context.bot.send_message(chat_id=CHANNEL_ID, text=format_food(post))


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(
        "我是 Taiwan Lifestyle Bot，每30分鐘自動推送台灣美食到頻道。"
    )


async def list_foods(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(f"目前資料庫共有 {len(foods)} 筆美食資料。")


async def random_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = random.choice(foods)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=format_food(post))


async def next_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    post = get_next_food()
    await context.bot.send_message(chat_id=CHANNEL_ID, text=format_food(post))


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    scheduler = context.application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        await update.effective_chat.send_message("⏹️ 已停止自動推送。")
    else:
        await update.effective_chat.send_message("排程目前未啟動。")


async def auto_push(application: Application) -> None:
    post = get_next_food()
    await application.bot.send_message(chat_id=CHANNEL_ID, text=format_food(post))


async def on_startup(application: Application) -> None:
    # Initialize scheduler after event loop is running to avoid startup issues.
    scheduler = AsyncIOScheduler(event_loop=asyncio.get_running_loop())
    scheduler.add_job(auto_push, "interval", minutes=30, args=[application])
    scheduler.start()
    application.bot_data["scheduler"] = scheduler


async def on_shutdown(application: Application) -> None:
    scheduler = application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("缺少 BOT_TOKEN。請先設定環境變數 BOT_TOKEN。")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("food", food))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("list", list_foods))
    application.add_handler(CommandHandler("random", random_food))
    application.add_handler(CommandHandler("next", next_food))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()


if __name__ == "__main__":
    main()
