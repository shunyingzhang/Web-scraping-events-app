import requests
import selectorlib
import time
import sqlite3
from send_email import send_email

URL = 'https://programmer100.pythonanywhere.com/tours/'

connection = sqlite3.connect('data.db')

def scrape(url):
    """Scrape the page source from URL"""
    response = requests.get(url)
    source = response.text
    return source

def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file('extract.yaml')
    return extractor.extract(source)['tours']

def read(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM event WHERE band=? AND city=? AND date=?', (band, city, date))
    return cursor.fetchall()

def store(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute('INSERT INTO event VALUES(?, ?, ?)', row)
    connection.commit()

if __name__ == '__main__':
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)

        if extracted != 'No upcoming tours':
            content = read(extracted)
            if not content:
                store(extracted)
                send_email(extracted)
        time.sleep(3)