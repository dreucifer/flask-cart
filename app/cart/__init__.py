""" @todo: Docstring """
from satchless import cart
from prices import Price


CART_SESSION_KEY = 'cart'


class Cart(cart.Cart):
    timestamp = None
    billing_address = None

    def __init__(self, session_cart):
        super(Cart, self).__init__()
        self.session_cart = session_cart

    def __str__(self):
        return "Shopping Cart, Your Cart({0})".format(self.count())

    @classmethod
    def for_session_cart(cls, session_cart):
        from .models import Product

        cart = Cart(session_cart)
        product_ids = [item.data['product_id'] for item in session_cart]
        products = Product.query.filter(Product.id in product_ids)
        product_map = dict((p.id, p) for p in products)
        for item in session_cart:
            try:
                product = product_map[item.data['product_id']]
            except KeyError:
                continue
            quantity = item.quantity
            cart.add(
                product,
                quantity=quantity,
                check_quantity=False,
                skip_session_cart=True
            )
        return cart

    def get_data_for_product(self, product):
        product_price = product.get_price_per_item()
        product_data = {
            'product_slug': product.get_slug(),
            'product_id': product.id,
            'unit_price_gross': str(product_price.gross),
            'unit_price_net': str(product_price.net)}
        return product_data

    def add(self, product, quantity=1, data=None, replace=False,
            check_quantity=True, skip_session_cart=False):
        super(Cart, self).add(product, quantity, data, replace, check_quantity)
        data = self.get_data_for_product(product)
        if not skip_session_cart:
            display = product.display_product()
            self.session_cart.add(display, quantity, data, replace=replace)

    def clear(self):
        super(Cart, self).clear()
        self.session_cart.clear()


class SessionCartLine(cart.CartLine):

    def get_price_per_item(self, **kwargs):
        gross = self.data['unit_price_gross']
        net = self.data['unit_price_net']
        return Price(gross=gross, net=net)

    @property
    def serialize(self):
        return {
            'product': self.product,
            'quantity': self.quantity,
            'data': self.data}

    @classmethod
    def from_storage(cls, data_dict):
        product = data_dict['product']
        quantity = data_dict['quantity']
        data = data_dict['data']
        instance = SessionCartLine(product, quantity, data)
        return instance


class SessionCart(cart.Cart):

    def __str__(self):
        return 'SessionCart'

    @classmethod
    def from_storage(cls, cart_data):
        cart = SessionCart()
        for line_data in cart_data['items']:
            cart._state.append(SessionCartLine.from_storage(line_data))
        return cart

    @property
    def serialize(self):
        cart_data = {'items': [i.serialize for i in self]}
        return cart_data

    def create_line(self, product, quantity, data):
        return SessionCartLine(product, quantity, data)
