import zmq
import json
context = zmq.Context()
socket = context.socket(zmq.REQ)

# Set a unique identity for the client
client_identity = b'client_1'
socket.setsockopt(zmq.IDENTITY, client_identity)

socket.connect("tcp://127.0.0.1:5559")

# Example: Creating a shopping list
message = {'action': 'create_shopping_list', 
           'name': 'MyShoppingList'}
socket.send_multipart([json.dumps(message).encode('utf-8')])
multipart_message = socket.recv_multipart()
print("REQ // Raw message from broker | ", multipart_message)
response_data = json.loads(multipart_message[0].decode('utf-8'))
print(response_data)
print(response_data['message'])

""" # Example: Getting shopping lists
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
print(response) """
