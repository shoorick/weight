#!/usr/bin/python3

import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as file:
    connection.executescript(file.read())

cur = connection.cursor()

cur.execute("INSERT INTO categories (id, title) VALUES (?, ?)",
            (1, 'Weight')
            )

cur.execute("INSERT INTO entries (category_id, entry) VALUES (?, ?)",
            (1, 88)
            )

connection.commit()
connection.close()
