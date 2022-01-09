from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Orders
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
# Create your views here.

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # Limpa o Carrinho
            cart.clear()
            # Dispara uma tarefa assincrona
            order_created.delay(order.id)
            # Define o pedido na sessão
            request.session['order_id'] = order.id
            # Redireciona para o pagamento
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()

    return render(request, 'orders/ordem/create.html', {'cart': cart,
                                                        'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Orders, id=order_id)

    return render(request, 'admin/orders/order/detail.html', {'order': order})


def admin_order_pdf(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    html = render_to_string('orders/ordem/pdf.html', {'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])
    return response