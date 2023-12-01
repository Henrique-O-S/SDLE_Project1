# --------------------------------------------------------------

import zmq
import json
import time
from server.multi_server import MultiServer
from crdts import ListsCRDT, ItemsCRDT

# --------------------------------------------------------------

class Broker:
    def __init__(self, frontend_port=5559, backend_port=5560):
        self.frontend_port = frontend_port
        self.backend_port = backend_port
        self.connect()
        self.setup_poller()

# --------------------------------------------------------------

    def connect(self):
        self.context = zmq.Context()
        self.frontend_socket = self.context.socket(zmq.ROUTER)
        self.backend_socket = self.context.socket(zmq.DEALER)
        self.frontend_socket.bind(f"tcp://127.0.0.1:{self.frontend_port}")
        self.backend_socket.bind(f"tcp://127.0.0.1:{self.backend_port}")

    def setup_poller(self):
        self.poller = zmq.Poller()
        self.poller.register(self.frontend_socket, zmq.POLLIN)
        self.poller.register(self.backend_socket, zmq.POLLIN)

# --------------------------------------------------------------

    def run(self):
        while True:
            print("Waiting for message from client or server...")
            self.socks = dict(self.poller.poll())
            self.frontend_polling()
            self.backend_polling()

    def frontend_polling(self):
        if self.frontend_socket in self.socks and self.socks[self.frontend_socket] == zmq.POLLIN:
            multipart_message = self.frontend_socket.recv_multipart()
            print("ROUTER // Raw message from client | ", multipart_message)
            client_id, dummy, message = multipart_message[0:]
            message = json.loads(message.decode('utf-8'))
            if message['action'] == 'get_shopping_list':
                self.search_shopping_list(message['id'], client_id)
            elif message['action'] == 'crdts':
                self.crdts_to_servers(message['crdt'], client_id)

    def backend_polling(self):
        if self.backend_socket in self.socks and self.socks[self.backend_socket] == zmq.POLLIN:
            multipart_message = self.backend_socket.recv_multipart()
            print("DEALER // Raw message from server | ", multipart_message)
            client_id, message = multipart_message[1], multipart_message[2]
            #message = json.loads(message.decode('utf-8'))
            #if (message['action']) == 'crdts':
            #    self.crdts_to_frontend(message['crdt'], client_id)
            #self.frontend_socket.send_multipart([client_id, b"", message])


# --------------------------------------------------------------

    def search_shopping_list(self, id, client_id):
        server = MultiServer.get_server(id)
        self.backend_socket.connect(server.address)
        time.sleep(2)
        message = {'action': 'get_shopping_list', 'id': id}
        self.backend_socket.send_multipart([b"", client_id, json.dumps(message).encode('utf-8')])

# --------------------------------------------------------------


    def distribute_crdts(self, crdt_json):
        servers_info = {server: ListsCRDT() for server in MultiServer.servers}
        for element in crdt_json['add_set']:
            print(element)
            server = MultiServer.get_server(element[0])
            print(server.address)
            servers_info[server].add((element[0], element[1]))
        for element in crdt_json['remove_set']:
            server = MultiServer.get_server(element[0])
            servers_info[server].add((element[0], element[1]))
        return servers_info

    def crdts_to_servers(self, crdt_json, client_id):
        servers_info = self.distribute_crdts(crdt_json)
        responses = []
        for server, crdt in servers_info.items():
            print("NOW AT", server.address)
            if crdt.add_set or crdt.remove_set:
                # Connect to the server
                self.backend_socket.connect(server.address)

                # Send the message to the server
                crdt_json = crdt.to_json()
                crdt_json['action'] = 'crdts'
                self.backend_socket.send_multipart([b"", client_id, json.dumps(crdt_json).encode('utf-8')])
                print(server.address, crdt.to_json())

                # Receive the response from the server
                multipart_message = self.backend_socket.recv_multipart()
                print("DEALER // Raw message from server | ", multipart_message)
                client_identity, response = multipart_message[1], multipart_message[2]
                responses.append(response)
                # Disconnect from the server
                self.backend_socket.disconnect(server.address)
                time.sleep(1)
        self.crdts_to_frontend(client_id)


# --------------------------------------------------------------

    def crdts_to_frontend(self, client_id):
        #crdt_json['action'] = 'crdts'
        crdt_json = {'status': 'OK'}
        message = json.dumps(crdt_json).encode('utf-8')
        self.frontend_socket.send_multipart([client_id, b"", message])
        #self.frontend_socket.send_multipart([client_id, b"", json.dumps(crdt_json).encode('utf-8')])

# --------------------------------------------------------------
