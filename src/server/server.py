# --------------------------------------------------------------

import zmq
import json
from db import ArmazonDB
from crdts import ListsCRDT, ItemsCRDT

# --------------------------------------------------------------

class Server:
    def __init__(self, name = 'server', port = 6000):
        self.name = name
        self.port = port
        self.address = f"tcp://127.0.0.1:{self.port}"
        self.database = ArmazonDB("server/databases/" + self.name)
        self.load_crdts()

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
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.address)
        print(f"Server listening on port {self.port}...")

# --------------------------------------------------------------

    def run(self):
        self.connect()
        while True:
            print("Waiting for message from broker...")
            multipart_message = self.socket.recv_multipart()
            print("SERVER RECEIVED MESSAGE", self.address)
            print("REP // Raw message from broker | ", multipart_message)
            request = json.loads(multipart_message[1].decode('utf-8'))
            client_id = multipart_message[0]
            self.process_request(request, client_id)

    def process_request(self, request, client_id):
        if request['action'] == 'get_shopping_list':
            self.get_shopping_list(request['id'], client_id)
        elif request['action'] == 'crdts':
            print(request)
            self.default_response(client_id)
        else:
            self.default_response(client_id)

# --------------------------------------------------------------

    def get_shopping_list(self, shopping_list_id, client_id):
        shopping_list = self.database.get_shopping_list(shopping_list_id)
        if shopping_list == None:
            response = {'status': 'ERROR', 'message': 'Shopping list not found'}
        else:
            items = self.database.get_items(shopping_list_id)
            response = {'status': 'OK', 'id': shopping_list[0], 'name': shopping_list[1], 'items': items}
        self.socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])

    def process_crdts(self, crdt, client_id):
        print(crdt)
        response = {'status': 'OK'}
        self.socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])

    def default_response(self, client_id):
        response = {'status': 'OK'}
        self.socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])

# --------------------------------------------------------------
