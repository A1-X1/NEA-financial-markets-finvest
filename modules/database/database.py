import sqlite3

# create the connection and cursor in database
connection = sqlite3.connect("modules/database/main.db")
cursor = connection.cursor()
