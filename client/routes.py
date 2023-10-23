import json
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

        response = requests.post(
            server_url + 'create_shopping_list', json=payload)

        response_data = response.json()

        flash(response_data['message'], response_data['type'])

        # Redirect to the newly created shopping list
        return redirect(url_for('routes.shopping_list', id=random_id))


@routes.route('/shopping_list', methods=['GET'])
def shopping_list():
    id = request.args.get('id')  # Get the ID from the query parameters

    payload = {
        'id': id,
    }

    response = requests.post(server_url + 'shopping_list', json=payload)

    response_data = response.json()

    if response_data['type'] == 'warning':
        shopping_list = get_list(id)
        if shopping_list is None:
            flash('Shopping list not found', 'warning')
            return render_template('index.html')
        items = get_items_in_list(id)
        flash('Retrieved Shopping list from Local Storage', 'success')
        return render_template('shopping_list.html', shopping_list=shopping_list, items=items)

    shopping_list_data = response_data['shopping_list']
    items_data = response_data['items']
    print(items_data)
    shopping_list = ShoppingList.from_json(shopping_list_data)
    items = [Item.from_json(item) for item in items_data]
    for item in items:
        if not check_item_existence(item.id):
            db.session.add(item)
            db.session.commit()
    flash('Retrieved Shopping list from Server', 'success')
    return render_template('shopping_list.html', shopping_list=shopping_list, items=items)


@routes.route('/add_item', methods=['POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('item_name')
        quantity = request.form.get('item_quantity')
        id = request.form.get('id')

        if not name:
            flash('Item name is required', 'warning')
            return redirect(url_for('routes.shopping_list', id=id))
        if not quantity or quantity == '0':
            flash('Item quantity is required', 'warning')
            return redirect(url_for('routes.shopping_list', id=id))
        payload = {
            'id': id,
            'name': name,
            'quantity': quantity,
        }

    response = requests.post(server_url + 'add_item', json=payload)

    response_data = response.json()

    if response_data['type'] == 'warning':
        shopping_list = get_list(id)
        if shopping_list is None:
            flash(response_data['message'], 'warning')
            return render_template('index.html')
        new_item = Item(name=name, quantity=quantity, shopping_list_id=id)
        db.session.add(new_item)
        db.session.commit()
        flash('Added item to Local Storage', 'success')
        return redirect(url_for('routes.shopping_list', id=id))
    new_item = Item(name=name, quantity=quantity, shopping_list_id=id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('routes.shopping_list', id=id))


@routes.route('/delete_shopping_list/<id>', methods=['DELETE'])
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
