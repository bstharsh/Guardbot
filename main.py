import os
from telegram import Update, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler
from pymongo import MongoClient

# ---- YOUR TOKEN AND MONGODB CONNECTION ----
BOT_TOKEN = "7519780244:AAH82o60aEhMBkOoYcyvF3CWDz08437IxZI"
MONGO_URI = "mongodb+srv://bstharshdeals:RhTzDtPEGMxppRln@cluster0.qkwtmlu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["guardbot"]
collection = db["user_logs"]
usernames = db["username_logs"]

def is_admin(member):
    return member.status in ['administrator', 'creator']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!
Please join @Harshified to use the bot."
    )

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if not is_admin(admin):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /warn <reason> (reply to user)")
        return
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    reason = " ".join(context.args)
    if user:
        await update.message.reply_text(
            f"⚠️ {user.mention_html()} has been warned.
Reason: {reason}",
            parse_mode="HTML"
        )
        collection.insert_one({
            "action": "warn",
            "user_id": user.id,
            "username": user.username,
            "reason": reason
        })

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if not is_admin(admin):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /ban <reason> (reply to user)")
        return
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    reason = " ".join(context.args)
    if user:
        await update.message.reply_text(
            f"🚫 {user.mention_html()} has been banned.
Reason: {reason}",
            parse_mode="HTML"
        )
        collection.insert_one({
            "action": "ban",
            "user_id": user.id,
            "username": user.username,
            "reason": reason
        })

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    if not is_admin(admin):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /details <user_id>")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return
    logs = collection.find({"user_id": user_id})
    msg = f"📄 Logs for user ID {user_id}:
"
    found = False
    for log in logs:
        found = True
        msg += f"{log['action'].upper()} — Reason: {log['reason']}
"
    if not found:
        msg = "ℹ️ No logs found for this user."
    await update.message.reply_text(msg)

async def track_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_member.new_chat_member.user
    if user.username:
        usernames.update_one(
            {"user_id": user.id},
            {"$set": {"username": user.username}},
            upsert=True
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("details", details))
    app.add_handler(ChatMemberHandler(track_username, ChatMemberHandler.CHAT_MEMBER))
    print("✅ Bot started successfully...")
    app.run_polling()
