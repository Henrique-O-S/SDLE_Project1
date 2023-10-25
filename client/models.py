import json
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
    @classmethod
    def from_json(cls, json_data):
        data_dict = json.loads(json_data)
        return cls(
            id=data_dict["id"],
            name=data_dict["name"]
        )
    
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    shopping_list_id = db.Column(db.String, db.ForeignKey('shopping_list.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    @classmethod
    def from_json(cls, json_data):
        print(json_data)
        if json_data == "[]":
            return None  # Handle empty JSON data
        data_dict = json.loads(json_data)
        return cls(
            id=data_dict["id"],
            name=data_dict["name"],
            quantity=data_dict["quantity"],
            shopping_list_id=data_dict["shopping_list_id"],
        )




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

def get_list_from_server(shopping_list_id):
    return ShoppingList.query.get(shopping_list_id)

def check_item_existence(item_id):
    # Check if an item with the specified item_id exists in the database
    existing_item = Item.query.filter_by(id=item_id).first()
    
    return existing_item is not None