import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["guardbot"]
collection = db["user_logs"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("👋 Welcome! Please join @Harshified to use the bot.")
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
    await update.message.reply_text("❗Usage: /warn @username reason")
    return
user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
reason = " ".join(context.args)
if user:
await update.message.reply_text(f"⚠️ {user.mention_html()} has been warned.", parse_mode="HTML")
await update.message.reply_text(f"Reason: {reason}", parse_mode="HTML")
collection.insert_one({
"action": "warn",
"user_id": user.id,
"username": user.username,
"reason": reason
})

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
reason = " ".join(context.args)
if user:
await update.message.reply_text(f"🚫 {user.mention_html()} has been banned.", parse_mode="HTML")
await update.message.reply_text(f"Reason: {reason}", parse_mode="HTML")
collection.insert_one({
"action": "ban",
"user_id": user.id,
"username": user.username,
"reason": reason
})

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("❗Usage: /details user_id")
return
user_id = int(context.args[0])
logs = collection.find({"user_id": user_id})
msg = f"📄 Logs for user ID {user_id}:\n"
found = False
for log in logs:
found = True
msg += f"{log['action'].upper()} — Reason: {log['reason']}\n"
if not found:
msg = "No logs found for this user."
await update.message.reply_text(msg)

if name == "main":
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("details", details))
print("✅ Bot started successfully...")
app.run_polling()
