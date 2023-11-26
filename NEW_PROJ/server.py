import sys
import zmq
import sqlite3
import json
def get_port():
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    return int(sys.argv[1])

def get_database_path(port):
    return f"databases/shopping_{port}.db"

context = zmq.Context()
socket = context.socket(zmq.REP)
port = get_port()
print(port)
socket.bind(f"tcp://127.0.0.1:{port}")

# Database setup (similar to previous example)
conn = sqlite3.connect(get_database_path(port))
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS shopping_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        shopping_list_id INTEGER,
        FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists (id)
    )
''')
conn.commit()
conn.close()

while True:
    multipart_message = socket.recv_multipart()
    print("REP // Raw message from broker | ", multipart_message)
    request = json.loads(multipart_message[1].decode('utf-8'))
    client_id = multipart_message[0]
    
    if request['action'] == 'create_shopping_list':
        name = request['name']
        conn = sqlite3.connect(get_database_path(port))
        cursor = conn.cursor()
        cursor.execute('INSERT INTO shopping_lists (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        response = {'message': 'Shopping list created successfully'}
        socket.send_multipart([client_id, json.dumps(response).encode('utf-8')])

    elif request['action'] == 'get_shopping_lists':
        conn = sqlite3.connect(get_database_path(port))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM shopping_lists')
        shopping_lists = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        conn.close()
        socket.send_json(shopping_lists)

    elif request['action'] == 'create_item':
        name = request['name']
        quantity = request['quantity']
        shopping_list_id = request['shopping_list_id']

        conn = sqlite3.connect(get_database_path(port))
        cursor = conn.cursor()
        cursor.execute('INSERT INTO items (name, quantity, shopping_list_id) VALUES (?, ?, ?)', (name, quantity, shopping_list_id))
        conn.commit()
        conn.close()
        socket.send_json({'message': 'Item created successfully'})

    elif request['action'] == 'get_items':
        shopping_list_id = request['shopping_list_id']
        conn = sqlite3.connect(get_database_path(port))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        items = [{'id': row[0], 'name': row[1], 'quantity': row[2]} for row in cursor.fetchall()]
        conn.close()
        socket.send_json(items)
