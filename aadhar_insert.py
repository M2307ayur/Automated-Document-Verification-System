import sqlite3

# Connect to the non-creamy layer database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS aadhar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    aadhar_no TEXT,
    birth_date TEXT
);
''')
# Manually insert a document
name = "Lalit Vijay Patil"
aadhar_no = "6150 3584 1431"
birth_date = "28/05/2003"

c.execute('INSERT INTO aadhar (name, aadhar_no,birth_date) VALUES (?, ?, ?)', 
          (name, aadhar_no,birth_date))

conn.commit()
conn.close()
