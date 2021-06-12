import os
import mysql.connector

# for i in os.environ:
# 	print(i, os.environ[i])



class SQL:
	users = []

	def __init__(self):
		setup = {
			"host":os.environ['MYSQLHOST'],
			"user":os.environ['MYSQLUSER'],
			"password":os.environ['MYSQLPASSWORD'],
			"port":int(os.environ['MYSQLPORT'])
		}
		try:
			self.db = mysql.connector.connect(database='main', **setup)
		except:
			self.db = mysql.connector.connect(**setup)
			cursor = self.db.cursor(buffered=True)
			cursor.execute("CREATE DATABASE main")
			self.db = mysql.connector.connect(database='main', **setup)

		self.cursor = self.db.cursor(buffered=True)
		# self.cursor.execute("SHOW TABLES")
		# if 'users' not in self.cursor:
		# 	self.cursor.execute(
		# 		"CREATE TABLE users (id VARCHAR(15), token VARCHAR(400))"
		# 	)
		self.cursor.execute('SELECT id FROM users')
		self.users = list(map(lambda i: i[0], self.cursor.fetchall()))

	def __setitem__(self, key, value):
		if key in self.users:
			self.cursor.execute("UPDATE users SET token=%s WHERE id=%s", (value, key))
		else:

			self.users.append(key)
			self.cursor.execute("INSERT INTO users (id, token) VALUES (%s, %s)", (key, value))
		self.db.commit()



	def __getitem__(self, key):
		self.cursor.execute('SELECT token FROM users WHERE id=%s', [key])
		return self.cursor.fetchall()[0][0]

	def keys(self):
		return self.users
