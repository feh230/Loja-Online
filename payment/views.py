from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import braintree
from orders.models import Orders
from .tasks import payment_completed
# Create your views here.

# Instancia o gateway de pagamento Braintree
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Orders, id=order_id)
    total_cost = order.get_total_cost()

    if request.method == 'POST':
        # Obtém o nonce
        nonce = request.POST.get('payment_method_nonce', None)

        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })

        if result.is_success:
            # Marca o pedido como pago
            order.paid = True
            # Armazena o id de transação Único
            order.braintree_id = result.transaction.id
            order.save()
            # Dispara uma tarefa assincrona
            payment_completed.delay(order.id)
            return redirect('payment:done')

        else:
            return redirect('payment:canceled')
    else:
        client_token = gateway.client_token.generate()

        return render(request, 'payment/process.html', {'order': order,
                                                        'client_token': client_token})


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
