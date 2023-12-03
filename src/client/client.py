# --------------------------------------------------------------

import uuid
import zmq
import json
from datetime import datetime
from db import ArmazonDB
from crdts import ListsCRDT, ItemsCRDT
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
        self.items_crdt = {}
        shopping_lists = self.database.get_shopping_lists()
        for shopping_list in shopping_lists:
            self.lists_crdt.add((shopping_list[0], shopping_list[1]))
            # to do: load items crdt
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
        print('SENT')
        self.socket.send_multipart([json.dumps(message).encode('utf-8')])
        multipart_message = self.socket.recv_multipart()
        #print("REQ // Raw message from broker | ", multipart_message)
        response = json.loads(multipart_message[0].decode('utf-8'))
        print('RECEIVED')
        return response

# --------------------------------------------------------------

    def get_shopping_list(self, id):
        shopping_list = self.database.get_shopping_list(id)
        if shopping_list == None:
            message = {'action': 'get_shopping_list', 'id': id}
            data = self.send_request_receive_reply(message)
            if data['status'] == 'OK':
                self.database.add_shopping_list(data['id'], data['name'])
                for item in data['items']:
                    self.database.add_item(item['name'], item['quantity'], data['id'])
        return shopping_list

    def add_shopping_list(self, name):
        id = str(uuid.uuid4())
        shopping_list = self.database.add_shopping_list(id, name)
        self.lists_crdt.add((id, name))
        self.items_crdt[id] = ItemsCRDT()
        return shopping_list

    def delete_shopping_list(self, id, name):
        self.database.delete_shopping_list(id)
        self.lists_crdt.remove((id, name))

# --------------------------------------------------------------

    def add_item(self, shopping_list_id, name, quantity):
        item = self.database.add_item(name, quantity, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].add((name, quantity), timestamp)
        return item

    def update_item(self, shopping_list_id, name, quantity):
        self.database.update_item(name, quantity, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].add((name, quantity), timestamp)

    def delete_item(self, shopping_list_id, name, quantity):
        self.database.delete_item(name, shopping_list_id)
        timestamp = datetime.now().timestamp()
        self.items_crdt[shopping_list_id].remove((name, quantity), timestamp)

# --------------------------------------------------------------

    def refresh(self):
        self.refresh_shopping_lists()
        #for shopping_list in self.lists_crdt.value():
        #    self.refresh_items(shopping_list[0])

# --------------------------------------------------------------

    def refresh_shopping_lists(self):
        backend_lists_crdt = self.lists_to_broker()
        #self.lists_crdt.removal_merge(backend_lists_crdt)
        #self.update_db_lists()

    def lists_to_broker(self):
        backend_lists_crdt = ListsCRDT()
        message = {'action': 'crdts', 'crdt': self.lists_crdt.to_json()}
        response = self.send_request_receive_reply(message)
        return backend_lists_crdt
    
    def update_db_lists(self):
        for element in self.lists_crdt.remove_set:
            self.database.delete_shopping_list(element[0])

# --------------------------------------------------------------

    def refresh_items(self, shopping_list_id):
        backend_items_crdt = self.backend_items_crdt(shopping_list_id)
        self.items_crdt[shopping_list_id].merge(backend_items_crdt)

    def backend_items_crdt(self, shopping_list_id):
        backend_items_crdt = ItemsCRDT()
        response = self.send_request({'type': 'refresh_items', 'id': shopping_list_id})
        if response['status'] == 'OK':
            print('backend response: OK')
            for item in response['actions']:
                if item['type'] == 'update_item':
                    backend_items_crdt.add((item['name'], item['quantity']), item['timestamp'])
                elif item['type'] == 'remove_item':
                    backend_items_crdt.remove((item['name'], item['quantity']), item['timestamp'])
        return backend_items_crdt

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
