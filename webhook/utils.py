import logging
import time

from django.db.models import Q, F
from django.utils import timezone

from core.translate import trans
from core.whatsapp import prepare_button_message, send_wa_message
from inventory.models import Inventory, Cart, CartProduct

from core.text import categories, color, language
from user.models import User


logger = logging.getLogger("app_api")


def get_entities(data):
    entities = []
    if data['intent']['name'] == "buy":
        for entity in data['entities']:
            if entity['entity'] == 'category':
                entities.append({'category__category__iexact': categories[entity['value']]})
            else:
                entities.append({entity['entity']: color[entity['value']]})
    return entities


def get_products(entities):
    inventory = None
    if entities:
        if len(entities) == 2:
            query = Q(**entities[0]) | Q(**entities[1])
        else:
            query = Q(**entities[0])

        inventory = Inventory.objects.filter(query, qty__gte=0).order_by('-id')[:3]
    return inventory


def get_product_by_id(product_id):
    try:
        return Inventory.objects.get(item_code=product_id)
    except Inventory.DoesNotExist as err:
        logger.exception(f"{product_id} is not found")
        return None


def add_to_cart(user: User, product_id, qty=1):
    product = get_product_by_id(product_id)
    cart_obj = None
    cart, created = Cart.objects.get_or_create(user=user)
    if product:
        try:
            cart_obj = CartProduct.objects.get(
                cart=cart,
                product=product
            )
            cart_obj.qty = F('qty') + qty
            cart_obj.updated_at = timezone.now()
            cart_obj.save()
        except CartProduct.DoesNotExist:
            cart_obj = CartProduct.objects.create(
                cart=cart,
                product=product,
                qty=qty,
                created_at=timezone.now(),
            )
    return prepare_msg_for_cart(cart_obj, cart, user)


def prepare_msg_for_cart(cart_product, cart, user):
    message = {
        "type": "text",
    }
    if cart_product is None:
        message['text'] = trans("Please try again, something went wrong", dest_lng=user.lang)
    else:
        message['text'] = trans(
            f"*{cart_product.product.name}* is added to cart",
            dest_lng=user.lang
        )
    second_msg = trans(
        "You can add more products by messaging or sending audio here",
        dest_lng=user.lang
    )
    caption = trans(
        "click on View Cart button to see what's in your cart",
        dest_lng=user.lang
    )
    option = [
        {
            "type": "text", "title": trans("View Cart", dest_lng=user.lang)
        }
    ]
    button_msg = prepare_button_message(
        cart.id,
        second_msg,
        option,
        msg_type='text'
    )
    return message, button_msg


def get_cart_items(user, cart_id=None):
    if cart_id is None:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_id = cart.id
    return CartProduct.objects.filter(
        cart_id=cart_id
    )


def cart_view_msg(cart_items, user):
    message = "*Cart Items!*"
    total = 0
    if not cart_items:
        message = f"{trans(message, user.lang)}\n\n" + "********************\n" \
                + f"{trans('You dont have Items in cart, Please add some products', user.lang)}\n" \
                "********************"
        return {'type': "text", "text": message}
    for cart_item in cart_items:
        product_price = (int(cart_item.product.price)/100) * cart_item.qty
        total = total + product_price
        message = f"{trans(message, user.lang)}\n\n" \
                  f"*{trans(cart_item.product.name, user.lang)}: {trans(cart_item.product.brand, user.lang)} X {cart_item.qty} = ₹{product_price}*\n"

    message = f"{message}\n\n" \
              "********************\n" \
              f"*Total: ₹{total}*\n" \
              "********************"

    options = [{
            "type": "text", "title": trans("Confirm Order", dest_lng=user.lang),
    }]
    return prepare_button_message(
        cart_items[0].cart.id,
        message,
        options,
        msg_type='text',
        caption=trans("Click on Confirm Order button to proceed", dest_lng=user.lang)
    )


def send_greet_msg(user, lang, app):
    message_en = "Hello, Welcome to Gazelle & Stage Store!\n\n " \
              "Please select your preferred language."

    message_mr = "Gazelle & Stage स्टोअरमध्ये आपले स्वागत आहे.\n\n" \
                 "कृपया तुमची पसंतीची भाषा निवडा."
    message_hi = "Gazelle & Stage स्टोर में आपका स्वागत है|\n\n" \
                 "कृपया अपनी पसंदीदा भाषा चुनें।"

    options = [
        {'title': "English", 'type': "text"},
        {'title': "मराठी", 'type': "text"},
        {'title': "हिंदी", 'type': "text"}
    ]

    en_button = prepare_button_message("en", message=message_en, options=options, msg_type="text")
    mr_button = prepare_button_message("mr", message=message_mr, options=options, msg_type="text")
    hi_button = prepare_button_message("hi", message=message_hi, options=options, msg_type="text")

    if lang == "en":
        send_wa_message(user.mobile, en_button, app_name=app)
    elif lang == "mr":
        send_wa_message(user.mobile, mr_button, app_name=app)
    elif lang == "hi":
        send_wa_message(user.mobile, hi_button, app_name=app)


def send_lang_set_msg(user, app):
    message = f"Thank you! {language[user.lang]} is set as your default language."
    msg = trans(message, user.lang)
    logger.info(msg)
    logger.info(user.lang)
    send_wa_message(user.mobile, {'text': msg, 'type': 'text'}, app_name=app)
    time.sleep(1)
    second_msg = trans(
        "You can add products by messaging or sending audio here",
        dest_lng=user.lang
    )
    send_wa_message(user.mobile, {'text': second_msg, 'type': 'text'}, app_name=app)


def send_address_msg(user, app):
    message = "Address add successfully"


def send_add_address_msg(user, app):

    message = trans("Please add address to deliver the order", user.lang)

    send_wa_message(user.mobile, {'text': message, 'type': "text"}, app_name=app)

