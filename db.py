import os
import mysql.connector as mysql

class SQL:
	users = []

	def __init__(self):
		self.db = mysql.connect(
			host = os.environ['MYSQLHOST'],
			user = os.environ['MYSQLUSER'],
			password = os.environ['MYSQLPASSWORD'],
			port = int(os.environ['MYSQLPORT']),
			database = os.environ['MYSQLDATABASE']
		)
		self.cursor = self.db.cursor(buffered=True)
		self.cursor.execute('SELECT id FROM users')
		self.users = list(map(lambda i: i[0], self.cursor.fetchall()))
		print('initilaized database object with keys:')
		for user in self.users:
			print('\t-', user)

	def __setitem__(self, key, value):
		print('setting key', key)
		value = str(value)
		if key in self.users:
			self.cursor.execute("UPDATE users SET token=%s WHERE id=%s", (value, key))
		else:
			self.users.append(key)
			self.cursor.execute("INSERT INTO users (id, token) VALUES (%s, %s)", (key, value))
		print('commiting key', key)
		self.db.commit()
		print('set key', key)

	def __getitem__(self, key):
		self.cursor.execute('SELECT token FROM users WHERE id=%s', [key])
		return self.cursor.fetchall()[0][0]

	def __contains__(self, key):
		return key in self.users

	def keys(self):
		return self.users
