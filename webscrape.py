from bs4 import BeautifulSoup
import requests

url = 'http://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/?viewType=Print&viewClass=Print'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'lxml')
database = soup.find(class_='striped')

map_data = []
temp = open("temp", 'w+')
temp.truncate()

for row in table.find_all('tr')[1:]:
    col = row.find_all('td')

    city = col[0].string.strip()

    link = col[1].find('a').get('href')

    version = col[1].get_text().split()
    version = version[0]
    temp.write(city + ',' + version + ',' + link + '\n')
