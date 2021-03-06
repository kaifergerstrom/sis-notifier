from bs4 import BeautifulSoup
from getpass import getpass
import requests
import datetime
from .DB import DB

class SIS:

	# Links for pages in SIS
	p_login = "https://sisstudent.fcps.edu/SVUE/"
	p_gradebook = "https://sisstudent.fcps.edu/SVUE/PXP2_Gradebook.aspx?AGU=0"
	
	def validate_credentials(self, username, password):
		"""Determines whether SIS credentials are valid

		:param username: SIS username
		:param password: SIS password

		:returns: boolean of status
		"""

		self.db = DB()

		# Assign the username and password to scrape
		self.username = username
		self.password = password

		self.status, self.soup = self.__update_grade_data()  # Get the status and the soup
		return self.status  # Return the status of the credentials


	def __get_assignment_info(self, row):
		"""Extract assignment information from row in assignment table.
		This has to be a hard coded sequence becuase SIS has no real html (website builder)

		:param row: soup object of row for assignment

		:returns: formatted dictionary with assignment information
		"""
		info = {}  # Empty dictionary to populate
		current_time = datetime.datetime.now().isoformat()  # Save date of addition

		for i, div in enumerate(row.findAll("div")):  # Find all the div elements in row

			if i == 0:  # First div stores the assignment title
				title = div.text
				title = title.replace("\n", "")
			elif i == 1:  # Second div stores teacher name and course name "Last, FI Course(Period)""
				# Parse out teacher name from string
				teacher = div.text.split(" ")[0]
				teacher = ''.join(teacher)
				teacher = teacher.replace(",", "")
				# Get course title from string
				course = div.text.split(" ")[3:]
				course = ' '.join(course)
				# Get period between course name
				period = (course.split("("))[1].split(")")[0]
				course = course.split("(")[0]  # Remove period string from course title
			elif i == 2:
				date = div.text.split("Due Date: ")[1]  # Get the due date (not really important)
			elif i == 3:  # Fourth div stores points of assignment "Points: 0/10(0%)"
				points = div.text
				points = points.replace("Points: ", "")
				points = points.split("(")[0]
				points = points.replace(" ", "")

		info[title] = {'teacher':teacher, 'course':course, 'period': period, 'date_added':current_time, 'date': date, 'points':points}  # Populate final dictionary for data
		
		return title, info


	def __update_grade_data(self):
		"""Fetches data from SIS website, determines status of credentials and gets gradebook page

		:param none:

		:returns: boolean of status, soup html of grade page
		"""
		with requests.Session() as s:  # Create a requests session

			page = s.get(self.p_login)  # Navigate to the login page
			s_login = BeautifulSoup(page.content, features="html.parser")  # Create a parser for the gradebook

			# Prepare the data to post to the login form (apsx)
			data = {}
			data['ctl00$MainContent$username'] = self.username
			data['ctl00$MainContent$password'] = self.password
			data["__VIEWSTATE"] = s_login.select_one("#__VIEWSTATE")["value"]
			data["__VIEWSTATEGENERATOR"] = s_login.select_one("#__VIEWSTATEGENERATOR")["value"]
			data["__EVENTVALIDATION"] = s_login.select_one('#__EVENTVALIDATION')['value']

			# Post data to form, open the gradebook with session
			s.post(self.p_login, data=data)
			soup = s.get(self.p_gradebook)
			soup = BeautifulSoup(soup.content, "html.parser")
			
			# Check if succesfully logged in (student info page)
			if soup.find("div", {"class": "gb-student-assignments-grid"}):
				print("[Status] Valid credentials")
				return True, soup
			print("[Status] Invalid credentials")
			return False, None


if __name__ == "__main__":

	sis = SIS()

	username = input("SIS Username: ")
	password = getpass("SIS Password: ")

	sis.validate_credentials(username, password)
	sis.extract_assignment_data()


'''

Old SIS.py script

from bs4 import BeautifulSoup
from getpass import getpass
import requests
import re
import json
import datetime
import os
import sqlite3

class SIS:


	# Links for pages in SIS
	p_login = "https://sisstudent.fcps.edu/SVUE/"
	p_gradebook = "https://sisstudent.fcps.edu/SVUE/PXP2_Gradebook.aspx?AGU=0"

	is_logged_in = False

	def __init__(self):
		pass
	
	def isLoggedIn(self):
		return self.status


	def update_grades(self, username, password):
		"""Detects new additions to the assignments tab in SIS and updates JSON file

		:returns: notifications dictionary
		"""
		notifications = {'new':[], 'update':[]}

		curr_soup = self.soup

		# Create current JSON object, if somehow parsing fails create new JSON array
		try:
			curr_json = self.__parse_json(self.json_path)
		except:
			curr_json = []

		table = self.__get_assignment_grid(curr_soup)  # Get the gradebook table from SIS

		for tr in table.findAll("tr"):  # Loop through all the assignments in table

			title, data = self.__get_assignment_info(tr)  # Get the assignment dictionary for each row
			
			check_task, index = self.__is_task_in_list(title, curr_json)
			if not check_task:  # If the assignment is not in the array
				curr_json.append(data)  # Add to current JSON 
				notifications["new"].append({'title':title, 'date':data[title]['date_added'], 'course':data[title]['course'], 'score':data[title]['points']})  # Append to additions column
			else:
				old_score = curr_json[index][title]['points']
				new_score = data[title]['points']
				if old_score != new_score:
					notifications["update"].append({'title':title, 'date':data[title]['date_added'], 'course':data[title]['course'], 'old_score':old_score, 'new_score': new_score})  # Append to additions column
					curr_json[index][title] = data[title]
		
		return curr_json


	def __is_task_in_list(self, key, data):
		"""Saves formatted dictionary to json file

		:param key: string key to check
		:param data: gradebook JSON array to check for key

		:returns: boolean whether in gradebook or not
		"""
		for i, task in enumerate(data):  # Iterate through JSON array
			key_check = list(task.keys())[0]   # Get the assignment name for each assignment
			if key == key_check:  # If key is in the assignment keys
				return True, i
		return False, -1


	def __get_gradebook_from_sis(self):
		"""Creates session to webscrap aspx SIS gradebook

		:returns: bs4 object for raw html of gradebook page
		"""
		with requests.Session() as s:  # Create a requests session

			page = s.get(self.p_login)  # Navigate to the login page
			s_login = BeautifulSoup(page.content, features="html.parser")  # Create a parser for the gradebook

			# Prepare the data to post to the login form (apsx)
			data = {}
			data['ctl00$MainContent$username'] = self.username
			data['ctl00$MainContent$password'] = self.password
			data["__VIEWSTATE"] = s_login.select_one("#__VIEWSTATE")["value"]
			data["__VIEWSTATEGENERATOR"] = s_login.select_one("#__VIEWSTATEGENERATOR")["value"]
			data["__EVENTVALIDATION"] = s_login.select_one('#__EVENTVALIDATION')['value']

			# Post data to form, open the gradebook with session
			s.post(self.p_login, data=data)
			soup = s.get(self.p_gradebook)
			soup = BeautifulSoup(soup.content, "html.parser")
			
			# Check if succesfully logged in (student info page)
			if soup.find("div", {"class": "gb-student-assignments-grid"}):
				self.soup = soup
				return True
			return False


	def __parse_json(self, filename):
		"""Open and parse JSON file

		:param filename: path to JSON file

		:returns: parsed JSON object
		"""
		with open(filename) as json_file:
			return json.load(json_file)


	def get_status(self):
		return str(self.isLoggedIn()).lower()

	def __get_assignment_grid(self, soup):
		"""Get soup object for assignment table

		:param soup: soup of gradebook page

		:returns: soup object for assignment table
		"""
		return soup.find("div", {"class": "gb-student-assignments-grid"}).find("tbody")


	def __get_soup_from_file(self, filename):
		"""Get soup object from file

		:param filename: filename to open (html)

		:returns: soup object for page
		"""
		return BeautifulSoup(open(filename), "html.parser")
		

	def __get_assignment_info(self, row):
		"""Extract assignment information from row in assignment table.
		This has to be a hard coded sequence becuase SIS has no real html (website builder)

		:param row: soup object of row for assignment

		:returns: formatted dictionary with assignment information
		"""
		info = {}  # Empty dictionary to populate
		current_time = datetime.datetime.now().isoformat()  # Save date of addition

		for i, div in enumerate(row.findAll("div")):  # Find all the div elements in row

			if i == 0:  # First div stores the assignment title
				title = div.text
				title = title.replace("\n", "")
			elif i == 1:  # Second div stores teacher name and course name "Last, FI Course(Period)""
				# Parse out teacher name from string
				teacher = div.text.split(" ")[0]
				teacher = ''.join(teacher)
				teacher = teacher.replace(",", "")
				# Get course title from string
				course = div.text.split(" ")[3:]
				course = ' '.join(course)
				# Get period between course name
				period = (course.split("("))[1].split(")")[0]
				course = course.split("(")[0]  # Remove period string from course title
			elif i == 2:
				date = div.text.split("Due Date: ")[1]  # Get the due date (not really important)
			elif i == 3:  # Fourth div stores points of assignment "Points: 0/10(0%)"
				points = div.text
				points = points.replace("Points: ", "")
				points = points.split("(")[0]
				points = points.replace(" ", "")

		info[title] = {'teacher':teacher, 'course':course, 'period': period, 'date_added':current_time, 'date': date, 'points':points}  # Populate final dictionary for data
		
		return title, info


if __name__ == "__main__":
	username = input("SIS Username: ")
	password = getpass("SIS Password: ")
	SISpy = SIS(username,password) # username, password
	print(SISpy.isLoggedIn())
	if SISpy.isLoggedIn():
		SISpy.update_grades()
	else:
		print("Not valid!")
	#print(SIS.update_grades())

'''