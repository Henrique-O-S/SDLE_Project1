import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('mydatabase.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table and define its schema
cursor.execute('''
    DROP TABLE IF EXISTS products
''')

cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        quantity INTEGER
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
