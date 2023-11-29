import sys
import zmq
import sqlite3
import json
sys.path.append('..')
from db import ArmazonDB

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.address = f"tcp://127.0.0.1:{self.port}"
        self.database = ArmazonDB("../server/databases/" + self.name)

    def get_database_path(self):
        return f"databases/shopping_{self.port}.db"

    def run(self):
        self.socket.bind(self.address)
        print(f"Server listening on port {self.port}...")
        while True:
            print("Waiting for message from broker...")
            multipart_message = self.socket.recv_multipart()
            print("SERVER RECEIVED MESSAGE", self.address)
            print("REP // Raw message from broker | ", multipart_message)
            request = json.loads(multipart_message[1].decode('utf-8'))
            client_id = multipart_message[0]

            if request['action'] == 'create_shopping_list':
                self.create_shopping_list(request, client_id)
            elif request['action'] == 'get_shopping_lists':
                self.get_shopping_lists(client_id)
            elif request['action'] == 'create_item':
                self.create_item(request, client_id)
            elif request['action'] == 'get_items':
                self.get_items(request, client_id)
            else:
                self.default_response(client_id)

    def create_shopping_list(self, request, client_id):
        name = request['name']
        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        cursor.execute('INSERT INTO shopping_lists (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        response = {'message': 'Shopping list created successfully'}
        self.socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])

    def get_shopping_lists(self, client_id):
        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shopping_lists')
        shopping_lists = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        conn.close()
        self.socket.send_json(shopping_lists)

    def create_item(self, request, client_id):
        name = request['name']
        quantity = request['quantity']
        shopping_list_id = request['shopping_list_id']

        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name, quantity, shopping_list_id) VALUES (?, ?, ?)', (name, quantity, shopping_list_id))
        conn.commit()
        conn.close()
        self.socket.send_json({'message': 'Item created successfully'})

    def get_items(self, request, client_id):
        shopping_list_id = request['shopping_list_id']
        conn = sqlite3.connect(self.get_database_path())
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        items = [{'id': row[0], 'name': row[1], 'quantity': row[2]} for row in cursor.fetchall()]
        conn.close()
        self.socket.send_json(items)

    def default_response(self, client_id):
        response = {'message': 'Im here bro'}
        self.socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])
