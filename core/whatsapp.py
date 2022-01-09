import json

import requests
from django.conf import settings

from core.translate import trans
from inventory.models import Inventory


def prepare_product_msg(inventory: Inventory, user):
    message_list = []
    options = [
        {
            "type": "text", "title": trans("ADD TO CART", dest_lng=user.lang),
        }
    ]
    for item in inventory:
        message = f"*{item.brand} {item.name}*\n\n" \
                  f"*Color: {item.color}*\n" \
                  f"*Size: {item.size}*\n" \
                  f"*Price: ₹{int(item.price)/100}*\n" \
                  f"*Description*: {item.description}"

        message_list.append(prepare_button_message(
            item.item_code, trans(message, dest_lng=user.lang), options=options, msg_type="image", url=item.image
        ))
    return message_list


def send_wa_message(destination, message: dict, source='918208363833', app_name="InventoBot"):
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': settings.API_KEY,
    }

    request_body = {
        'channel': "whatsapp",
        'source': source,
        'destination': destination,
        'message': json.dumps(message),
        'src.name': app_name,
    }
    r = requests.post(
        settings.API_ENDPOINT,
        data=request_body,
        headers=headers
    )
    print(r.json())


def prepare_button_message(code, message, options: list = None, msg_type='text', **kwargs):
    content = {
        "type": msg_type,
        "text": message,
    }
    if msg_type == 'image':
        content['url'] = kwargs['url']
    if 'caption' in kwargs:
        content['caption'] = kwargs['caption']
    return {
        "type": "quick_reply",
        "msgid": code,
        "content": content,
        "options": options
    }
