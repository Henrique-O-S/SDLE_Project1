import random
import string
from flask import Blueprint, render_template, request, redirect, url_for
from models import *

# Create a Flask Blueprint
routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('index.html')

@routes.route('/admin')
def about():
    return render_template('admin.html')

@routes.route('/create_shopping_list', methods=['POST'])
def create_shopping_list():
    if request.method == 'POST':
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Create a new shopping list with the generated ID and a name
        new_list = ShoppingList(id=random_id, name="New Shopping List")
        db.session.add(new_list)
        db.session.commit()

        return redirect(url_for('routes.shopping_list', id=random_id))  # Redirect to the newly created shopping list


@routes.route('/shopping_list/<id>')
def shopping_list(id):
    # Retrieve the shopping list and its associated items based on the ID
    shopping_list = get_shopping_list_by_id(id)
    items = get_items_in_shopping_list(id)
    
    # Pass the shopping list and items to the template for rendering
    return render_template('shopping_list.html', shopping_list=shopping_list, items=items)
