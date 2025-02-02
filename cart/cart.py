from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon


class Cart(object):
    def __init__(self, request):
        # Inicializa o carrinho de compra
        self.session = request.session

        # Armazena o cupom aplicado no momento
        self.coupon_id = self.session.get('coupon_id')

        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # Salva um carrinho vazio na sessão
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    def add(self, product, quantity=1, override_quantity=False):
        # Adiciona um produto no carrinho de compras ou atualiza a sua quantidade
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id][quantity] += quantity
        self.save()

    def save(self):
        # Marca a sessão como 'modificada' para garantir que ela seja salva
        self.session.modified = True

    def remove(self, product):
        # Remove um produto de carrinho de compras    
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        # Itera pelos itens do carrinho de compras e obtém os produtos do banco de dados
        product_ids = self.cart.keys()
        # Obtém os objetos referentes aos produtos e os adiciona no carrinho
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        # Contabiliza todos os itens que estão no carrinho de compras

        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove o carrinho da sessão
        del self.session[settings.CART_SESSION_ID]
        self.save()
