from sqlite3 import Error
import sqlite3
import os
import base64
import json


class DB:

	db_file = "users.db"

	def __init__(self):
		'''
		Create database connection and initialize the table
		'''
		# Get one folder back path for user database
		dirname, filename = os.path.split(os.path.abspath(__file__))
		db_path = f"{os.path.dirname(dirname)}\{self.db_file}"

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
		'''
		password = base64.b64encode(password.encode()).decode("utf-8")  # base64 encrypted password
		data = {'hello', 'hello'}
		insert_user = f"INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD) VALUES ('{device_id}','{username}','{password}') WHERE DEVICE_ID ="
		print(f"[Status] Inserted {device_id} into users.db")
		self.__query(insert_user)
		'''
		select_ids = f"SELECT DEVICE_ID FROM users WHERE DEVICE_ID='{device_id}'"
		rows = self.c.fetchall()

		# If the device ID dosen't already exist, create it
		if len(rows) == 0:
			insert_user = f"INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD) VALUES ('{device_id}','{username}','{password}')"
			self.__query(insert_user)
			self.conn.commit()
			print(f"[Status] Inserted {device_id} into users.db")


if __name__ == "__main__":
	DB = DB()
	DB.create_user("12371293712937129037120923712093", "1420569", "testpassword")