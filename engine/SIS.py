from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import json
import datetime

class SIS:

	# Links for pages in SIS
	p_login = "https://sisstudent.fcps.edu/SVUE/"
	p_gradebook = "https://sisstudent.fcps.edu/SVUE/PXP2_Gradebook.aspx?AGU=0"

	def __init__(self):

		#soup = self.get_gradebook_from_sis("1420569", "Ready2go")
		new_soup = self.get_soup_from_file("After.html")
		#old_soup = self.get_soup_from_file("Before.html")

		#self.detect_changes(new_soup, old_soup)

		self.update_grades(new_soup, "before.json")

	
	def save_dict_as_json(self, data, filename):
		with open(filename, 'w') as outfile:
			json.dump(data, outfile)

	def update_grades(self, new_soup, filename):

		old_json = self.parse_json("before.json")

		table = self.get_assignment_grid(new_soup)

		for tr in table.findAll("tr"):
			title, data = self.get_assignment_info(tr)
			if not self.is_task_in_list(title, old_json):
				old_json.append(data)
				print(data[title]['date_added'])

		#print(old_json)

		self.save_dict_as_json(old_json, filename)
		print(old_json)
		done = self.parse_json("before.json")
		print(done)


	def is_task_in_list(self, key, data):
		for task in data:
			key_check = list(task.keys())[0] 
			if key == key_check:
				return True
		return False

	def detect_changes(self, new_soup, old_soup):
		pass

	def get_gradebook_from_sis(self, username, password):

		with requests.Session() as s:  # Create a requests session
			page = s.get(self.p_login)  # Navigate to the login page
			s_login = BeautifulSoup(page.content, features="html.parser")  # Create a parser for the gradebook

			# Prepare the data to post to the login form (apsx)
			data = {}
			username = ""
			password = ""
			data['ctl00$MainContent$username'] = username
			data['ctl00$MainContent$password'] = password
			data["__VIEWSTATE"] = s_login.select_one("#__VIEWSTATE")["value"]
			data["__VIEWSTATEGENERATOR"] = s_login.select_one("#__VIEWSTATEGENERATOR")["value"]
			data["__EVENTVALIDATION"] = s_login.select_one('#__EVENTVALIDATION')['value']

			# Post data to form, open the gradebook with session
			s.post(self.p_login, data=data)
			soup = s.get(self.p_gradebook)
			soup = BeautifulSoup(soup.content, "html.parser")

			if soup.find("div", {"class": "student-info"}):
				return soup
			raise ValueError('Invalid login credentials')

			
	def parse_json(self, filename):
		with open(filename) as json_file:
			return json.load(json_file)

	def get_assignment_grid(self, page):
		return page.find("div", {"class": "gb-student-assignments-grid"}).find("tbody")

	def get_soup_from_file(self, filename):
		return BeautifulSoup(open(filename), "html.parser")

	def get_assignment_info(self, row):
		info = {}
		for i, div in enumerate(row.findAll("div")):
			if i == 0:
				title = div.text
				title = title.replace("\n", "")
			elif i == 1:
				teacher = div.text.split(" ")[0]
				teacher = ''.join(teacher)
				teacher = teacher.replace(",", "")

				course = div.text.split(" ")[3:]
				course = ' '.join(course)
				period = (course.split("("))[1].split(")")[0]
				course = course.split("(")[0]
			elif i == 2:
				date = div.text.split("Due Date: ")[1]
			elif i == 3:
				points = div.text
				points = points.replace("Points: ", "")
				points = points.split("(")[0]
				points = points.replace(" ", "")
		info[title] = {'teacher':teacher, 'course':course, 'period': period, 'date_added':datetime.datetime.now().isoformat(), 'date': date, 'points':points}
		return title, info
		


SIS = SIS()

