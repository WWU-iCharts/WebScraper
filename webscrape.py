from bs4 import BeautifulSoup
import requests
import smtplib



def webscrape():
    url = 'http://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/?viewType=Print&viewClass=Print'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find(class_='striped')

    try:
        table.find_all('tr')
    except Exception, e:
        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login("ichartgroup@gmail.com", "icharts321")
        msg = "Webscraper Failed, FAA website might have changed"
        server.sendmail("ichartgroup@gmail.com", "walker60@wwu.edu", msg)
        return

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


webscrape()
