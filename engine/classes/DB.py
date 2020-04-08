from sqlite3 import Error
import sqlite3
import os
import base64
import json

class DB:

	db_file = "users.db"

	def __init__(self):
		"""Create table and file if does not exist and establish connection

		:param none:

		:returns: none
		"""
		# Get one folder back path for user database
		dirname, filename = os.path.split(os.path.abspath(__file__))
		db_path = f"{os.path.dirname(dirname)}\{self.db_file}"

		self.conn = sqlite3.connect(db_path)  # Create sqlite connection
		self.c = self.conn.cursor()

		create_user_table = """
			CREATE TABLE IF NOT EXISTS users (
				ID integer PRIMARY KEY AUTOINCREMENT,
				DEVICE_ID TEXT UNIQUE,
				USERNAME TEXT,
				PASSWORD TEXT,
				DATA TEXT
			);
		"""
		self.__query(create_user_table)  # Create users table if does not exist
		self.conn.commit()

		print(f"[Status] Loaded users.db in {dirname}")
	

	def __query(self, q):
		"""Run inputed query, print error if query fails

		:param q: string query to execute

		:returns: void
		"""
		try:
			self.c.execute(q)
		except Error as e:
			print(q, e)


	def create_user(self, device_id, username, password):
		"""Add new entry to user.db

		:param device_id: unique device id from user
		:param username: SIS username
		:param password: SIS password

		:returns: void
		"""
		# Run query to check if device_id is in the users.db
		select_ids = f"SELECT DEVICE_ID FROM users WHERE DEVICE_ID='{device_id}'"
		self.__query(select_ids)
		rows = self.c.fetchall()
		
		# If the device ID dosen't already exist, create it
		if len(rows) == 0:
			insert_user = f"INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD) VALUES ('{device_id}','{username}','{password}')"
			self.__query(insert_user)
			self.conn.commit()
			print(f"[Status] Inserted {device_id} into users.db")
		else:  # If the row does exist, just update the SIS credentials associated
			update_user = f"UPDATE users set USERNAME='{username}', PASSWORD='{password}' WHERE DEVICE_ID='{device_id}'"
			self.__query(update_user)
			self.conn.commit()
			print(f"[Status] Updated credentials for {device_id} in users.db")

	
	def get_unique_users(self):
		"""Get list of unique SIS credentials to run update operation

		:param none:

		:returns: list of unique username/password
		"""
		unique_select = f"SELECT DISTINCT USERNAME,PASSWORD FROM users"
		self.__query(unique_select)
		rows = self.c.fetchall()
		return rows


	def get_device_ids(self, username):
		"""Get list of device ids associated to certain SIS account

		:param username: SIS username

		:returns: list of device ids
		"""
		select_ids = f"SELECT DEVICE_ID FROM users WHERE USERNAME='{username}'"
		self.__query(select_ids)
		rows = self.c.fetchall()
		return [row[0] for row in rows]


if __name__ == "__main__":
	DB = DB()
	DB.create_user("uajdh7y1723h1jhsdad1723y", "21312312", "fakepassword")
	DB.get_unique_users()
	print(DB.get_device_ids("1420569"))