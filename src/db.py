import sqlite3

class ArmazonDB:
    def __init__(self, name):
        self.conn = sqlite3.connect(name + '.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                removed BOOLEAN DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                shopping_list_id TEXT NOT NULL,
                FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS updated_shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shopping_list_id INTEGER NOT NULL,
                removed BOOLEAN DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shopping_list_id) REFERENCES shopping_lists (id)
            )
        ''')
        self.conn.commit()

    def add_shopping_list(self, new_list_id, new_list_name):
        self.cursor.execute('INSERT INTO shopping_lists (id, name) VALUES (?, ?)', (new_list_id, new_list_name))

        # Check if the shopping list has already been updated
        self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (new_list_id,))
        result = self.cursor.fetchone()
        if result:
            # If the shopping list is already in the updated_shopping_lists table, update the timestamp
            self.cursor.execute('UPDATE updated_shopping_lists SET updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (new_list_id,))
        else:
            # If the shopping list is not in the updated_shopping_lists table, insert a new entry
            self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id) VALUES (?)', (new_list_id,))

        self.conn.commit()
        return new_list_id

    def add_item(self, name, quantity, shopping_list_id, timestamp=None):
        self.cursor.execute('SELECT name FROM items WHERE name = ? AND shopping_list_id = ?', (name, shopping_list_id))
        existing_item = self.cursor.fetchone()
        if existing_item:
            return None
        else:
            self.cursor.execute('INSERT INTO items (name, quantity, shopping_list_id) VALUES (?, ?, ?)',
                                (name, quantity, shopping_list_id))
            
            # Check if the shopping list has already been updated
            self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (shopping_list_id,))
            result = self.cursor.fetchone()
            if result:
                # If the shopping list is already in the updated_shopping_lists table, update the timestamp
                self.cursor.execute('UPDATE updated_shopping_lists SET updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (shopping_list_id,))
            else:
                # If the shopping list is not in the updated_shopping_lists table, insert a new entry
                self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id) VALUES (?)', (shopping_list_id,))

            self.conn.commit()
            self.update_timestamp(name, shopping_list_id, timestamp)
            return self.cursor.lastrowid
 
    def get_shopping_list(self, shopping_list_id):
        self.cursor.execute('SELECT * FROM shopping_lists WHERE id = ?', (shopping_list_id,))
        return self.cursor.fetchone()

    def get_shopping_lists(self):
        self.cursor.execute('SELECT * FROM shopping_lists WHERE removed = ?', (0,))
        return self.cursor.fetchall()
    
    def get_removed_lists(self):
        self.cursor.execute('SELECT * FROM shopping_lists WHERE removed = ?', (1,))
        return self.cursor.fetchall()

    def get_items(self, shopping_list_id):
        self.cursor.execute('SELECT * FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        return self.cursor.fetchall()
    
    def get_item(self, shopping_list_id, item_name):
        self.cursor.execute('SELECT * FROM items WHERE shopping_list_id = ? AND name = ?', (shopping_list_id, item_name))
        return self.cursor.fetchone()

    def delete_shopping_list(self, shopping_list_id):
        # Check if the shopping list exists before marking it as removed
        self.cursor.execute('SELECT * FROM shopping_lists WHERE id = ?', (shopping_list_id,))
        shopping_list = self.cursor.fetchone()

        if shopping_list:
            # Mark the shopping list as removed in the shopping_lists table
            self.cursor.execute('UPDATE shopping_lists SET removed = ? WHERE id = ?', (1, shopping_list_id))

            # Check if the shopping list has already been updated
            self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (shopping_list_id,))
            result = self.cursor.fetchone()
            if result:
                # If the shopping list is already in the updated_shopping_lists table, update the timestamp
                self.cursor.execute('UPDATE updated_shopping_lists SET removed = ?, updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (1, shopping_list_id,))
            else:
                # If the shopping list is not in the updated_shopping_lists table, insert a new entry
                self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id, removed, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)', (shopping_list_id, 1))

            self.conn.commit()

    def delete_item(self, item_name, shopping_list_id):
        self.cursor.execute('DELETE FROM items WHERE name = ? AND shopping_list_id = ?', (item_name, shopping_list_id))

        # Check if the shopping list has already been updated
        self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (shopping_list_id,))
        result = self.cursor.fetchone()
        if result:
            # If the shopping list is already in the updated_shopping_lists table, update the timestamp
            self.cursor.execute('UPDATE updated_shopping_lists SET updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (shopping_list_id,))
        else:
            # If the shopping list is not in the updated_shopping_lists table, insert a new entry
            self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id) VALUES (?)', (shopping_list_id,))

        self.conn.commit()

    def update_item(self, item_name, new_quantity, shopping_list_id):
        self.cursor.execute('UPDATE items SET quantity = ? WHERE name = ? AND shopping_list_id = ?',
                            (new_quantity, item_name, shopping_list_id))
        
        # Check if the shopping list has already been updated
        self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (shopping_list_id,))
        result = self.cursor.fetchone()
        if result:
            # If the shopping list is already in the updated_shopping_lists table, update the timestamp
            self.cursor.execute('UPDATE updated_shopping_lists SET updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (shopping_list_id,))
        else:
            # If the shopping list is not in the updated_shopping_lists table, insert a new entry
            self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id) VALUES (?)', (shopping_list_id,))

        self.conn.commit()
        self.update_timestamp(item_name, shopping_list_id)

    def update_timestamp(self, item_name, shopping_list_id, timestamp=None):
        if timestamp is None:
            self.cursor.execute('UPDATE items SET timestamp = CURRENT_TIMESTAMP WHERE name = ? AND shopping_list_id = ?',
                                (item_name, shopping_list_id))
        else:
            self.cursor.execute('UPDATE items SET timestamp = ? WHERE name = ? AND shopping_list_id = ?',
                                (timestamp, item_name, shopping_list_id))
        self.conn.commit()

    def get_updated_shopping_lists(self):
        self.cursor.execute('SELECT * FROM updated_shopping_lists')
        return self.cursor.fetchall()
    
    def clear_updated_shopping_lists(self):
        self.cursor.execute('DELETE FROM updated_shopping_lists')
        self.conn.commit()

    def clear_shopping_lists(self):
        self.cursor.execute('DELETE FROM shopping_lists')
        self.cursor.execute('DELETE FROM items')
        self.cursor.execute('DELETE FROM updated_shopping_lists')
        self.conn.commit()

    def clear_list_items(self, shopping_list_id):
        self.cursor.execute('DELETE FROM items WHERE shopping_list_id = ?', (shopping_list_id,))
        
        # Check if the shopping list has already been updated
        self.cursor.execute('SELECT * FROM updated_shopping_lists WHERE shopping_list_id = ?', (shopping_list_id,))
        result = self.cursor.fetchone()
        if result:
            # If the shopping list is already in the updated_shopping_lists table, update the timestamp
            self.cursor.execute('UPDATE updated_shopping_lists SET updated_at = CURRENT_TIMESTAMP WHERE shopping_list_id = ?', (shopping_list_id,))
        else:
            # If the shopping list is not in the updated_shopping_lists table, insert a new entry
            self.cursor.execute('INSERT INTO updated_shopping_lists (shopping_list_id) VALUES (?)', (shopping_list_id,))

        self.conn.commit()

    def close_connection(self):
        self.conn.close()
