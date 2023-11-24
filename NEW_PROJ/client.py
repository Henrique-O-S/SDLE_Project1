import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")

# Example: Creating a shopping list
message = {'action': 'create_shopping_list', 'name': 'MyShoppingList'}
socket.send_json(message)
response = socket.recv_json()
print(response)

# Example: Getting shopping lists
message = {'action': 'get_shopping_lists'}
socket.send_json(message)
response = socket.recv_json()
print(response)

# Example: Creating an item
message = {'action': 'create_item', 'name': 'Item1', 'quantity': 5, 'shopping_list_id': 1}
socket.send_json(message)
response = socket.recv_json()
print(response)

# Example: Getting items for a shopping list
message = {'action': 'get_items', 'shopping_list_id': 1}
socket.send_json(message)
response = socket.recv_json()
print(response)
