from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import *
import requests

# Create a Flask Blueprint
routes = Blueprint('routes', __name__)

server_url = 'http://127.0.0.1:8000/'



@routes.route('/')
def home():
    return render_template('index.html')


@routes.route('/admin')
def admin():
    # Retrieve the shopping list and its associated items based on the ID
    shopping_lists = get_shopping_lists()

    # Pass the shopping list and items to the template for rendering
    return render_template('admin.html', shopping_lists=shopping_lists)


@routes.route('/create_shopping_list', methods=['POST'])
def create_shopping_list():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash('Shopping list name is required', 'error')
            return redirect(url_for('routes.home'))

        random_id = get_random_id()

        new_list = ShoppingList(id=random_id, name=name)

        db.session.add(new_list)
        db.session.commit()

        payload = {
        'id': new_list.id,
        'name': new_list.name,
        }

        response = requests.post(server_url + 'create_shopping_list', json=payload)

        response_data = response.json()

        flash(response_data['message'], response_data['type'])


        flash('Shopping list created successfully', 'success')
        return redirect(url_for('routes.shopping_list', id=random_id))  # Redirect to the newly created shopping list



@routes.route('/shopping_list/<id>')
def shopping_list(id):
    # Retrieve the shopping list and its associated items based on the ID
    shopping_list = get_shopping_list_by_id(id)

    if shopping_list is None:
        flash('Shopping list not found', 'warning')
        return render_template('index.html')

    items = get_items_in_shopping_list(id)
    return render_template('shopping_list.html', shopping_list=shopping_list, items=items)


@routes.route('/check_id', methods=['GET'])
def check_id():
    id = request.args.get('id')  # Get the ID from the query parameters
    return redirect(url_for('routes.shopping_list', id=id))

@routes.route('/add_item/<id>', methods=['POST'])
def add_item(id):
    # Get the shopping list based on the provided ID
    shopping_list = ShoppingList.query.get(id)

    if shopping_list is None:
        flash('Shopping list not found', 'warning')
    else:
        item_name = request.form.get('item_name')
        item_quantity = request.form.get('item_quantity')

        if not item_name or not item_quantity:
            flash('Item name and quantity are required', 'danger')
        else:
            new_item = Item(name=item_name, quantity=item_quantity, shopping_list_id=id)
            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully', 'success')

    return redirect(url_for('routes.shopping_list', id=id))

@routes.route('/delete_shopping_list/<id>', methods=['POST'])
def delete_shopping_list(id):
    shopping_list = ShoppingList.query.get(id)

    if shopping_list:
        # Delete the shopping list and its associated items
        db.session.delete(shopping_list)
        db.session.commit()
        flash('Shopping list deleted successfully', 'success')
    else:
        flash('Shopping list not found', 'warning')

    return redirect(url_for('routes.admin'))
