from flask import Blueprint, render_template, abort

cart = Blueprint('cart', __name__, url_prefix='/cart')


@cart.route('/', defaults={'page': 'index'})
@cart.route('/<page>')
def show(page):
    try:
        return render_template('cart/%s.html' % page)
    except:
        abort(404)
