# --------------------------------------------------------------

import uuid
import zmq
import json
from datetime import datetime
from db import ArmazonDB
from crdts.lists_crdt import ListsCRDT
from crdts.items_crdt import ItemsCRDT
from client.gui import ArmazonGUI

# --------------------------------------------------------------

class Client:
    def __init__(self, name = 'client'):
        self.name = name
        self.database = ArmazonDB("client/" + self.name)
        self.lists_crdt = ListsCRDT()
        self.items_crdt = {}
        self.gui = ArmazonGUI(self)

# --------------------------------------------------------------

    def connect(self, address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.IDENTITY, str(self.name).encode('utf-8'))
        self.socket.connect(address)

    def send_request(self, message):
        self.socket.send_multipart([json.dumps(message).encode('utf-8')])
        multipart_message = self.socket.recv_multipart()
        return json.loads(multipart_message[0].decode('utf-8'))
    
# --------------------------------------------------------------

    def add_shopping_list(self, name):
        id = str(uuid.uuid4())
        shopping_list = self.database.add_shopping_list(id, name)
        self.lists_crdt.add((id, name))
        self.items_crdt[id] = ItemsCRDT()
        #message = {'type': 'add_list', 'id': id, 'name': name}
        #response = self.send_request(message)
        #if response['status'] == 'OK':
        #    print('Server response: OK')
        return shopping_list

    def delete_shopping_list(self, id, name):
        self.database.delete_shopping_list(id)
        self.lists_crdt.remove((id, name))
        #message = {'type': 'remove_list', 'id': id}
        #response = self.send_request(message)
        #if response['status'] == 'OK':
        #    print('Server response: OK')

# --------------------------------------------------------------

    def add_item(self, shopping_list_id, name, quantity):
        item = self.database.add_item(name, quantity, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].add((name, quantity), timestamp)
        #message = {'type': 'add_item', 'name': name, 'quantity': quantity, 'timestamp': timestamp}
        #response = self.send_request(message)
        #if response['status'] == 'OK':
        #    print('Server response: OK')
        return item

    def update_item(self, shopping_list_id, name, quantity):
        self.database.update_item(name, quantity, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].add((name, quantity), timestamp)
        #message = {'type': 'update_item', 'name': name, 'quantity': quantity, 'timestamp': timestamp}
        #response = self.send_request(message)
        #if response['status'] == 'OK':
        #    print('Server response: OK')

    def delete_item(self, shopping_list_id, name, quantity):
        self.database.delete_item(name, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].remove((name, quantity), timestamp)
        #message = {'type': 'remove_item', 'name': name, 'quantity': quantity, 'timestamp': timestamp}
        #response = self.send_request(message)
        #if response['status'] == 'OK':
        #    print('Server response: OK')

# --------------------------------------------------------------

    def refresh(self):
        self.refresh_shopping_lists()
        for shopping_list_id in self.lists_crdt.value():
            self.refresh_items(shopping_list_id)

# --------------------------------------------------------------

    def refresh_shopping_lists(self):
        server_lists_crdt = self.server_lists_crdt()
        self.lists_crdt.merge(server_lists_crdt)
        self.update_db_lists()

    def server_lists_crdt(self):
        server_lists_crdt = ListsCRDT()
        #response = self.send_request({'type': 'refresh_lists'})
        #if response['status'] == 'OK':
        #    print('Server response: OK')
        #    for shopping_list in response['actions']:
        #        if shopping_list['type'] == 'add_list':
        #            server_lists_crdt.add((shopping_list['id'], shopping_list['name']))
        #        elif shopping_list['type'] == 'remove_list':
        #            server_lists_crdt.remove((shopping_list['id'], shopping_list['name']))
        return server_lists_crdt
    
    def update_db_lists(self):
        for element in self.lists_crdt.add_set:
            shopping_list = self.database.get_shopping_list(element[0])
            if shopping_list == None:
                self.database.add_shopping_list(element[0], element[1])
        for element in self.lists_crdt.remove_set:
            self.database.delete_shopping_list(element[0])

# --------------------------------------------------------------

    def refresh_items(self, shopping_list_id):
        server_items_crdt = self.server_items_crdt(shopping_list_id)
        self.items_crdt[shopping_list_id].merge(server_items_crdt)

    def server_items_crdt(self, shopping_list_id):
        server_items_crdt = ItemsCRDT()
        #response = self.send_request({'type': 'refresh_items', 'id': shopping_list_id})
        #if response['status'] == 'OK':
        #    print('Server response: OK')
        #    for item in response['actions']:
        #        if item['type'] == 'update_item':
        #            server_items_crdt.add((item['name'], item['quantity']), item['timestamp'])
        #        elif item['type'] == 'remove_item':
        #            server_items_crdt.remove((item['name'], item['quantity']), item['timestamp'])
        return server_items_crdt

    def update_db_items(self, shopping_list_id):
        for element in self.items_crdt[shopping_list_id].add_set:
            item = self.database.get_item(shopping_list_id, element[0])
            if item == None:
                self.database.add_item(element[0], element[1], shopping_list_id)
            else:
                self.database.update_item(element[0], element[1], shopping_list_id)
        for element in self.items_crdt[shopping_list_id].remove_set:
            self.database.delete_item(element[0], shopping_list_id)

# --------------------------------------------------------------