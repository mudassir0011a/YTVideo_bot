from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import yt_dlp as youtube_dl
import os

# Ensure the 'downloads' folder exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# Start Command
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("Feedback", url="https://example.com")]  # Replace with a valid feedback link
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to the YouTube Video Downloader Bot! Choose an option below:",
        reply_markup=reply_markup
    )

# Handle Help Button
async def show_help(update: Update):
    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        "This bot lets you download YouTube videos. To download a video:\n"
        "1. Send the YouTube link directly in the chat.\n"
        "2. Use the buttons to confirm or cancel the download.",
        reply_markup=reply_markup
    )

# Handle Callback Actions
async def handle_callback(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await show_help(update)
    elif query.data == "main_menu":
        await start(update, context)
    elif query.data == "download":
        await query.edit_message_text("Send a YouTube link to download the video.")
    elif query.data == "cancel":
        keyboard = [
            [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Action Cancelled.", reply_markup=reply_markup)

# Download YouTube Videos
async def download_video(update: Update, context):
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        await update.message.reply_text(f"Downloading video from: {url}")

        # Video download settings
        options = {'outtmpl': 'downloads/%(title)s.%(ext)s', 'format': 'best'}
        with youtube_dl.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "video")
            file_name = ydl.prepare_filename(info)

        # Send the downloaded video
        with open(file_name, 'rb') as video_file:
            await context.bot.send_video(chat_id=chat_id, video=video_file)
        await update.message.reply_text("Here is your downloaded video!")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = ApplicationBuilder().token("7868580875:AAEejPBpzEIMsSFf2XX8hOoNQ8ehDNA5oT0").build()
    
    # Add Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Entity("url"), download_video))

    print("Bot is running...")
    app.run_polling()
