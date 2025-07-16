import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

BOT_TOKEN = os.getenv("7519780244:AAH82o60aEhMBkOoYcyvF3CWDz08437IxZI")
MONGO_URI = os.getenv("mongodb+srv://bstharshdeals:RhTzDtPEGMxppRln@cluster0.qkwtmlu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
FORCE_JOIN_CHANNEL = os.getenv("@Harshified")

client = MongoClient(MONGO_URI)
db = client["modbot"]
logs_collection = db["logs"]

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    try:
        member = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL, user.id)
        if member.status in ["left", "kicked"]:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚫 Please join {FORCE_JOIN_CHANNEL} to use the bot."
            )
            return
    except Exception:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Could not check join status.")
        return

    await context.bot.send_message(chat_id=chat_id, text="✅ You have access to use the bot!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Usage: /warn @user reason")
        return

    user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    reason = " ".join(context.args)
    if user:
        logs_collection.insert_one({
            "action": "warn",
            "user_id": user.id,
            "username": user.username,
            "reason": reason
        })
        await update.message.reply_text(f"⚠️ {user.mention_html()} has been warned.", parse_mode="HTML")
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    reason = " ".join(context.args)
    if user:
        logs_collection.insert_one({
            "action": "ban",
            "user_id": user.id,
            "username": user.username,
            "reason": reason
        })
        await update.message.reply_text(f"🚫 {user.mention_html()} has been banned.", parse_mode="HTML").
Reason: {reason}", parse_mode="HTML")

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗Usage: /details user_id")
        return
    try:
        user_id = int(context.args[0])
        logs = logs_collection.find({"user_id": user_id})
        msg = f"📄 Logs for user ID {user_id}:
"
        found = False
        for log in logs:
            found = True
            msg += f"{log['action'].upper()} — Reason: {log['reason']}
"
        if not found:
            msg = "❌ No logs found for this user."
        await update.message.reply_text(msg)
    except Exception:
        await update.message.reply_text("⚠️ Invalid user ID.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("details", details))
    print("✅ Bot is running...")
    app.run_polling()
