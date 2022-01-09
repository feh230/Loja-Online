from celery import task
from django.core.mail import send_mail
from .models import Orders


@task
def order_created(order_id):
    # Tarefa para enviar uma notificação por email quando um pedido for criado com sucesso

    orders = Orders.objects.get(id=order_id)
    subject = f'Order nr. {orders.id}'
    message = f'Dear {orders.first_name}, \n\n' \
              f'You have sucessfully placed an order.' \
              f'Your order ID is {orders.id}'
                
    mail_sent = send_mail(
        subject, message, 'felipel@nuveto.com.br', [orders.email])

    return mail_sent
