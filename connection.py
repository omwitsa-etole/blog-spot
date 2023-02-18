import os
import mysql.connector
def connector():
	"""
	db = mysql.connector.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="root",  # your password
                     db="dbo")
	"""
	for i in range(0,8):
		try:
			db = mysql.connector.connect(host="192.185.81.65",    # your host, usually localhost
		             user=os.environ.get("db_user"),         # your username
		             passwd=os.environ.get("db_pass"),  # your password
		             db=os.environ.get("db_name"))
			break
		except Exception as e:
			print(str(e))
			pass
	#"""
	if db == None:
		raise "No connection"

	return db
