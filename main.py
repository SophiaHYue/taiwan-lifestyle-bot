import time
from telegram import Bot

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHANNEL_ID = "@taiwanliving"

posts = [
    {
        "location": "台北市中山區 XX 咖啡館",
        "image": "https://example.com/image1.jpg",
        "video": "https://example.com/video1.mp4",
        "address": "https://maps.google.com/?q=台北市中山區XX",
        "feature": "24 小時營業，提供 AI 主題手沖咖啡"
    },
    # 更多內容...
]

bot = Bot(token=BOT_TOKEN)

def send_post(post):
    text = f"📍 {post['location']}\n🖼️ 圖片：{post['image']}\n🎥 影片：{post['video']}\n📌 地址：{post['address']}\n✨ 特殊之處：{post['feature']}"
    bot.send_message(chat_id=CHANNEL_ID, text=text)

while True:
    for post in posts:
        send_post(post)
        time.sleep(1800)  # 每30分鐘發一次
