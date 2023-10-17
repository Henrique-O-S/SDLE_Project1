from flask_sqlalchemy import SQLAlchemy
import random
import string

db = SQLAlchemy()

class ShoppingList(db.Model):
    id = db.Column(db.String, primary_key=True)  # Use a string as the primary key for the URL
    name = db.Column(db.String)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    shopping_list_id = db.Column(db.String, db.ForeignKey('shopping_list.id'))



def get_shopping_list_by_id(shopping_list_id):
    return ShoppingList.query.get(shopping_list_id)

def get_shopping_lists():
    return ShoppingList.query.all()

def get_items_in_shopping_list(shopping_list_id):
    return Item.query.filter_by(shopping_list_id=shopping_list_id).all()

def get_random_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))