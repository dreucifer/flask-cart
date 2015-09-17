from satchless.item import Item
from prices import Price

from flask import url_for

from app.models import db


class PriceType(db.TypeDecorator):
    impl = db.Float

    def __init__(self, currency=None, *args, **kwargs):
        self.currency = currency
        db.TypeDecorator.__init__(self, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if isinstance(value, Price):
            return value.net
        else:
            return None

    def process_result_value(self, value, dialect):
        return Price(value, currency=self.currency)

    def copy(self):
        return PriceField(self, currency=self.currency)


class Product(Item, db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(128))
    description = db.Column(db.Text())
    price = db.Column(PriceType(currency='USD', asdecimal=True))
    weight = db.Column(db.Integer())

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        pass

    def get_slug(self):
        from unidecode import unidecode
        from smartencoding import smart_text
        from slugify import slugify
        return slugify(smart_text(unidecode(self.name)))

    def get_price_per_item(self, item, **kwargs):
        return self.price
