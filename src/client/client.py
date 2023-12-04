# --------------------------------------------------------------

import uuid
import zmq
import json
from db import ArmazonDB
from crdts import ListsCRDT
from client.gui import ArmazonGUI

# --------------------------------------------------------------

class Client:
    def __init__(self, name = 'client', port = 5559):
        self.name = name
        self.port = port
        self.database = ArmazonDB("client/databases/" + self.name)
        self.load_crdts()
        self.connect()
        self.gui = ArmazonGUI(self)
        
# --------------------------------------------------------------

    def load_crdts(self):
        self.lists_crdt = ListsCRDT()
        shopping_lists = self.database.get_shopping_lists()
        for shopping_list in shopping_lists:
            self.lists_crdt.add((shopping_list[0], shopping_list[1]))
            items = self.database.get_items(shopping_list[0])
            for item in items:
                self.lists_crdt.add_item(shopping_list[0], (item[1], item[2]), item[3])
        removed_lists = self.database.get_removed_lists()
        for removed_list in removed_lists:
            self.lists_crdt.remove((removed_list[0], removed_list[1]))

# --------------------------------------------------------------

    def connect(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.IDENTITY, str(self.name).encode('utf-8'))
        self.socket.connect(f"tcp://127.0.0.1:{self.port}")

    def send_request_receive_reply(self, message):
        self.socket.send_multipart([json.dumps(message).encode('utf-8')])
        multipart_message = self.socket.recv_multipart()
        print("\n[BROKER] > ", multipart_message)
        response = json.loads(multipart_message[0].decode('utf-8'))
        return response

# --------------------------------------------------------------

    def get_shopping_list(self, id):
        shopping_list = self.database.get_shopping_list(id)
        if shopping_list == None:
            message = {'action': 'get_shopping_list', 'id': id}
            data = self.send_request_receive_reply(message)
            if data['status'] == 'OK':
                self.database.add_shopping_list(data['id'], data['name'])
                self.lists_crdt.add((id, data['name']))
                for item in data['items']:
                    self.database.add_item(item['name'], item['quantity'], data['id'], item['timestamp'])
                    self.lists_crdt.add_item(data['id'], (item['name'], item['quantity']), item['timestamp'])
                shopping_list = self.database.get_shopping_list(id)
        return shopping_list

    def add_shopping_list(self, name):
        id = str(uuid.uuid4())
        shopping_list = self.database.add_shopping_list(id, name)
        self.lists_crdt.add((id, name))
        return shopping_list

    def delete_shopping_list(self, id, name):
        self.database.delete_shopping_list(id)
        self.lists_crdt.remove((id, name))

# --------------------------------------------------------------

    def add_item(self, shopping_list_id, name, quantity):
        item = self.database.add_item(name, quantity, shopping_list_id)
        self.lists_crdt.add_item(shopping_list_id, (name, quantity))
        return item

    def update_item(self, shopping_list_id, name, quantity):
        self.database.update_item(name, quantity, shopping_list_id)
        self.lists_crdt.add_item(shopping_list_id, (name, quantity))

    def delete_item(self, shopping_list_id, name, quantity):
        self.database.delete_item(name, shopping_list_id)
        self.lists_crdt.remove_item(shopping_list_id, (name, quantity))

# --------------------------------------------------------------

    def refresh(self):
        backend_lists_crdt = self.lists_to_broker()
        self.lists_crdt.removal_merge(backend_lists_crdt)
        self.update_db_lists()

    def lists_to_broker(self):
        crdt_json = self.lists_crdt.to_json()
        crdt_json['action'] = 'crdts'
        response = self.send_request_receive_reply(crdt_json)
        return ListsCRDT.from_json(response)
    
    def update_db_lists(self):
        for element in self.lists_crdt.remove_set:
            self.database.delete_shopping_list(element[0])
        for element in self.lists_crdt.add_set:
            self.update_db_items(element[0])
        
    def update_db_items(self, shopping_list_id):
        for item_name, (quantity, _) in self.lists_crdt.items_crdt.get(shopping_list_id).add_set.items():
            existing_item = self.database.get_item(shopping_list_id, item_name)
            if existing_item is None:
                self.database.add_item(item_name, quantity, shopping_list_id)
            else:
                self.database.update_item(item_name, quantity, shopping_list_id)
        for item_name, _ in self.lists_crdt.items_crdt.get(shopping_list_id).remove_set.items():
            self.database.delete_item(item_name, shopping_list_id)

# --------------------------------------------------------------
