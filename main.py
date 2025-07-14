import logging
from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
import os
from datetime import timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
FORCE_JOIN_CHANNEL = os.getenv("FORCE_JOIN_CHANNEL")

client = MongoClient(MONGO_URI)
db = client["guardbot"]
users_collection = db["users"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if FORCE_JOIN_CHANNEL:
        user_id = update.effective_user.id
        try:
            member = await context.bot.get_chat_member(FORCE_JOIN_CHANNEL, user_id)
            if member.status in ['left', 'kicked']:
                await update.message.reply_text(f"🚫 You must join {FORCE_JOIN_CHANNEL} to use this bot.")
                return
        except:
            await update.message.reply_text("❌ Could not verify channel join. Please check bot permissions.")
            return
    await update.message.reply_text("✅ You have access to use the bot!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to warn them.")
        return
    reason = ' '.join(context.args) or "No reason provided."
    user = update.message.reply_to_message.from_user
    users_collection.update_one(
        {"user_id": user.id},
        {"$push": {"actions": {"type": "warn", "reason": reason}}},
        upsert=True
    )
    await update.message.reply_text(f"⚠️ {user.mention_html()} has been warned.", parse_mode="HTML")
await update.message.reply_text(f"⚠️ {user.mention_html()} has been warned.\nReason: {reason}", parse_mode="HTML")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to ban them.")
        return
    reason = ' '.join(context.args) or "No reason provided."
    user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user.id)
    users_collection.update_one(
        {"user_id": user.id},
        {"$push": {"actions": {"type": "ban", "reason": reason}}},
        upsert=True
    )
    await update.message.reply_text(f"⛔ {user.mention_html()} has been banned.
Reason: {reason}", parse_mode="HTML")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or len(context.args) < 1:
        await update.message.reply_text("Usage: /mute [duration in seconds] [reason]")
        return
    duration = int(context.args[0])
    reason = ' '.join(context.args[1:]) or "No reason provided."
    user = update.message.reply_to_message.from_user
    until_date = update.message.date + timedelta(seconds=duration)
    await context.bot.restrict_chat_member(update.effective_chat.id, user.id, ChatPermissions(can_send_messages=False), until_date=until_date)
    users_collection.update_one(
        {"user_id": user.id},
        {"$push": {"actions": {"type": "mute", "duration": duration, "reason": reason}}},
        upsert=True
    )
    await update.message.reply_text(f"🔇 {user.mention_html()} has been muted for {duration} seconds.
Reason: {reason}", parse_mode="HTML")

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /details [user_id]")
        return
    try:
        uid = int(context.args[0])
        user_data = users_collection.find_one({"user_id": uid})
        if not user_data or "actions" not in user_data:
            await update.message.reply_text("❌ No data found for this user.")
            return
        actions = user_data["actions"]
        reply = f"📊 User ID: {uid}
Actions:
"
        for act in actions:
            reply += f"- {act['type'].capitalize()}: {act.get('reason', 'No reason')}
"
        await update.message.reply_text(reply)
    except ValueError:
        await update.message.reply_text("Invalid user ID.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("details", details))
    app.run_polling()
