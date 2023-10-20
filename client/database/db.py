import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('shopping_list.db')

# Create a cursor object
cursor = conn.cursor()

# Create a table and define its schema

cursor.execute('''
    DROP TABLE IF EXISTS shopping_list;
''')
cursor.execute('''
    DROP TABLE IF EXISTS item;
''')
# Commit the changes and close the connection
conn.commit()
conn.close()