import os
import asyncio
from telethon import TelegramClient, events
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Default time-ah 10 minutes (600 seconds)
DEFAULT_DELAY = 600 
group_settings = {}

# --- DUMMY SERVER FOR KOYEB HEALTH CHECK ---
# Koyeb lines-la "Health check failed" error varama eruka indha chinna server udhavum
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    # Koyeb default-ah port 8000 thaan check pannum
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    server.serve_forever()

# Server-ah background thread-la run panrom
threading.Thread(target=run_health_server, daemon=True).start()
print("Koyeb Health Check Server started on port 8000...")

# --- TELEGRAM BOT LOGIC ---
bot = TelegramClient('autodelete_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
print("Dynamic Time Bot with 10 mins default is running successfully...")

# 1. TIME SET PANRA COMMAND
@bot.on(events.NewMessage(pattern=r'^/settime (\d+)'))
async def set_delete_time(event):
    chat_id = event.chat_id
    if event.is_private:
        await event.reply("⚠️ Idhai neenga group-la dhaan set panna mudiyum!")
        return

    sender = await event.get_sender()
    try:
        permissions = await bot.get_permissions(chat_id, sender)
        if not permissions.is_admin and not permissions.is_creator:
            await event.reply("❌ Prachana! Idhai panna ungaluku Admin power thevai.")
            return
    except Exception:
        pass

    seconds = int(event.pattern_match.group(1))
    if seconds < 5:
        await event.reply("⚠️ Minimum time 5 seconds-avadhu irukkanum!")
        return

    group_settings[chat_id] = seconds
    await event.reply(f"✅ Semma! Ippo indha group-la messages ellaam **{seconds} seconds**-la auto-delete aagum.")

# 2. CURRENT TIME CHECK PANRA COMMAND
@bot.on(events.NewMessage(pattern=r'^/status'))
async def check_status(event):
    if event.is_private:
        return
    chat_id = event.chat_id
    current_time = group_settings.get(chat_id, DEFAULT_DELAY)
    
    mins = current_time // 60
    secs = current_time % 60
    time_str = f"{mins} mins" if secs == 0 else f"{mins} mins {secs} secs" if mins > 0 else f"{secs} secs"
    
    await event.reply(f"⏱️ Ippo set aahi irukkura delete time: **{time_str}** ({current_time} seconds).")

# 3. AUTO DELETE LOGIC
@bot.on(events.NewMessage)
async def handle_new_message(event):
    if event.is_private or event.text.startswith('/'):
        return

    chat_id = event.chat_id
    delete_delay = group_settings.get(chat_id, DEFAULT_DELAY)

    await asyncio.sleep(delete_delay)
    
    try:
        await event.delete()
        print(f"[{chat_id}] Deleted message: {event.id}")
    except Exception as e:
        print(f"Error deleting message: {e}")

bot.run_until_disconnected()
