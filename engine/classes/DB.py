from sqlite3 import Error
import sqlite3
import os
import base64


class DB:

	db_file = "users.db"

	def __init__(self):
		'''
		Create database connection and initialize the table
		'''
		# Get one folder back path for user database
		os.chdir("..")
		db_path = f"{os.path.abspath(os.curdir)}\{self.db_file}"

		self.conn = sqlite3.connect(db_path)  # Create sqlite connection
		self.c = self.conn.cursor()

		create_user_table = """
			CREATE TABLE IF NOT EXISTS users (
				ID integer PRIMARY KEY AUTOINCREMENT,
				DEVICE_ID TEXT,
				USERNAME TEXT,
				PASSWORD TEXT,
				DATA TEXT
			);
		"""
		self.__query(create_user_table)  # Create users table if does not exist
	
	def __query(self, q):
		'''
		Execute certain query and commit the changes
		'''
		try:
			self.c.execute(q)
			self.conn.commit()
		except Error as e:
			print(q, e)

	def create_user(self, device_id, username, password):
		password = base64.b64encode(password.encode()).decode("utf-8")  # base64 encrypted password
		data = {'hello', 'hello'}
		insert_user = f"INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD) VALUES ('{device_id}','{username}','{password}')"
		self.__query(insert_user)


DB = DB()
DB.create_user("12371293712937129037120923712093", "1420569", "testpassword")
'''

"""

def query(q):
	try:
		c.execute(q)
	except Error as e:
		print(q)
		print(e)


def create_user(device_id, username, password):
	q = f"INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD,DATA) VALUES ('{device_id}','{username}','{password}','Hello')"
	conn.commit()

query(q)

create_user("23", "134123421", "12123")

#print(os.path.abspath(os.curdir))


class DB:

	def __init__(self, db_file):
		self.conn = sqlite3.connect(db_file)


		self.__query(sql_create_tables)

	def __query(self, query):
		try:
			c = self.conn.cursor()
			c.execute(query)
		except Error as e:
			print(e)


		



if __name__ == "__main__":
	
	db = DB("./users.db")
'''