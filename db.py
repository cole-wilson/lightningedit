import os
import mysql.connector

mydb = mysql.connector.connect(
  host=os.environ['MYSQLHOST'],
  user=os.environ['MYSQLUSER'],
  password=os.environ['MYSQLPASSWORD'],
	# port=os.environ['MYSQLPORT']
)

class SQL:
	def __setitem__(self, key, value):
		pass
	def __getitem__(self, key):
		return ""
	def keys(self):
		return []
