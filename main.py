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
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()
print("Koyeb Health Check Server started...")

# --- TELEGRAM BOT LOGIC ---
bot = TelegramClient('autodelete_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
print("Admin Delete Bot is running successfully...")


# --- 1. BOT CHAT (PRIVATE DM)-LA TIME SET PANNA ---
# Format: /settime [Group_ID] [Seconds] -> e.g., /settime -100123456789 20
@bot.on(events.NewMessage(chats=None, pattern=r'^/settime\s+(-\d+)\s+(\d+)'))
async def set_delete_time_dm(event):
    if not event.is_private:
        # Group-la potta udanae delete pannidum, settings allow pannaadhu
        await event.delete()
        return

    target_chat_id = int(event.pattern_match.group(1))
    seconds = int(event.pattern_match.group(2))

    if seconds < 5:
        await event.reply("⚠️ Minimum time 5 seconds-avadhu irukkanum!")
        return

    # Andha specific group ID-ku time-ah save panrom
    group_settings[target_chat_id] = seconds
    await event.reply(f"✅ Semma! Group ID ` {target_chat_id} `-la ippo messages ellaam **{seconds} seconds**-la auto-delete aagum (Admins sethu)!")


# --- 2. BOT CHAT (PRIVATE DM)-LA STATUS CHECK PANNA ---
# Format: /status [Group_ID] -> e.g., /status -100123456789
@bot.on(events.NewMessage(chats=None, pattern=r'^/status\s+(-\d+)'))
async def check_status_dm(event):
    if not event.is_private:
        await event.delete()
        return

    target_chat_id = int(event.pattern_match.group(1))
    current_time = group_settings.get(target_chat_id, DEFAULT_DELAY)
    
    mins = current_time // 60
    secs = current_time % 60
    time_str = f"{mins} mins" if secs == 0 else f"{mins} mins {secs} secs" if mins > 0 else f"{secs} secs"
    
    await event.reply(f"⏱️ Group ID ` {target_chat_id} `-oda delete time ippo: **{time_str}** ({current_time} seconds).")


# --- 3. AUTO DELETE LOGIC (FOR ALL USERS & ADMINS) ---
@bot.on(events.NewMessage)
async def handle_all_messages(event):
    # Chat private-ah irundhalo, commands-ah irundhalo ulla pogadhu
    if event.is_private or event.text.startswith('/'):
        return

    chat_id = event.chat_id
    delete_delay = group_settings.get(chat_id, DEFAULT_DELAY)

    # Set panna time varaikkum wait pannum
    await asyncio.sleep(delete_delay)
    
    try:
        # Inga direct-ah event.delete() tharurom, bot-ku admin right irundha ellaathayum thookkidum
        await event.delete()
        print(f"[{chat_id}] Deleted message from user/admin: {event.id}")
    except Exception as e:
        print(f"Error deleting message: {e}")

bot.run_until_disconnected()
