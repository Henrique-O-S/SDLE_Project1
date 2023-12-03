# --------------------------------------------------------------

import zmq
import json
import sys
sys.path.append('../')
from db import ArmazonDB
from crdts import ListsCRDT, ItemsCRDT

# --------------------------------------------------------------

class Server:
    def __init__(self, name = 'server', port = 6000):
        self.name = name
        self.online = True
        self.port = port
        self.address = f"tcp://127.0.0.1:{self.port}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

# --------------------------------------------------------------

    def load_crdts(self):
        self.lists_crdt = ListsCRDT()
        self.items_crdt = {}
        shopping_lists = self.database.get_shopping_lists()
        for shopping_list in shopping_lists:
            self.lists_crdt.add((shopping_list[0], shopping_list[1]))
            #self.items_crdt[shopping_list[0]] = ItemsCRDT()
            # to do
        removed_lists = self.database.get_removed_lists()
        for removed_list in removed_lists:
            self.lists_crdt.remove((removed_list[0], removed_list[1]))

# --------------------------------------------------------------

    def connect(self):
        self.socket.bind(self.address)
        print(f"[INFO] > Listening on port {self.port}")

# --------------------------------------------------------------

    def receive_message(self):
        multipart_message = self.socket.recv_multipart()
        print(f"\n[{self.port}][BROKER] > {multipart_message}")
        client_id, message = multipart_message[0], multipart_message[1]
        message = json.loads(message.decode('utf-8'))
        return client_id, message

    def send_message(self, client_id, message):
        self.socket.send_multipart([client_id, json.dumps(message).encode('utf-8')])

# --------------------------------------------------------------

    def run(self):
        self.database = ArmazonDB("server/databases/" + self.name)
        self.load_crdts()
        self.connect()
        while True:
            client_id, request = self.receive_message()
            self.process_request(request, client_id)

    def process_request(self, request, client_id):
        if request['action'] == 'r_u_there':
            self.send_pulse()
        elif request['action'] == 'get_shopping_list':
            self.get_shopping_list(request, client_id)
        elif request['action'] == 'crdts':
            crdt = ListsCRDT.from_json(request)
            self.process_crdts(crdt, client_id)
        else:
            self.default_response(client_id)
        
# --------------------------------------------------------------

    def send_pulse(self):
        response = {'status': 'OK'}
        self.send_message(b"", response)

    def get_shopping_list(self, request, client_id):
        shopping_list_id = request['id']
        shopping_list = self.database.get_shopping_list(shopping_list_id)
        if shopping_list == None:
            response = {'action': 'get_shopping_list', 'message': 'Shopping list not found'}
        else:
            items = self.database.get_items(shopping_list_id)
            response = {'action': 'get_shopping_list', 'id': shopping_list[0], 'name': shopping_list[1], 'items': items}
        self.send_message(client_id, response)

    def process_crdts(self, crdt, client_id):
        self.lists_crdt.merge(crdt)
        crdt_json = self.lists_crdt.to_json()
        crdt_json['action'] = 'crdts'
        self.update_db_lists()
        self.send_message(client_id, crdt_json)

    def default_response(self, client_id):
        response = {'status': 'OK'}
        self.send_message(client_id, response)

# --------------------------------------------------------------

    def update_db_lists(self):
        for element in self.lists_crdt.add_set:
            if self.database.get_shopping_list(element[0]) == None:
                self.database.add_shopping_list(element[0], element[1])
        for element in self.lists_crdt.remove_set:
            self.database.delete_shopping_list(element[0])

# --------------------------------------------------------------

    def mark_as_offline(self):
        self.online = False
    
    def mark_as_online(self):
        self.online = True