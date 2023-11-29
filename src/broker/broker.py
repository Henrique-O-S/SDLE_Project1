import zmq
import sys
sys.path.append('../server')
sys.path.append('../crdts')
from multi_server import MultiServer
from crdts import ListsCRDT
import json
import time

class Broker:
    def __init__(self, frontend_port=5559, backend_port=5560):
        self.context = zmq.Context()
        self.frontend_socket = self.context.socket(zmq.ROUTER)
        self.backend_socket = self.context.socket(zmq.DEALER)
        self.frontend_socket.bind(f"tcp://127.0.0.1:{frontend_port}")
        self.backend_socket.bind(f"tcp://127.0.0.1:{backend_port}")
        self.poller = zmq.Poller()
        self.poller.register(self.frontend_socket, zmq.POLLIN)
        self.poller.register(self.backend_socket, zmq.POLLIN)

    def run(self):
        while True:
            socks = dict(self.poller.poll())

            if self.frontend_socket in socks and socks[self.frontend_socket] == zmq.POLLIN:
                # Message from client
                multipart_message = self.frontend_socket.recv_multipart()
                #print("ROUTER // Raw message from client | ", multipart_message)
                client_id, dummy, message = multipart_message[0:]
                #print(multipart_message[2])
                #print(MultiServer.get_server(multipart_message[2].decode('utf-8')).address)
                message = json.loads(message.decode('utf-8'))
                #print(message)
                if message['action'] == 'update_shopping_lists_crdt':
                    self.backend_send_shopping_lists_crdt(message['crdt'], client_id)
                

            if self.backend_socket in socks and socks[self.backend_socket] == zmq.POLLIN:
                # Message from server
                multipart_message = self.backend_socket.recv_multipart()
                print("DEALER // Raw message from server | ", multipart_message)

                client_identity, response = multipart_message[1], multipart_message[2]

                # Forward the message to the client
                self.frontend_socket.send_multipart([client_identity, b"", response])

    def backend_send_shopping_lists_crdt(self, crdt_json, client_id):
        servers_info = {server: ListsCRDT() for server in MultiServer.servers}
        for el in crdt_json['add_set']:
            server = MultiServer.get_server(el[0])
            servers_info[server].add((el[0], el[1]))
        for el in crdt_json['remove_set']:
            server = MultiServer.get_server(el[0])
            servers_info[server].add((el[0], el[1]))
        #print data in servers_info
        for server in servers_info:
            print(server.name, servers_info[server].add_set, servers_info[server].remove_set)
        #send data to servers
        for server, crdt in servers_info.items():
            if crdt.add_set or crdt.remove_set:
                print(server.address, crdt.to_json())
                self.backend_socket.connect(server.address)
                crdt_json = crdt.to_json()
                crdt_json['action'] = 'update_shopping_lists_crdt'
                self.backend_socket.send_multipart([b"", client_id, json.dumps(crdt_json).encode('utf-8')])
                time.sleep(1)

  #      self.backend_socket.connect(MultiServer.get_server(multipart_message[2].decode('utf-8')).address)

 #       self.backend_socket.send_multipart([b"", client_id, message])



if __name__ == '__main__':
    broker = Broker()
    broker.run()
