# --------------------------------------------------------------

import zmq
import json
import sys
import time
import random
sys.path.append('../')
from db import ArmazonDB
from crdts import ListsCRDT

# --------------------------------------------------------------

class Server:
    def __init__(self, name = 'server', port = 6000, update_interval = 10, receive_timeout = 6):
        self.name = name
        self.online = True
        self.port = port
        self.update_interval = update_interval
        self.message_receive_timeout = receive_timeout
        self.curr_broker_nr = random.randint(0, 2) 
        self.address = f"tcp://127.0.0.1:{self.port}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

# --------------------------------------------------------------

    def load_crdts(self):
        self.lists_crdt = ListsCRDT()
        self.updated_lists_crdt = ListsCRDT()
        shopping_lists = self.database.get_shopping_lists()
        updated_shopping_lists = self.database.get_updated_shopping_lists()
        for shopping_list in shopping_lists:
            self.lists_crdt.add((shopping_list[0], shopping_list[1]))
            items = self.database.get_items(shopping_list[0])
            for item in items:
                self.lists_crdt.add_item(shopping_list[0], (item[1], item[2]), item[3])
        removed_lists = self.database.get_removed_lists()
        for removed_list in removed_lists:
            self.lists_crdt.remove((removed_list[0], removed_list[1]))
        for shopping_list in updated_shopping_lists:
            self.updated_lists_crdt.add((shopping_list[0], shopping_list[1]))
            items = self.database.get_items(shopping_list[0])
            for item in items:
                self.updated_lists_crdt.add_item(shopping_list[0], (item[1], item[2]), item[3])

# --------------------------------------------------------------

    def connect(self):
        self.socket.bind(self.address)
        print(f"[INFO] > Listening on port {self.port}")

    def disconnect(self):
        self.socket.unbind(self.address)
        print(f"[INFO] > Disconnected from port {self.port}")


# --------------------------------------------------------------

    def receive_message(self):
        print(f"\n[{self.port}] > Waiting for message")
        multipart_message = self.socket.recv_multipart()
        print(f"\n[{self.port}][BROKER] > {multipart_message}")
        if len(multipart_message) == 2:
            client_id, message = multipart_message[0], multipart_message[1]
        else:
            client_id, message = b"", multipart_message[0]
        message = json.loads(message.decode('utf-8'))
        return client_id, message

    def send_message(self, client_id, message):
        print(f"\n[BROKER][{self.port}] > {message}")
        self.socket.send_multipart([client_id, json.dumps(message).encode('utf-8')])

# --------------------------------------------------------------

    def run(self):
        self.database = ArmazonDB("server/databases/" + self.name)
        self.load_crdts()
        self.connect()

        next_update_time = time.time() + self.update_interval  # Set initial time for first update

        print(f"\n[{self.port}] > Next update time: {next_update_time}")

        print(f"[INFO] > Server {self.name} is running")
        while True:
            current_time = time.time()

            print(f"\n[{self.port}] > Current time: {current_time}")
            # Check if it's time to perform an update
            if current_time >= next_update_time:
                print(f"\n[{self.port}] > Performing update")
                self.check_for_updates()
                next_update_time = current_time + self.update_interval  # Update next update time

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
        elif request['action'] == 'replication':
            crdt = ListsCRDT.from_json(request)
            self.process_replication(crdt, client_id)
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
            response = {'status': 'ERROR', 'action': 'get_shopping_list'}
        else:
            response = {'status': 'OK', 'action': 'get_shopping_list', 'id': shopping_list[0], 'name': shopping_list[1], 'items': []}
            items = self.database.get_items(shopping_list[0])
            for item in items:
                response['items'].append({'name': item[1], 'quantity': item[2], 'timestamp': item[3]})
        self.send_message(client_id, response)

    def process_crdts(self, crdt, client_id):
        self.lists_crdt.merge(crdt)
        self.updated_lists_crdt.merge(crdt)
        crdt_json = self.lists_crdt.to_json()
        crdt_json['action'] = 'crdts'
        self.update_db_lists()
        self.send_message(client_id, crdt_json)

    def process_replication(self, crdt, client_id):
        self.lists_crdt.merge(crdt)
        crdt_json = self.lists_crdt.to_json()
        crdt_json['action'] = 'replication'
        self.replicate_db_lists()
        self.send_message(client_id, crdt_json)

    def default_response(self, client_id):
        response = {'status': 'OK'}
        self.send_message(client_id, response)

# --------------------------------------------------------------

    def update_db_lists(self):
        for element in self.lists_crdt.add_set:
            if self.database.get_shopping_list(element[0]) == None:
                self.database.add_shopping_list(element[0], element[1])
            self.update_db_items(element[0])
        for element in self.lists_crdt.remove_set:
            self.database.delete_shopping_list(element[0])

    def replicate_db_lists(self):
        for element in self.lists_crdt.add_set:
            if self.database.get_shopping_list(element[0]) == None:
                self.database.replicate_add_shopping_list(element[0], element[1])
            self.replicate_db_items(element[0])
        for element in self.lists_crdt.remove_set:
            self.database.replicate_delete_shopping_list(element[0])

    def update_db_items(self, shopping_list_id):
        for item_name, (quantity, _) in self.lists_crdt.items_crdt.get(shopping_list_id).add_set.items():
            existing_item = self.database.get_item(shopping_list_id, item_name)
            if existing_item is None:
                self.database.add_item(item_name, quantity, shopping_list_id)
            else:
                self.database.update_item(item_name, quantity, shopping_list_id)
        for item_name, _ in self.lists_crdt.items_crdt.get(shopping_list_id).remove_set.items():
            self.database.delete_item(item_name, shopping_list_id)

    def replicate_db_items(self, shopping_list_id):
        for item_name, (quantity, _) in self.lists_crdt.items_crdt.get(shopping_list_id).add_set.items():
            existing_item = self.database.get_item(shopping_list_id, item_name)
            if existing_item is None:
                self.database.replicate_add_item(item_name, quantity, shopping_list_id)
            else:
                self.database.replicate_update_item(item_name, quantity, shopping_list_id)
        for item_name, _ in self.lists_crdt.items_crdt.get(shopping_list_id).remove_set.items():
            self.database.replicate_delete_item(item_name, shopping_list_id)

# --------------------------------------------------------------

    def check_for_updates(self):
        self.disconnect()

        # Retrieve shopping lists that have been updated
        updated_shopping_lists = self.database.get_updated_shopping_lists()

        if updated_shopping_lists:
                crdt_json = self.lists_crdt.to_json()
                crdt_json['action'] = 'replication'
                print(f"\n[{self.port}] > Sending CRDT to broker")
                response = self.send_request_receive_reply(crdt_json)
                print(f"\n[{self.port}] > Response: {response}")
                if response['status'] != 'ERROR':
                    print(f"\n[{self.port}] > Updating updated lists CRDT")
                    self.updated_lists_crdt = ListsCRDT()
                    self.database.clear_updated_shopping_lists()
                    print(f"\n[{self.port}] > Updated lists CRDT: {self.updated_lists_crdt}")

        print(f"\n[{self.port}] > Updated lists CRDT: {self.updated_lists_crdt}")

        if self.socket:
            self.socket.close()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.connect()

    def connect_to_broker(self, broker):
        self.broker_port = broker + 8500
        if self.socket:
            self.socket.close()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt(zmq.IDENTITY, str(self.name).encode('utf-8'))
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.socket.connect(f"tcp://127.0.0.1:{self.broker_port}")
        self.curr_broker_nr += 1

    def send_request_receive_reply(self, message):
        for _ in range(3):
            broker = self.curr_broker_nr % 3
            self.connect_to_broker(broker)
            print(f"\n [{self.name}]: Trying broker {self.broker_port}")
            self.socket.send_multipart([b"", self.name.encode('utf-8'), json.dumps(message).encode('utf-8')])
            try:
                sockets = dict(self.poller.poll(self.message_receive_timeout * 1000))
                if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                    multipart_message = self.socket.recv_multipart()
                    self.socket.disconnect(f"tcp://127.0.0.1:{self.broker_port}")
                    print(f"\n [BROKER] > [SERVER {self.name}]: {multipart_message}")
                    response = json.loads(multipart_message[1].decode('utf-8'))
                    return response
                else:
                    print(f"\n[ERROR] > [{self.name}]: No message received within {self.message_receive_timeout} seconds from [BROKER {self.broker_port}]")
                    self.socket.disconnect(f"tcp://127.0.0.1:{self.broker_port}")
                    print(f"\n [{self.name}]: ASSUMING BROKER IS OFFLINE")
            except zmq.ZMQError as e:
                print(f"\n[ERROR] > [{self.name}]: Error receiving message from BROKER: {e}")
                return None
        print(f"\n[ERROR] > [{self.name}]: TRIES EXCEEDED, ABORTING REQUEST")
        data = {}
        data['status'] = 'ERROR'
        return data

# --------------------------------------------------------------

    def mark_as_offline(self):
        self.online = False
    
    def mark_as_online(self):
        self.online = True

# --------------------------------------------------------------
