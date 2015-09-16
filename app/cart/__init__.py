""" @todo: Docstring """
from satchless import cart as scart
from prices import Price
from product.models import Product


class ShoppingCart(scart.Cart):
    timestamp = None
    billing_address = None

    def __init__(self, session_cart):
        super(ShoppingCart, self).__init__()
        self.session_cart = session_cart

    @classmethod
    def for_session_cart(cls, session_cart):
        shoppingcart = ShoppingCart(session_cart)
        for item in session_cart:
            product = Product.query.get(item.data['product_id'])
            if product is None:
                continue
            quantity = item.quantity
            shoppingcart.add(product, quantity=quantity, check_quantity=False,
                    skip_session_cart=True)
        return shoppingcart

    def __str__(self):
        return "Shopping Cart, Your Cart({0})".format(self.count())

    def get_data_for_product(self, product):
        product_price = product.get_price_per_item()
        product_data = {
                'product_slug': product.get_slug(),
                'product_id': product.id_,
                'unit_price_gross': str(product_price.gross),
                'unit_price_net': str(product_price.net)}
        return product_data

    def add(self, product, quantity=1, data=None, replace=False,
            check_quantity=True, skip_session_cart=False):
        super(ShoppingCart, self).add(product, quantity, data,
                                      replace, check_quantity)
        data = self.get_data_for_product(product)
        if not skip_session_cart:
            self.session_cart.add(str(product), quantity, data,
                                  replace=replace)

    def clear(self):
        super(ShoppingCart, self).clear()
        self.session_cart.clear()


class SessionCartLine(scart.CartLine):


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
    def from_storage(cls, line_data):
        product = line_data['product']
        quantity = line_data['quantity']
        data = line_data['data']
        instance = SessionCartLine(product, quantity, data)
        return instance


class SessionCart(scart.Cart):


    def __str__(self):
        return 'SessionCart'

    @classmethod
    def from_storage(cls, cart_data):
        sessioncart = SessionCart()
        for line_data in cart_data['items']:
            sessioncart._state.append(SessionCartLine.from_storage(line_data))
        return sessioncart

    @property
    def serialize(self):
        cart_data = {'items': [i.serialize for i in self]}
        return cart_data

    def create_line(self, product, quantity, data):
        return SessionCartLine(product, quantity, data)
