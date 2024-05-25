from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_2")
OPENAI_ORG = os.getenv("OPENAI_ORG")

# OpenAI Client init
client = OpenAI(api_key=OPENAI_API_KEY, organization=OPENAI_ORG)

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


async def summary(update: Update, context: CallbackContext) -> None:
    logger.info(f"Summary requested")
    chat = update.effective_chat

    # Open the JSON file for reading
    with open('messages.json', 'r') as file_temp:
        # Load the JSON data from the file
        history = json.load(file_temp)

    history_df = pd.DataFrame(history)
    history_df['timestamp_short'] = pd.to_datetime(history_df['timestamp'], format='%Y-%m-%dT%H:%M:%S.%f').dt.strftime(
        '%Y-%m-%d %H:%M:%S')
    history_df_trunc = history_df.query(f"chat_title == '{chat.title}'").tail(100)[
        ['timestamp_short', 'user_name', 'message_text']]

    history_df_trunc['formatted'] = (history_df_trunc['timestamp_short'] + ' '
                                     + history_df_trunc['user_name'] + ': ' + history_df_trunc['message_text'])

    chat_history_string = "\n".join(history_df_trunc['formatted'].tolist())

    instruction = """As a professional Russian chat summarizer, create a concise and comprehensive summary of the 
    provided chat history in Russian. Please adhere to the following guidelines: - Provide an overall summary of the 
    discussion. - List the main topics discussed, including who discussed each topic, formatted as bullet points.

    Example:
    Общий обзор: В чате обсуждались различные темы: поездка на дачу, новая работа и концерт.
    
    Детальный список:
    - Поездка на дачу (Иван и Евгений)
    - Новая работа (Наталья)
    - Концерт Би-2 (Геллер и Игорь)"""

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=1,
        max_tokens=512,
        top_p=1,
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": chat_history_string}
        ]
    )

    response_str = completion.choices[0].message.content
    await update.message.reply_text(response_str)


# Asynchronous function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Send me a message and I will log it.')


# Main function to create the bot
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('summary', summary))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until you press Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
