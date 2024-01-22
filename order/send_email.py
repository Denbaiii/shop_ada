from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def sender_order_notification(user_email, order_id):
    activation_url = f'http://127.0.0.1:8000/api/order/confirm/{order_id}/'
    context = {'activation_url': activation_url}
    subject = 'Здравствуйте, подтвердите заказ!'
    html_message = render_to_string('order/order.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'admin@gmail.com',
        [user_email],
        html_message=html_message,
        fail_silently=True
    )