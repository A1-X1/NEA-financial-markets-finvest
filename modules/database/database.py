import sqlite3

connection = sqlite3.connect("modules/database/main.db")
cursor = connection.cursor()

cursor.execute("CREATE TABLE movie(title, year, score)")
