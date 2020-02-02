from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup, SoupStrainer
import requests
import collections
import json
import argparse
import getpass
import time
import pickle
import re
from xpath_soup import xpath_soup
from selenium.webdriver.common.action_chains import ActionChains

class SIS:

	# Links for pages in SIS
	p_login = "https://sisstudent.fcps.edu/SVUE/"
	p_gradebook = "https://sisstudent.fcps.edu/SVUE/PXP2_Gradebook.aspx?AGU=0"

	def __init__(self):

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

			table = soup.find("div", {"class": "gb-student-assignments-grid"}).find("tbody")
			for tr in table.findAll("tr"):
				for i, div in enumerate(tr.findAll("div")):
					if i == 0:
						title = div.text
					elif i == 1:
						teacher = div.text
					elif i == 2:
						date = div.text
					elif i == 3:
						points = div.text
				print([title, teacher, date, points])
			
	def find(self, soup, class_name, elem="div", one=False):
		if one:
			return soup.find(elem, {"class": re.compile(r'\b{}\b'.format(class_name))})
		return soup.findAll(elem, {"class": re.compile(r'\b{}\b'.format(class_name))})
		


SIS = SIS()

