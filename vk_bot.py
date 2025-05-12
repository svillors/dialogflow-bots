import os
import random
import logging

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

from qwe.tg_bot.dialogflow_utils import detect_intent_texts


logger = logging.getLogger('vk_bot_logger')


class VkBotHandler(logging.Handler):

    def __init__(self, vk_api, admin_id):
        super().__init__()
        self.vk_api = vk_api
        self.admin_id = admin_id

    def emit(self, record):
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            exc_name = exc_type.__name__
            self.vk_api.messages.send(
                user_id=self.admin_id,
                message=f"Бот упал с ошибкой:\n\n{exc_name} - {exc_value}",
                random_id=random.randint(1, 1000)
            )


def answer_by_dialogflow(event, vk_api, project_id):
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
                answer_by_dialogflow(event, vk_api, project_id)
        except Exception as e:
            logger.error(e, exc_info=True)


if __name__ == "__main__":
    main()
