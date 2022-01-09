import json
import logging
import requests

from django.conf import settings


logger = logging.getLogger(__name__)


def send_message_to_rasa(**kwargs):
    try:
        # endpoint = f"{settings.RASA_BASE_URL}/webhooks/rest/webhook"
        endpoint = f"{settings.RASA_BASE_URL}/model/parse"
        headers = {
            'Content-Type': 'application/json'
        }
        resp = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps({'text': kwargs['message'], 'sender': kwargs['sender']})
        )
        json_resp = resp.json()
        print(json_resp)
        return json_resp
    except Exception as e:
        logger.exception(e)
        return None



