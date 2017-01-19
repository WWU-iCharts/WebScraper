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
		url = 'http://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/?viewType=Print&viewClass=Print'
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, 'lxml')
		table = soup.find(class_='striped')
		table.find_all('tr')

		#Put city,version and download link into temp file
		map_data = []
		temp = open("temp", 'w+')
		temp.truncate()

		downloader = urllib.URLopener()
		for row in table.find_all('tr')[1:]:
			col = row.find_all('td')
			city = col[0].string.strip()

			link = col[1].find('a').get('href')
			version = col[1].get_text().split()
			version = version[0]
			temp.write(city + ',' + version + ',' + link + '\n')


			filePath = "./"+ city +"/"+ version +"/"
			fileName = filePath + city + version + ".zip"
			
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
				
				tileWithGDAL(gdalFileName, filePath, fileName)

	except Exception, e:
		server = smtplib.SMTP('smtp.gmail.com', 587)

		server.ehlo()
		server.starttls()
		server.ehlo()

		server.login("ichartgroup@gmail.com", "icharts321")
		msg = "Webscraper Failed: "
		print e
		server.sendmail("ichartgroup@gmail.com", "walker60@wwu.edu", msg)
		return

# A .tif should exist in the file path when this is called.
def tileWithGDAL(fName, fPath, zipName):
	os.system("gdal_translate -of vrt -expand rgba '"+ fName +"' '"+ fPath +"translated.vrt'")
	os.system("gdal2tiles.py -p 'raster' '"+ fPath +"translated.vrt'")
	for file in os.listdir(fPath):
		if os.path.isfile(os.path.join(fPath, file)):
			os.remove(os.path.join(fPath, file))
	os.chmod('translated', 0o777)
	shutil.make_archive(zipName[1:], 'zip', 'translated/')
	
	zipf = zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk('translated/'):
		for file in files:
			zipf.write(os.path.join(root, file))
	
	shutil.rmtree('./translated')
	
webscrape()