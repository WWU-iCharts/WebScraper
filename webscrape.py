#!/usr/bin/python
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen
from bs4 import BeautifulSoup
import requests
import os

DEBUGMODE = True

url = 'http://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/?viewType=Print&viewClass=Print'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'lxml')
table = soup.find(class_='striped')

temp = open("temp", 'w+')
temp.truncate()

for row in table.find_all('tr')[1:]:
	col = row.find_all('td')
	city = col[0].string.strip()
	link = col[1].find('a').get('href')
	version = col[1].get_text().split()[0]
	startdate = col[1].get_text().split()[2] + ' ' + col[1].get_text().split()[3] + ' ' + col[1].get_text().split()[4].split('G')[0]
	enddate = col[2].get_text().split()[2] + ' ' + col[2].get_text().split()[3] + ' ' + col[2].get_text().split()[4].split('G')[0]

	directory = (version + '_'+city+"_UNTILED")
	directory = "".join(e for e in directory if e.isalnum() or e == '_')

	if not os.path.exists(directory):
		os.makedirs(directory)
		url = urlopen(link)
		ZipFile(StringIO(url.read())).extractall("./" + directory)

	temp.write(city + ',' + version + ','  + startdate + ',' + enddate + ',' + link + '\n')
