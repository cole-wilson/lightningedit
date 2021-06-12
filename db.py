import os
import mysql.connector

for i in os.environ:
	print(i, os.environ[i])

# mydb = mysql.connector.connect(
#   host=os.environ['MYSQLHOST'],
#   user=os.environ['MYSQLUSER'],
#   password=os.environ['MYSQLPASSWORD'],
# 	# port=os.environ['MYSQLPORT']
# )

class SQL:
	def __setitem__(self, key, value):
		pass
	def __getitem__(self, key):
		return ""
	def keys(self):
		return []
