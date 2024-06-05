from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    urls = [
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=ab48&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Alberta",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=bc59&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=British%20Columbia",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=mb46&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Manitoba",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=nb13&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=New%20Brunswick",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=nl10&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Newfoundland%20and%20Labrador",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=nt61&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Northwest%20Territories",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=ns12&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Nova%20Scotia",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=nu62&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Nunavut",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=on35&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Ontario",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=pe11&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Prince%20Edward%20Island",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=qc24&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Quebec",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=sk47&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Saskatchewan",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?location=yt60&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Yukon"
        ]
    schema = 'canada'
    topic = 'Provinces and Territories News'
    link_variable_name = 'link'
    notification_title = 'Dept. of Defense Updates'
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()


    

    
    for url in urls:
        data = []
        resp = Response('news_by_area', topic, url, link_variable_name, item_name)
        response = resp.request_content()
        xml_string = BeautifulSoup(response.content, 'xml')
        table = xml_string.find('title').text
        print(table)
        """
        Edit the XML based on your needs
        """
        for item in xml_string.find_all('entry')[:1]:
            entry_data = {}
            # Make sure to look for all the tags in content
            tags = item.find_all()
            entry_data['category'] = item.find('category')['term'].title()
            entry_data['title'] = item.find('title').text
            entry_data['description'] = item.find('summary').text
            entry_data['author'] = item.find('author').text
            entry_data['pubDate'] = item.find('updated').text
            entry_data['link'] = item.find('link')['href']
            data.append(entry_data)


        items = []
        print(data)
        for item in data:
            scrapped = ReadArticles(schema=schema).check_item(table, item[link_variable_name])
            if scrapped == False:
                item = resp.log_item(item, response)
                items.append(item)

        if len(items) > 0:
            number_of_items = len(items)
            print(number_of_items)
            cleaned = clean_items(items)
            print(cleaned)
            WriteItems(schema=schema).process_item(cleaned, table, 'executive')
            # recent = notify.get_recent_value(cleaned)
            # message = notify.message(cleaned, recent['title'])
            # notify.notification_push(topic,notification_title, str(message))
            
            logging.info(f'The total items needed are: {number_of_items}')
        else:
            logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()