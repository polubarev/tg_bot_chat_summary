from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import json
from datetime import datetime
import os


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token provided by BotFather on Telegram
GIT_TOKEN = os.getenv("GIT_TOKEN")


# Load or initialize the message list
try:
    with open('messages.json', 'r') as file:
        messages = json.load(file)
except FileNotFoundError:
    messages = []


async def save_messages():
    with open('messages.json', 'w') as temp_file:
        json.dump(messages, temp_file, indent=4)


# Asynchronous function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat
    message_text = update.message.text  # .replace('\n', ' ')  # Replace newlines in messages with spaces
    # Construct the message data as a dictionary
    message_data = {
        "user_id": user.id,
        "user_name": user.first_name,
        "chat_id": chat.id,
        "chat_title": chat.title or 'Private Chat',
        "message_text": message_text,
        "timestamp": datetime.now().isoformat()
    }

    # Append message to the in-memory list
    messages.append(message_data)
    logger.info(f"Message received and stored: {message_data}")

    await save_messages()


# Asynchronous function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Send me a message and I will log it.')


# Main function to create the bot
def main() -> None:
    application = Application.builder().token(GIT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until you press Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
