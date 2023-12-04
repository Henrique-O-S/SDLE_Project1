# --------------------------------------------------------------

import zmq
import json
import time
from server.multi_server import MultiServer
from crdts import ListsCRDT

# --------------------------------------------------------------

class Broker:
    def __init__(self, name, frontend_port=5559, backend_port=5560, pulse_check_interval=5, message_receive_timeout=2):
        self.name = name
        self.pulse_enabled = False
        self.pulse_check_interval = pulse_check_interval
        self.message_receive_timeout = message_receive_timeout
        self.last_pulse_check = time.time()
        self.frontend_port = frontend_port
        self.backend_port = backend_port

# --------------------------------------------------------------

    def connect(self):
        self.context = zmq.Context()
        self.frontend_socket = self.context.socket(zmq.ROUTER)
        self.backend_socket = self.context.socket(zmq.DEALER)
        self.frontend_socket.bind(f"tcp://127.0.0.1:{self.frontend_port}")
        self.backend_socket.bind(f"tcp://127.0.0.1:{self.backend_port}")
        print("[INFO] > Broker connected", self.frontend_port, self.backend_port, self.name)

    def setup_poller(self):
        self.poller = zmq.Poller()
        self.poller.register(self.frontend_socket, zmq.POLLIN)
        self.poller.register(self.backend_socket, zmq.POLLIN)

# --------------------------------------------------------------

    def receive_message_client(self):
        try:
            sockets = dict(self.poller.poll(self.message_receive_timeout * 1000))
            if self.frontend_socket in sockets and sockets[self.frontend_socket] == zmq.POLLIN:
                multipart_message = self.frontend_socket.recv_multipart()
                print(f"\n [CLIENT] > [{self.name}]: {multipart_message}")
                client_id, message = multipart_message[0], multipart_message[2]
                message = json.loads(message.decode('utf-8'))
                return client_id, message
            else:
                print(f"\n[ERROR] > [{self.name}]: No message received within {self.message_receive_timeout} seconds from [CLIENT]")
                return None, None
        except zmq.ZMQError as e:
            print(f"\n[ERROR] > [{self.name}]: Error receiving message from CLIENT: {e}")
            return None, None

    def send_message_client(self, client_id, message):
        self.frontend_socket.send_multipart([client_id, b"", json.dumps(message).encode('utf-8')])

    def send_message_server_receive_reply(self, servers, client_id, message, pulse=False):
        for server in servers:
            print(f"\n [{self.name}]: Trying server {server.address}")
            if not pulse and not server.online:
                continue
            print(server.address, server.online)
            self.backend_socket.connect(server.address)
            self.backend_socket.send_multipart([b"", client_id, json.dumps(message).encode('utf-8')])
            try:
                sockets = dict(self.poller.poll(self.message_receive_timeout * 1000))
                if self.backend_socket in sockets and sockets[self.backend_socket] == zmq.POLLIN:
                    multipart_message = self.backend_socket.recv_multipart()
                    print(f"\n [SERVER] > [{self.name}]: {multipart_message}")

                    self.backend_socket.disconnect(server.address)

                    client_id, message = multipart_message[1], multipart_message[2]
                    message = json.loads(message.decode('utf-8'))
                    server.mark_as_online()
                    return client_id, message
                else:
                    server.mark_as_offline()
                    self.backend_socket.disconnect(server.address)
                    print(f"\n [{self.name}]: {server.address} is offline")
                    print(f"\n[ERROR] > [{self.name}]: No message received within {self.message_receive_timeout} seconds from [SERVER]")
            except zmq.ZMQError as e:
                print(f"\n[ERROR] > [{self.name}]: Error receiving message from SERVER: {e}")
                return None, None
        print(f"\n [{self.name}]: No server online")
        return None, None

# --------------------------------------------------------------

    def run(self):
        self.connect()
        self.setup_poller()
        while True:
            current_time = time.time()
            if self.pulse_enabled and current_time - self.last_pulse_check >= self.pulse_check_interval:
                self.pulse_check_to_servers()
                self.last_pulse_check = current_time
            self.socks = dict(self.poller.poll(1000))
            self.frontend_polling()

    def frontend_polling(self):
        if self.frontend_socket in self.socks and self.socks[self.frontend_socket] == zmq.POLLIN:
            client_id, message = self.receive_message_client()
            if message['action'] == 'get_shopping_list':
                self.search_shopping_list(message['id'], client_id)
            elif message['action'] == 'crdts':
                self.crdts_to_servers(message, client_id)

# --------------------------------------------------------------

    def search_shopping_list(self, id, client_id):
        server = MultiServer.get_servers(id)
        servers = [server['primary']] + server['backup']
        message = {'action': 'get_shopping_list', 'id': id}
        client_id, response = self.send_message_server_receive_reply(servers, client_id, message)
        self.send_message_client(client_id, response)

# --------------------------------------------------------------

    def crdts_to_servers(self, crdt_json, client_id):
        servers_info = self.distribute_crdts(crdt_json)
        responses = []
        for server, [crdt, backup_servers] in servers_info.items():
            if crdt.add_set or crdt.remove_set:
                message = crdt.to_json()
                message['action'] = 'crdts'
                servers = [server] + backup_servers
                for server_el in servers:
                    print(f"\n [{self.name}]: It will try on {server_el.address}")
                _, response = self.send_message_server_receive_reply(servers, client_id, message)
                responses.append(response)
        self.crdts_to_client(responses, client_id)

    def distribute_crdts(self, crdt_json):
        servers_info = {server: [ListsCRDT(),[]] for server in MultiServer.servers}
        for element in crdt_json['add_set']:
            server = MultiServer.get_servers(element[0])
            servers_info[server['primary']][0].add((element[0], element[1]))
            if element[0] in crdt_json['items']:
                for item in crdt_json['items'][element[0]]['add_set']:
                    servers_info[server['primary']][0].add_item(element[0], (item[0], item[1][0]), item[1][1])
                for item in crdt_json['items'][element[0]]['remove_set']:
                    servers_info[server['primary']][0].remove_item(element[0], (item[0], item[1][0]), item[1][1])
            servers_info[server['primary']][1] = server['backup']
        for element in crdt_json['remove_set']:
            server = MultiServer.get_servers(element[0])
            servers_info[server['primary']][0].remove((element[0], element[1]))
            servers_info[server['primary']][1] = server['backup']
        return servers_info

# --------------------------------------------------------------

    def crdts_to_client(self, responses, client_id):
        crdt = ListsCRDT()
        for response in responses:
            received_crdt = ListsCRDT.from_json(response)
            crdt.merge(received_crdt)
        crdt_json = crdt.to_json()
        crdt_json['action'] = 'crdts'
        self.send_message_client(client_id, crdt_json)

# --------------------------------------------------------------

    def pulse_check_to_servers(self):
        for server in MultiServer.servers:
            message = {'action': 'r_u_there'}
            _, response = self.send_message_server_receive_reply([server], b"", message, pulse=True)
            if response:
                if response['status'] == 'OK':
                    print(f'\n[{server.port}] > [{self.name}] Pulse')
            else:
                print(f'\n[{server.port}] > [{self.name}] No Pulse')
                
# --------------------------------------------------------------
