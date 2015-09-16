from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from cart import SessionCart, ShoppingCart
from cart.forms import AddToCartForm, ReplaceCartLineForm
from product.utils import get_or_404
from product.models import Product

Cart = Blueprint('cart', __name__, url_prefix='/cart',
                 template_folder='templates',
                 static_folder='static')

import cart.admin

@Cart.route('/')
def index():
    shoppingcart = ShoppingCart.for_session_cart(request.cart)
    forms = [ReplaceCartLineForm(request.form, product=product,
        cart=shoppingcart, product_id=product.id_) for product in shoppingcart.items]
    return render_template('cart.html', cart=shoppingcart, forms=forms)

@Cart.route('/add', methods=['POST'])
def add_to_cart():
    if request.form:
        try:
            product = get_or_404(Product, request.form['product_id'])
        except KeyError:
            return redirect(request.referrer)
        shoppingcart = ShoppingCart.for_session_cart(request.cart)
        form = AddToCartForm(request.form, product=product, cart=shoppingcart)
        if form.validate():
            flash('Added {0} {1} to the cart'.format(
                form.quantity.data, product.name))
            form.save()
        return redirect(url_for('.index'))
    return redirect(request.referrer)
