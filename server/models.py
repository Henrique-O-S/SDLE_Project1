from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import func

db = SQLAlchemy()

class ShoppingList(db.Model):
    id = db.Column(db.String, primary_key=True)  # Use a string as the primary key for the URL
    name = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # Set the default value to the current date and time
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    shopping_list_id = db.Column(db.String, db.ForeignKey('shopping_list.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)  # Set the default value to the current date and time
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'shopping_list_id': self.shopping_list_id,
        }



def get_list(shopping_list_id):
    return ShoppingList.query.get(shopping_list_id)

def get_shopping_lists():
    return ShoppingList.query.all()

def get_items_in_list(shopping_list_id):
    return Item.query.filter_by(shopping_list_id=shopping_list_id).all()

def get_random_id():
    return str(uuid.uuid4())

