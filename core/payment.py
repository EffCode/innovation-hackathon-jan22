import logging
import uuid
import razorpay
from django.conf import settings
from django.utils import timezone
from django.db.models.functions import Cast
from django.db.models import TextField

from inventory.models import CartProduct, Order
from user.models import User

logger = logging.getLogger('app_api')


def gen_order_id():
    return uuid.uuid4().hex[:10]


def gen_payment_link(user: User, items: CartProduct):
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET)
    )
    line_items = []
    message = ""
    total = 0
    for item in items:
        total = total + (item.qty * int(item.product.price))
        message = f"{message}\n\n" \
                  f"*{item.product.name}: {item.product.brand} X {item.qty} = ₹{int(item.product.price)/100}*\n"
        line_items.append(
            {
                "name": item.product.name,
                "description": item.product.description,
                "quantity": item.qty,
                "currency": "INR",
                "amount": item.product.price,
                "type": "invoice",
            }
        )
    order_id = gen_order_id()
    data = {
        "customer": {
            "name": user.name,
            "contact": user.mobile  # request.data['contact']
        },
        "line_items": line_items,
        "type": "link",
        "currency": "INR",
        "description": message,
        "amount": total,
        "callback_url": f"{settings.BASE_URL}/callback/?token={user.token}&order_id={order_id}",
        "callback_method": "get"
    }
    cat_products = list(items.values(
        'product__item_code',
        'product__name',
        'product__price',
        'qty',
        'product__brand',
        'product__category__category',
        'product__color',
        'product__size',
        'cart__user_id',
        added_at=Cast('created_at', TextField()),
        updated_on=Cast('updated_at', TextField())
    ))

    link = client.invoice.create(data=data)
    logger.info(link)
    Order.objects.create(
        order_id=order_id,
        order_products=cat_products,
        rz_py_resp=link,
        created_at=timezone.now()
    )
    return {'short_link': link['short_url'], 'order_id': order_id}
