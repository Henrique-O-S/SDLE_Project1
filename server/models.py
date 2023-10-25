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

def get_item(shopping_list_id, name):
    return Item.query.filter_by(shopping_list_id=shopping_list_id, name=name).first()

def get_shopping_lists():
    return ShoppingList.query.all()

def get_items_in_list(shopping_list_id):
    return Item.query.filter_by(shopping_list_id=shopping_list_id).all()

def get_item(item_name, shopping_list_id):
    return Item.query.get(name=item_name, shopping_list_id=shopping_list_id)

def get_random_id():
    return str(uuid.uuid4())

def update_quantity(shopping_list_id, item_id, new_quantity):
    item = Item.query.filter_by(shopping_list_id=shopping_list_id, id=item_id).first()
    item.quantity = new_quantity
    db.session.commit()


def check_item_existence(item_id):
    # Check if an item with the specified item_id exists in the database
    existing_item = Item.query.filter_by(id=item_id).first()
    
    return existing_item is not None
