import sqlite3

# Connect to the non-creamy layer database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS non_creamy_layer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    outward_no TEXT,
    date_of_issue TEXT
);
''')
# Manually insert a document
name = "Kumar Lalit Vijay Patil"
outward_no = "39691330545"
date_of_issue = "11/08/2023"

c.execute('INSERT INTO non_creamy_layer (name, outward_no, date_of_issue) VALUES (?, ?, ?)', 
          (name, outward_no, date_of_issue))

conn.commit()
conn.close()
