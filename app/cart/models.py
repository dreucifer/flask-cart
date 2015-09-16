from satchless.item import Item
from app.models import db


class Product(Item, db.Model):
    id = db.Column(db.Integer, primary_key=True)
