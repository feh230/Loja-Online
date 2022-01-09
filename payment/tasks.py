from celery import task
from io import BytesIO
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Orders


@task
def payment_completed(order_id):
    # Tarefa para enviar uma notificação por email quando um pedido é criado com sucesso
    order = Orders.objects.get(id=order_id)

    # Cria o email para a fatura
    subject = f'My shop - EE Invoice no. {order.id}'
    message = f'Please, find attached the invoice for your recent purchase'
    email = EmailMessage(subject,
                         message,
                         'felipel@nuveto.com.br',
                         [order.email])

    # Gera o PDF
    html = render_to_string('orders/ordem/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    # Anexa o arquivo PDF
    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')

    # Envia o EmailMessage
    email.send()
