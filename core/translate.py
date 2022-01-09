from django.conf import settings

from googletrans import Translator
from google.cloud import translate_v2


def trans(text, dest_lng, src='en'):
    try:
        client = translate_v2.Client.from_service_account_json(settings.GOOGLE_KEY)
        response = client.translate(text, dest_lng, source_language=src)
        # translator = Translator()
        # result = translator.translate(text, src=src, dest=dest_lng)
        return response['translatedText']
    except Exception as err:
        return text


def detect_lang(text):
    translator = Translator()
    return translator.detect(text)


def google_trans(text):
    client = translate_v2.Client.from_service_account_json('/Users/rahul/Downloads/mumsmile-python-6e2aa5eaf54c.json')
    response = client.translate(text, 'mr', source_language='en')

    print(response)
    return response.translations

