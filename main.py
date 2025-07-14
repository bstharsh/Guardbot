import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

BOT_TOKEN = "7519780244:AAH82o60aEhMBkOoYcyvF3CWDz08437IxZI"
MONGO_URI = "mongodb+srv://bstharshdeals:RhTzDtPEGMxppRln@cluster0.qkwtmlu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["guardbot"]
collection = db["user_logs"]

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
    msg = f"📄 Logs for user ID {user_id}:
"
    found = False
    for log in logs:
        found = True
        action = log.get("action", "UNKNOWN").upper()
        reason = log.get("reason", "No reason provided")
        msg += f"{action} — Reason: {reason}
"
    if not found:
        msg = "No logs found for this user."
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("details", details))
    print("✅ Bot started successfully...")
    app.run_polling()
