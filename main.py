from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

# === Your bot token and MongoDB URI ===
BOT_TOKEN = "7519780244:AAH82o60aEhMBkOoYcyvF3CWDz08437IxZI"
MONGO_URI = "mongodb+srv://harshpvt1029:Sk6JkeQQGNIzj68l@cluster0.kiev6oo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# === Connect to MongoDB ===
client = MongoClient(MONGO_URI)
db = client["guardbot"]
collection = db["user_logs"]

# === /start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}! Please join @Harshified to use the bot."
    )

# === /warn command ===
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

# === /ban command ===
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

# === /details command ===
async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Usage: /details user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    logs = collection.find({"user_id": user_id})
    msg = f"📄 Logs for user ID {user_id}:\n"
    found = False
    for log in logs:
        found = True
        msg += f"{log['action'].upper()} — Reason: {log['reason']}\n"
    if not found:
        msg = "No logs found for this user."
    await update.message.reply_text(msg)

# === Run the bot ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("details", details))
    print("✅ Bot is running...")
    app.run_polling()
