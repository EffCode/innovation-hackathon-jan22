import hashlib
import logging
import secrets
import hmac

from django.conf import settings
from django.db.models import F
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.rasa import send_message_to_rasa
from core.translate import trans
from core.whatsapp import send_wa_message, prepare_product_msg, prepare_button_message
from inventory.models import Order, Inventory, CartProduct
from user.models import User
from webhook.handler import bot_handler
from webhook.utils import get_entities, get_products


logger = logging.getLogger('app_api')


class GupShupWebHook(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data
            product_id = None
            if 'type' in data:
                if data['type'] == "message":
                    if 'type' in data['payload']:
                        logger.info(data)
                        if data['payload']['type'] == 'button_reply':
                            message = data['payload']['payload']['title'].lower()
                            product_id = data['payload']['payload']['id']
                        else:
                            message = data['payload']['payload']['text'].lower()
                    else:
                        message = data['payload']['payload']['text'].lower()
                    name = data['payload']['sender']['name']
                    country_code = data['payload']['sender']['country_code']
                    sender = f"{country_code}{data['payload']['sender']['dial_code']}"
                    user, created = User.objects.get_or_create(
                        mobile=sender,
                        name=name
                    )
                    if created:
                        user.token = secrets.token_urlsafe()
                        user.save()
                    bot_handler(message, user, data['app'], product_id)
                else:
                    logger.info(data)
        except Exception as err:
            logger.exception(err)
        return Response()


class PaymentCallback(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        token = request.GET.get('token')
        user = User.objects.get(token__exact=token)
        order = request.GET.get('order_id')
        rz_invoice_id = request.GET.get('razorpay_invoice_id')
        rz_invoice_status = request.GET.get('razorpay_invoice_status')
        rz_payment_id = request.GET.get('razorpay_payment_id')
        order_obj = Order.objects.get(order_id=order)
        order_obj.payment_status = rz_invoice_status
        order_obj.rz_invoice_id = rz_invoice_id
        order_obj.rz_payment_id = rz_payment_id
        order_obj.updated_at = timezone.now()
        order_obj.save()
        for item in order_obj.order_products:
            in_product = Inventory.objects.get(
                item_code=item['product__item_code']
            )
            in_product.qty = F('qty') - item['qty']
            in_product.save()
        CartProduct.objects.filter(cart__user=user).delete()
        rz_signature = request.GET.get('razorpay_signature')
        payload = f"{order_obj.rz_py_resp['id']}|{rz_invoice_id}|{rz_invoice_status}|{rz_payment_id}"

        gen_sig = hmac.new(bytes(settings.RAZORPAY_SECRET, 'latin-1'), bytes(payload, 'latin-1'), digestmod=hashlib.sha256)
        print(str(gen_sig.hexdigest()))
        if hmac.compare_digest(rz_signature, gen_sig.hexdigest()):
            print("in if")
        # @todo verify razorpay data with signature

        message = f"*{trans('Payment Received', user.lang)}*\n" \
                  f"{trans(f'Your Order id is *{order_obj.order_id}*', user.lang)}\n" \
                  f"{trans(f'To track order you can message *status {order_obj.order_id}*', user.lang)}\n" \
                  f"{trans('Or you can click on Check Order Status', user.lang)}"
        caption = trans("Please click on Order Status button to track order", user.lang)
        option = [
            {
                "type": "text", "title": trans(f"Status {order_obj.order_id}", dest_lng=user.lang),
            }
        ]
        button_msg = prepare_button_message(
            order_obj.id,
            message,
            option,
            msg_type='text',
            caption=trans(caption, dest_lng=user.lang)
        )
        send_wa_message(user.mobile, button_msg, app_name='RealestBot')
        return redirect(f'https://wa.me/918208363833')
