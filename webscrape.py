#Icharts
#Written by Chris Walker

from bs4 import BeautifulSoup
import requests
import smtplib
import zipfile
import urllib
import os, shutil

def webscrape():
	#Error handling if FAA website has changed
	try:
		#Open table on FAA website conataining Chart data
		sectionalData = buildSectional()
		url = 'http://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/?viewType=Print&viewClass=Print'
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, 'lxml')
		table = soup.find(class_='striped')
		table.find_all('tr')

		#Put city,version and download link into temp file
		map_data = []
		temp = open("database", 'w+')
		temp.truncate()

		downloader = urllib.URLopener()
		i = 0
		for row in table.find_all('tr')[1:]:
			col = row.find_all('td')
			city = col[0].string.strip()
			link = col[1].find('a').get('href')
			sectional = sectionalData[i]
			i += 1
			version = col[1].get_text().split()
			version[4] = version[4][0:4]
			startDate = ' '.join(version[2:5])
			version = version[0].strip()

			m = col[2].get_text().split()
			m[4] = m[4][0:4]
			endDate = ' '.join(m[2:5])

			temp.write(city + ',' + version + ',' + startDate +','+ endDate +','+ sectional +'\n')

			filePath = "./"+ city +"/"+ version +"/"
			fileName = filePath + city + version + ".zip"

			if os.path.isdir("./"+ city):
				for file in os.listdir("./"+ city):
					if version in file:
						break
					else:
						shutil.rmtree("./"+ city)
						break

			if not os.path.isdir(filePath):
				os.mkdir(city, 0o777)
				os.mkdir(city +"/"+ version, 0o777)
				downloader.retrieve(link, fileName)

				unzip = zipfile.ZipFile(fileName, 'r')
				unzip.extractall(filePath)
				unzip.close()

				os.remove(fileName)

				tifFileName = ""
				for file in os.listdir(filePath):
					if file.endswith(".tif"):
						tifFileName = file
				gdalFileName = filePath + tifFileName

		       		model = open("./"+city +"/" + city +"model", 'w+')
	       			model.truncate()
       				model.write(city + ',' + version + ',' + startDate +','+ endDate +','+ sectional +'\n')
				zipname = filePath + city + ".zip"
				tileWithGDAL(gdalFileName, filePath, zipname)

	except Exception, e:
#		server = smtplib.SMTP('smtp.gmail.com', 587)

#		server.ehlo()
#		server.starttls()
#		server.ehlo()

#		server.login("ichartgroup@gmail.com", "icharts321")
#		msg = "Webscraper Failed: "
		print e
	#	server.sendmail("ichartgroup@gmail.com", "walker60@wwu.edu", msg)
		return

# A .tif should exist in the file path when this is called.
def tileWithGDAL(fName, fPath, zipName):
	os.system("gdal_translate -of vrt -expand rgba '"+ fName +"' '"+ fPath +"translated.vrt'")
	os.system("gdal2tiles.py -z 4-6 -p 'raster' '"+ fPath +"translated.vrt'")
	for file in os.listdir(fPath):
		if os.path.isfile(os.path.join(fPath, file)):
			os.remove(os.path.join(fPath, file))
	os.chmod('translated', 0o777)

	zipf = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk('translated/'):
		for file in files:
			if 'openlayers.html' not in file and 'tilemapresource.xml' not in file:
				zipf.write(os.path.join(root, file))
	shutil.rmtree('./translated')

def buildSectional():
	url = 'https://www.faa.gov/air_traffic/flight_info/aeronav/productcatalog/vfrcharts/sectional/'
	response = requests.get(url)
	html = response.text
	soup = BeautifulSoup(html, 'lxml')
	table = soup.find(class_='striped')
	table.find_all('tr')
	sectional = []
	for row in table.find_all('tr')[1:]:
		col = row.find_all('td')
		sectional.append(col[1].string.strip()[1:])
	return sectional
		
webscrape()