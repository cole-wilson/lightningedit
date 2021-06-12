import os
import mysql.connector as mysql

db = mysql.connect(
	host = os.environ['MYSQLHOST'],
	user = os.environ['MYSQLUSER'],
	password = os.environ['MYSQLPASSWORD'],
	port = int(os.environ['MYSQLPORT']),
	database = os.environ['MYSQLDATABASE']
)
cursor = db.cursor(buffered=True)

while 1:
	try:
		cursor.execute(input('>> '))
		db.commit()
		[print(i) for i in cursor.fetchall()]
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print('<< error: ' + str(e))