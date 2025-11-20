import sqlite3

# Connect to the non-creamy layer database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS pan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    pan_no TEXT
);
''')
# Manually insert a document
name = "LALIT VIJAY PATIL"
pan_no = "GPMPPOS905"

c.execute('INSERT INTO pan (name, pan_no) VALUES (?, ?)', 
          (name, pan_no))

conn.commit()
conn.close()
