import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE messages (id INTEGER PRIMARY KEY, username TEXT, message TEXT)''')
conn.commit()
conn.close()
