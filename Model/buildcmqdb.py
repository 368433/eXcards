# -*- coding: utf-8 -*-

import requests, csv, os, time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
#line below added to enable headless run of code
from selenium.webdriver.chrome.options import Options

nextyearlic = 118000
#############################################
# defining custom exceptions
class NoPhysician (Exception):
	pass
#############################################
#SETTING HEAD pointer number
def save_headpointer(value):
	"""
	assumes value is a valid integer (between 1940 and current year)
	writes the value to settings file
	"""
	with open("settings.txt", 'w') as settings:
		settings.write("head = {}".format(value))
		print("Headpointer was saved as {}".format(value))

def get_headpointer():
	"""
	returns the value of head from settings file
	"""
	try:
		with open('settings.txt', 'r') as settings:
			headpointer = settings.readline()
			headpointer = int(headpointer[7:]) # reads after "head = "

		print("Headpointer found. Currently set to {}".format(str(headpointer)))
		while True:
			answer = input("Do you want to continue with this value ? Y/N: ")
			if answer in ['Y', 'y']:
				return headpointer
			elif answer in ['N','n']:
				raise
			else:
				print("Invalid answer.")
	except:
		raise

def set_headpointer():
	while True:
		try:
			usedefault = input("Setting headpointer. Do you want to start in 1940? (Y/N): ")
			if usedefault in ['N','n']:
				while True:
					try:
						startingyear = input("Enter starting year: ")
						if startingyear.isdigit() and 1940 <= int(startingyear) <= currentyear:
							headpointer = int(startingyear[2:]+'000')
							save_headpointer(headpointer)
							return headpointer
						else:
							raise
					except:
						print("Wrong entry. Enter a year between 1940 and {}".format(currentyear))
			elif usedefault in ['Y', 'y']:
				save_headpointer(40000)
				return 40000
			else:
				raise
		except:
			print("Wrong entry. Retry...")
#############################################
# SETTING UP CHROME DRIVER
def set_chrome(option):
	chrome_options = Options()
	if option == 'invisible':
		chrome_options.add_argument("--headless")
	browser = webdriver.Chrome(os.path.realpath('./chromedriver'), chrome_options=chrome_options)
	browser.get("http://www.cmq.org/bottin/index.aspx?lang=fr&a=1")
	return browser

def get_physician(headpointer, browser):
	"""
	(int, webdriver)--> dict
	looks up physician with license number headpointer
	returns a dictionary of values if exists
	returns exception if does not exist
	"""
	#entering license number and pressing return key
	champ = browser.find_element_by_id("txbNoPermis")
	champ.send_keys(headpointer, Keys.RETURN)

	#parsing the resulting html page
	results = browser.page_source
	results = BeautifulSoup(results,"html.parser")

	if results.b != None:
		next = browser.find_element_by_name("btSubmit")
		next.click()
		raise NoPhysician("License # {} does not exist".format(headpointer))

	else:
		try:
			#click on found physician
			element = browser.find_element_by_partial_link_text(str(headpointer))
			element.click()

			#parse resulting page
			resultpage = browser.page_source
			resultpage = BeautifulSoup(resultpage,"html.parser")

			#get physician name
			physician = resultpage.th.td.text
			physician = physician.replace("({0})".format(headpointer),"")
			lnamefname = physician.split(",")

			#create and populate dictionary
			md = {}
			md["license"] = int('1'+str(headpointer))
			md["fname"] = lnamefname[1].strip()
			md["lname"] = lnamefname[0].strip()
			md["sex"] = resultpage.find_all("td",string="Genre")[0].findNext("td").text.strip()
			md["license_type"] = resultpage.find_all("td",string="Permis")[0].findNext("td").text.strip()
			md["status"] = resultpage.find_all("td",string="Statut")[0].findNext("td").text.strip()
			md["address"] = resultpage.find_all("td",string="Adresse")[0].findNext("td").text
			md["address"] = md["address"].replace('\n', ';')
			md["address"] = md["address"].replace(u'\xa0', ' ')
			md["phone"] = resultpage.find_all("td",string="Téléphone")[0].findNext("td").text
			md["DataCollectionTime"] = resultpage.find("span",class_="dt").text

			specialites = resultpage.find_all("td",string="Spécialité(s)")[0].findNext("td").text
			if specialites == "":
				md["num_of_spe"] = 0
				md["specialty"] = ""
			elif "," in specialites:
				specialites = specialites.split(",")
				md["num_of_spe"] = len(specialites)
				md["specialty"] = specialites
			else:
				md["num_of_spe"] = 1
				md["specialty"] = specialites


			suite = browser.find_element_by_name("btNewsearch")
			suite.click()
			return md
		except:
			raise ValueError("Error in the try block of get physician data")

def add_physician(md):
	"""
	(dic) --> none
	writes the dictionary values to the cmqdb.csv file in append mode
	makes sure to have the leading 1 in license number
	make sure to not have return char at end of address lines
	"""
	entetes = ['license','fname', 'lname', 'sex', 'status',\
	 			'license_type', 'num_of_spe','specialty','address','phone','DataCollectionTime'  ]
	try:
		with open('cmqdb.csv', 'a') as database:
			physiciandb = csv.DictWriter(database, fieldnames = entetes)
			physiciandb.writerow(md)
	except:
		raise ValueError("Could not add data to cmqdb file")
#############################################

if __name__ == '__main__':

	try:
		headpointer = get_headpointer()
	except:
		headpointer = set_headpointer()

	# pass value "invisible" to set_chrome to make headless
	browser = set_chrome("invisible")
	new_entries = 0

	while new_entries < 10 and headpointer < nextyearlic:
		try:
			md = get_physician(headpointer, browser)
			add_physician(md)
			headpointer += 1
			new_entries += 1
		except NoPhysician as msg:
			print(msg)
			headpointer += 1
		except:
			print("A critical error occured. Terminating")
			break

	browser.close()
	print("Work completed. {} new entries added".format(new_entries))
	save_headpointer(headpointer)
