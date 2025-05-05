import os
import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow
from dotenv import load_dotenv


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


def echo(event, vk_api, project_id):
    user_id = event.user_id
    text = detect_intent_texts(project_id, user_id, event.text)
    if text:
        vk_api.messages.send(
            user_id=user_id,
            message=text,
            random_id=random.randint(1, 1000)
        )


if __name__ == "__main__":
    load_dotenv()
    project_id = os.environ["PROJECT_ID"]
    vk_session = vk.VkApi(token=os.environ['VK_TOKEN'])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api, project_id)
