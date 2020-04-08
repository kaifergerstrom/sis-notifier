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

		self.conn = sqlite3.connect(db_path, check_same_thread=False)  # Create sqlite connection
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
		self.c.execute(create_user_table)  # Create users table if does not exist
		self.conn.commit()

		print(f"[Status] Loaded users.db in {dirname}")


	def create_user(self, device_id, username, password):
		"""Add new entry to user.db

		:param device_id: unique device id from user
		:param username: SIS username
		:param password: SIS password

		:returns: void
		"""
		# Run query to check if device_id is in the users.db
		select_ids = "SELECT DEVICE_ID FROM users WHERE DEVICE_ID=?"
		self.c.execute(select_ids, [device_id])
		rows = self.c.fetchall()

		#data = str({'test':'word', 'test2':24})  # Replace with gradebook.get()
		
		# If the device ID dosen't already exist, create it
		if len(rows) == 0:
			insert_user = "INSERT INTO users (DEVICE_ID,USERNAME,PASSWORD) VALUES (?,?,?)"
			self.c.execute(insert_user, [device_id, username, password])
			self.conn.commit()
			print(f"[Status] Inserted {device_id} into users.db")
		else:  # If the row does exist, just update the SIS credentials associated
			update_user = "UPDATE users set USERNAME=?, PASSWORD=? WHERE DEVICE_ID=?"
			self.c.execute(update_user, [username, password, device_id])
			self.conn.commit()
			print(f"[Status] Updated credentials for {device_id} in users.db")
			
			
	def get_unique_users(self):
		"""Get list of unique SIS credentials to run update operation

		:param none:

		:returns: list of unique username/password
		"""
		unique_select = "SELECT DISTINCT USERNAME,PASSWORD FROM users"
		self.c.execute(unique_select)
		rows = self.c.fetchall()
		return rows


	def get_grade_json(self, username):
		grade_select = "SELECT DATA FROM users WHERE USERNAME=?"
		self.c.execute(grade_select, [username])
		rows = self.c.fetchall()
		return rows[0][0]


	def get_device_ids(self, username):
		"""Get list of device ids associated to certain SIS account

		:param username: SIS username

		:returns: list of device ids
		"""
		select_ids = "SELECT DEVICE_ID FROM users WHERE USERNAME=?"
		self.c.execute(select_ids, [username])
		rows = self.c.fetchall()
		return [row[0] for row in rows]


if __name__ == "__main__":
	DB = DB()
	#DB.create_user("uajdh7y1723h1jhsdad1723y", "1420569", "cGFzc3dvcmQ=")
	print(DB.get_unique_users())
	print(DB.get_device_ids("1420569"))
	print(DB.get_grade_json("1420569"))