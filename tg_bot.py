import os
import logging

from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from qwe.tg_bot.dialogflow_utils import detect_intent_texts


logger = logging.getLogger('tg_bot_logger')


class TelegramBotHandler(logging.Handler):

    def __init__(self, updater, admin_id):
        super().__init__()
        self.udpater = updater
        self.admin_id = admin_id

    def emit(self, record):
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            exc_name = exc_type.__name__
            bot = self.udpater.bot
            bot.send_message(
                chat_id=self.admin_id,
                text=f"Бот упал с ошибкой:\n\n{exc_name} - {exc_value}"
            )


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def answer_by_dialogflow(update: Update, context: CallbackContext) -> None:
    tg_id = update.effective_user.id
    project_id = context.bot_data['project_id']
    answer = detect_intent_texts(
        project_id,
        f'tg-{tg_id}',
        update.message.text
    )
    update.message.reply_text(answer)


def main() -> None:
    load_dotenv()
    token = os.environ['TG_BOT_TOKEN']
    project_id = os.environ["PROJECT_ID"]
    admin_id = os.environ["TG_ADMIN_ID"]
    updater = Updater(token)

    logger.setLevel(logging.ERROR)
    logger.addHandler(TelegramBotHandler(updater, admin_id))

    dispatcher = updater.dispatcher
    dispatcher.bot_data['project_id'] = project_id
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command,
            answer_by_dialogflow
        )
    )
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(e, exc_info=True)


if __name__ == '__main__':
    main()
