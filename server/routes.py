import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import *

# Create a Flask Blueprint
routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    return render_template('index.html')


@routes.route('/admin')
def admin():
    # Retrieve the shopping list and its associated items based on the ID
    shopping_lists = get_shopping_lists()

    # Pass the shopping list and items to the template for rendering
    return render_template('admin.html', shopping_lists=shopping_lists)



@routes.route('/shopping_list', methods=['GET', 'POST', 'DELETE'])
def shopping_list():
    if request.method == 'GET':
        id = request.args.get('id')  # Get the ID from the query parameters
        shopping_list = get_list(id)
        if shopping_list is None:
            return jsonify({'type': 'warning', 'message': 'Shopping list not found'})

        items = get_items_in_list(id)

        shopping_list_data = json.dumps(shopping_list.to_dict())
        items_data = [json.dumps(item.to_dict()) for item in items]
        if items_data == "[]":
            items_data = "[{}]"
        print(shopping_list_data)

        print(items_data)

        return jsonify({'type': 'success', 'message': 'Shopping list found', 'shopping_list': shopping_list_data, 'items': items_data})
    elif request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        id = data.get('id')
        if not name:
            return jsonify({'type': 'warning', 'message': 'Shopping list name is required'})

        
        new_list = ShoppingList(id=id, name=name)
        db.session.add(new_list)
        db.session.commit()

        flash('Shopping list created successfully', 'success')
        return jsonify({'type': 'success', 'message': 'Shopping list Created'})
    elif request.method == 'DELETE':
        # Get the shopping list based on the provided ID
        id = request.args.get('id')
        shopping_list = get_list(id)
        if shopping_list is None:
            return jsonify({'type': 'warning', 'message': 'Shopping list not found'})
        else:
            db.session.delete(shopping_list)
            db.session.commit()
            return jsonify({'type': 'success', 'message': 'Shopping list deleted on Server'})

@routes.route('/add_item', methods=['POST'])
def add_item():
    # Get the shopping list based on the provided ID
    data = request.get_json()
    id = data.get('id')
    shopping_list = get_list(id)
    if shopping_list is None:
        return jsonify({'type': 'warning', 'message': 'Shopping list not found'})
    else:
        name = data.get('name')
        quantity = data.get('quantity')
        if not name:
            return jsonify({'type': 'warning', 'message': 'Item name is required'})
        if not quantity or quantity == '0':
            return jsonify({'type': 'warning', 'message': 'Item quantity is required'})
        else:
            new_item = Item(name=name, quantity=quantity, shopping_list_id=id)
            db.session.add(new_item)
            db.session.commit()
            return jsonify({'type': 'success', 'message': 'Item added to shopping list'})
        
@routes.route('/shopping_lists', methods=['GET'])
def shopping_lists():
    shopping_lists = get_shopping_lists()
    shopping_lists_data = [json.dumps(shopping_list.to_dict())for shopping_list in shopping_lists]
    return jsonify({'type': 'success', 'message': 'Shopping lists found', 'shopping_lists': shopping_lists_data})



@routes.route('/view_shopping_list', methods=['GET'])
def view_shopping_list():
    if request.method == 'GET':
        id = request.args.get('id')  # Get the ID from the query parameters

        shopping_list = get_list(id)
        if shopping_list is None:
            flash('Shopping list not found', 'warning')
            return render_template('index.html')

        items = get_items_in_list(id)
        return render_template('shopping_list.html', shopping_list=shopping_list, items=items)