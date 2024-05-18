from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token provided by BotFather on Telegram
TOKEN = '6835758891:AAEaqo2y77vGDF0gIQo85wQoLMZQWyGqbXg'


# Asynchronous function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat
    message_text = update.message.text.replace('\n', ' ')  # Replace newlines in messages with spaces

    logger.info(f"Message from {user.first_name} ({user.id}) in {chat.title or 'unknown chat'}: {message_text}")

    # Save message to a file
    with open('group_messages.txt', 'a', encoding='utf-8') as file:
        file.write(f"{chat.id} - {chat.title or 'Private Chat'} - {user.id} - {user.first_name}: {message_text}\n")

# Asynchronous function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Send me a message and I will log it.')

# Main function to create the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
