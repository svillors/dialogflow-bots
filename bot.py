import os

from dotenv import load_dotenv
from google.cloud import dialogflow 
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")


def detect_intent_texts(project_id, session_id, text, language_code='ru'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def answer_by_dialogflow(update: Update, context: CallbackContext) -> None:
    session_id = update.effective_user.id
    answer = detect_intent_texts(PROJECT_ID, session_id, update.message.text)
    update.message.reply_text(answer)


def main() -> None:
    token = os.getenv('TG_BOT_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, answer_by_dialogflow))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
