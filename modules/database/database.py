import sqlite3

connection = sqlite3.connect("modules/database/main.db")
cursor = connection.cursor()

cursor.execute('DELETE FROM GlobalSettingsTable WHERE (id=1);')