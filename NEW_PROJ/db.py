import sqlite3

class ShoppingListDB:
    def __init__(self, db_name='gui.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                name TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL,
                shopping_list_id TEXT NOT NULL,
                FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists (id)
            )
        ''')
        self.conn.commit()

    def add_shopping_list(self, new_list_id, new_list_name):
        self.cursor.execute('INSERT INTO shopping_lists (id, name) VALUES (?, ?)', (new_list_id, new_list_name))
        self.conn.commit()
        return new_list_id

    def add_item(self, name, quantity, shopping_list_id):
        self.cursor.execute('SELECT name FROM items WHERE name = ? AND shopping_list_id = ?', (name, shopping_list_id))
        existing_item = self.cursor.fetchone()
        if existing_item:
            return None
        else:
            self.cursor.execute('INSERT INTO items (name, quantity, shopping_list_id) VALUES (?, ?, ?)',
                                (name, quantity, shopping_list_id))
            self.conn.commit()
            return self.cursor.lastrowid

    def get_shopping_lists(self):
        self.cursor.execute('SELECT * FROM shopping_lists')
        return self.cursor.fetchall()
    
    def get_shopping_list(self, shopping_list_id):
        self.cursor.execute('SELECT * FROM shopping_lists WHERE id = ?', (shopping_list_id,))
        return self.cursor.fetchone()

    def get_items(self, shopping_list_id):
        self.cursor.execute('SELECT * FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        return self.cursor.fetchall()
    
    def get_item(self, shopping_list_id, item_name):
        self.cursor.execute('SELECT * FROM items WHERE shopping_list_id = ? AND name = ?', (shopping_list_id, item_name))
        return self.cursor.fetchone()

    def delete_shopping_list(self, shopping_list_id):
        self.cursor.execute('DELETE FROM shopping_lists WHERE id = ?', (shopping_list_id,))
        self.cursor.execute('DELETE FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        self.conn.commit()

    def delete_item(self, item_name):
        self.cursor.execute('DELETE FROM items WHERE name = ?', (item_name,))
        self.conn.commit()

    def update_item(self, item_name, new_quantity):
        self.cursor.execute('UPDATE items SET quantity = ? WHERE name = ?', (new_quantity, item_name))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()
