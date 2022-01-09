import logging
import time

from core.payment import gen_payment_link
from core.rasa import send_message_to_rasa
from core.text import add_to_cart as add_to_cart_txt, language, view_cart as view_cart_txt, confirm_order_txt
from core.translate import detect_lang, trans
from core.whatsapp import prepare_product_msg, send_wa_message
from inventory.models import CartProduct
from webhook.utils import get_entities, get_products, add_to_cart, prepare_msg_for_cart, get_cart_items, cart_view_msg, \
    send_greet_msg, send_lang_set_msg, send_address_msg, send_add_address_msg

logger = logging.getLogger('app_api')


def bot_handler(message, user, app, product_id=None):
    logger.info(trans(message, dest_lng='en', src='mr'))
    lang = detect_lang(message)
    if message in add_to_cart_txt:
        cart_msg, button_msg = add_to_cart(user, product_id)
        send_wa_message(user.mobile, cart_msg, app_name=app)
        time.sleep(1)
        send_wa_message(user.mobile, button_msg, app_name=app)
    elif trans(message, dest_lng='en', src=lang.lang).lower() in view_cart_txt:
        cart_items = get_cart_items(user, product_id)
        cart_msg = cart_view_msg(cart_items, user)
        send_wa_message(user.mobile, cart_msg, app_name=app)
    elif trans(message, dest_lng='en', src=lang.lang).lower() in confirm_order_txt:
        send_add_address_msg(user, app)
    else:
        bot_reply = send_message_to_rasa(
            message=message,
            sender=user.mobile
        )
        entities = get_entities(bot_reply)
        logger.info(entities)
        if bot_reply['intent']['name'] == "buy":
            logger.info("in if")
            inventory = get_products(entities)
            if inventory:
                logger.info(inventory)
                product_msgs = prepare_product_msg(inventory, user)
                logger.info(product_msgs)
                for product_msg in product_msgs:
                    send_wa_message(user.mobile, product_msg, app_name=app)
            else:
                logger.info("no products found")

        elif bot_reply['intent']['name'] == "greet":
            if product_id is None:
                logger.info("in greet")
                lang = detect_lang(message)
                send_greet_msg(user, lang.lang, app)
            else:
                if product_id.lower() == "en" or product_id.lower() == "mr" or product_id.lower() == "hi":
                    user.lang = language[message]
                    user.save()
                    send_lang_set_msg(user, app)

        elif bot_reply['intent']['name'] == "address":
            user.address = message
            user.save()
            # send_address_msg(user, app)
            cart_items = get_cart_items(user, product_id)
            if cart_items:
                payment_link = gen_payment_link(user, cart_items)
                msg = "Thank For Your Order!\n\n" \
                      "Please make payment on below link\n\n"
                message = {
                    'type': "text",
                    "text": f"{trans(msg, dest_lng=user.lang)}\n\n{payment_link['short_link']}"
                }
                send_wa_message(user.mobile, message, app_name=app)
        else:
            logger.info(bot_reply)
