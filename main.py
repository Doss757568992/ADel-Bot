import os
import asyncio
from telethon import TelegramClient, events

# Environment Variables (Koyeb-la kudupom)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Delete aaga vendiya time (Seconds-la) - e.g., 60 for 1 minute
DELETE_DELAY = 30 

bot = TelegramClient('autodelete_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

print("Bot is running successfully...")

@bot.on(events.NewMessage)
async def handle_new_message(event):
    # Group illadha messages matrum Command-sh skip panna
    if event.is_private or event.text.startswith('/'):
        return

    # Message vanbapram specific time wait panni delete pannum
    await asyncio.sleep(DELETE_DELAY)
    try:
        await event.delete()
        print(f"Deleted message: {event.id} in chat: {event.chat_id}")
    except Exception as e:
        print(f"Error deleting message: {e}")

# Bot run aaitae irukka
bot.run_until_disconnected()