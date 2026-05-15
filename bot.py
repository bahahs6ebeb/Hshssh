import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_IDS = [8508012498, 8225821294]
PASSWORD = "1910398591@#aA"

channels = []
members = set()
user_states = {}
user_temp_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "😎 বস যে পোস্ট করতে চান তা লিখুন এক মিনিট মধ্য আমার আর্ডারে বা আমি যে গ্রুপে বা চ্যানেল এডমিন আছি সকল গ্রুপ/চ্যানেলে আপনার মেসেজ টি পাঠাব 😻।\n\nআপনি যদি বটের এর এডমিন বা পাসওয়ার্ড না জানেন তাহলে এক্সেস নিতে পারবেন না contract admin ✆@A15287"
    await update.message.reply_text(msg)

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not channels:
        await update.message.reply_text("কোন গ্রুপ/চ্যানেল যোগ করা হয়নি।")
        return
    text = "যোগকৃত গ্রুপ/চ্যানেল লিস্ট:\n"
    for idx, ch in enumerate(channels, start=1):
        text += f"{idx}. {ch}\n"
    await update.message.reply_text(text)

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS and user_id not in members:
        await update.message.reply_text("আপনার এক্সেস নেই।")
        return
    user_states[user_id] = {"state": "waiting_post", "post_content": None}
    await update.message.reply_text("😻বস আপনি কি পোস্ট করতে চান তা শেয়ার করে দেখুন কি করি 😎")

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("😎 boss submit passward ✅")
        user_states[user_id] = {"state": "waiting_password_for_add"}
        return
    await update.message.reply_text("বস submit telegram ID")
    user_states[user_id] = {"state": "waiting_target_id", "action": "add"}

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("😎 boss submit passward ✅")
        user_states[user_id] = {"state": "waiting_password_for_ban"}
        return
    await update.message.reply_text("submit telegram id")
    user_states[user_id] = {"state": "waiting_target_id", "action": "ban"}

async def removepost_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS and user_id not in members:
        await update.message.reply_text("আপনার এক্সেস নেই।")
        return
    if not channels:
        await update.message.reply_text("কোন চ্যানেল/গ্রুপ নেই।")
        return
    keyboard = []
    for idx, ch in enumerate(channels, start=1):
        keyboard.append([InlineKeyboardButton(f"{idx}. {ch}", callback_data=f"delgroup_{idx}")])
    keyboard.append([InlineKeyboardButton("All", callback_data="delgroup_all")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "কোন কোন চ্যানেল অথবা গ্রুপ থেকে পোস্ট ডিলিট করতে চান? নিচ থেকে নির্বাচন করুন:",
        reply_markup=reply_markup
    )

async def addchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("আপনার এক্সেস নেই।")
        return
    await update.message.reply_text("চ্যানেল/গ্রুপ আইডি বা ইউজারনেম দিন (যেমন: @mychannel বা -1001234567890)")
    user_states[user_id] = {"state": "waiting_channel_id"}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state_info = user_states.get(user_id, {})
    state = state_info.get("state")
    text = update.message.text

    if state == "waiting_password_for_add" or state == "waiting_password_for_ban":
        if text != PASSWORD:
            await update.message.reply_text("password incorrect ❌")
            del user_states[user_id]
            return
        if state == "waiting_password_for_add":
            await update.message.reply_text("বস submit telegram ID")
            user_states[user_id] = {"state": "waiting_target_id", "action": "add"}
        else:
            await update.message.reply_text("submit telegram id")
            user_states[user_id] = {"state": "waiting_target_id", "action": "ban"}
        return

    if state == "waiting_target_id":
        try:
            target_id = int(text)
        except ValueError:
            await update.message.reply_text("সঠিক টেলিগ্রাম আইডি দিন (সংখ্যা)।")
            return
        action = state_info["action"]
        if action == "add":
            members.add(target_id)
            await update.message.reply_text(f"✅ {target_id} মেম্বার হিসেবে যোগ করা হয়েছে।")
        elif action == "ban":
            members.discard(target_id)
            await update.message.reply_text(f"❌ {target_id} মেম্বার থেকে বহিস্কার করা হয়েছে।")
        del user_states[user_id]
        return

    if state == "waiting_channel_id":
        if text not in channels:
            channels.append(text)
            await update.message.reply_text(f"✅ {text} যোগ করা হয়েছে।")
        else:
            await update.message.reply_text(f"⚠️ {text} আগে থেকেই আছে।")
        del user_states[user_id]
        return

    if state == "waiting_post":
        if user_id not in ADMIN_IDS and user_id not in members:
            await update.message.reply_text("আপনার এক্সেস নেই।")
            del user_states[user_id]
            return
        user_states[user_id] = {"state": "waiting_channel_selection", "post_content": text}
        if not channels:
            await update.message.reply_text("কোন গ্রুপ/চ্যানেল নেই, আগে /addchannel দিয়ে যোগ করুন।")
            del user_states[user_id]
            return
        keyboard = []
        for idx, ch in enumerate(channels, start=1):
            keyboard.append([InlineKeyboardButton(f"{idx}. {ch}", callback_data=f"select_{idx}")])
        keyboard.append([InlineKeyboardButton("All", callback_data="select_all")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "আপনি কোন কোন চ্যানেল অথবা গ্রুপে পোস্ট করতে চান? নিচ থেকে নির্বাচন করুন:",
            reply_markup=reply_markup
        )
        return

    if user_temp_ids.get(user_id, {}).get("del_groups") is not None:
        selected_groups = user_temp_ids[user_id]["del_groups"]
        total = len(selected_groups)
        deleted = 0
        failed = 0
        for idx in selected_groups:
            try:
                deleted += 1
            except:
                failed += 1
        await update.message.reply_text(f"TOTAL : {total}\nDeleted : {deleted}\nDeleted Fail : {failed}")
        del user_temp_ids[user_id]
        return

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("select_"):
        state_info = user_states.get(user_id, {})
        if state_info.get("state") != "waiting_channel_selection":
            await query.edit_message_text("পোস্ট প্রক্রিয়া সঠিকভাবে শুরু হয়নি, আবার /post দিন।")
            return
        post_content = state_info["post_content"]
        if data == "select_all":
            selected_indices = list(range(len(channels)))
        else:
            idx = int(data.split("_")[1]) - 1
            selected_indices = [idx]
        success_count = 0
        for idx in selected_indices:
            chat_id = channels[idx]
            try:
                await context.bot.send_message(chat_id=chat_id, text=post_content)
                success_count += 1
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")
        await query.edit_message_text(f"পোস্ট সম্পন্ন! মোট {len(selected_indices)}টি জায়গায় {success_count}টি সফল।")
        del user_states[user_id]

    elif data.startswith("delgroup_"):
        if data == "delgroup_all":
            selected_groups = list(range(len(channels)))
        else:
            idx = int(data.split("_")[1]) - 1
            selected_groups = [idx]
        user_temp_ids[user_id] = {"del_groups": selected_groups}
        await query.edit_message_text("কোন পোস্ট টি ডিলিট করতে চান সেটি ঠিক সেই ভাবে লিখে দিন 😶")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("add", add_command))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("removepost", removepost_command))
    app.add_handler(CommandHandler("addchannel", addchannel_command))

    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("বট চালু হচ্ছে...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
