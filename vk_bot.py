import os
import random
import logging

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow
from dotenv import load_dotenv


logger = logging.getLogger('vk_bot_logger')


class VkBotHandler(logging.Handler):

    def __init__(self, vk_api, admin_id):
        super().__init__()
        self.vk_api = vk_api
        self.admin_id = admin_id

    def emit(self, record):
        event = getattr(record, 'event', None)
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            exc_name = exc_type.__name__
            self.vk_api.messages.send(
                user_id=self.admin_id,
                message=f"Бот упал с ошибкой:\n\n{exc_name} - {exc_value}",
                random_id=random.randint(1, 1000)
            )
        else:
            self.vk_api.messages.send(
                user_id=event.user_id,
                message=self.format(record),
                random_id=random.randint(1, 1000)
            )


def detect_intent_texts(project_id, session_id, text, language_code='ru'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    if response.query_result.intent.is_fallback:
        return
    return response.query_result.fulfillment_text


def answer(event, vk_api, project_id):
    user_id = event.user_id
    text = detect_intent_texts(project_id, user_id, event.text)
    if text:
        vk_api.messages.send(
            user_id=user_id,
            message=text,
            random_id=random.randint(1, 1000)
        )


def main():
    load_dotenv()
    project_id = os.environ["PROJECT_ID"]
    vk_session = vk.VkApi(token=os.environ['VK_TOKEN'])
    admin_id = os.environ['VK_ADMIN_ID']
    vk_api = vk_session.get_api()

    logger.setLevel(logging.ERROR)
    logger.addHandler(VkBotHandler(vk_api, admin_id))

    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        try:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer(event, vk_api, project_id)
        except Exception as e:
            logger.error(e, exc_info=True, extra={"event": event})


if __name__ == "__main__":
    main()
