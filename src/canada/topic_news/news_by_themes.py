from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    urls = [
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=artsandmedia&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Arts%20and%20media",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=benefits&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=benefits",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=businessandindustry&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Business%20and%20industry"
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=canadaandtheworld&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Canada%20and%20the%20world",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=nationalsecurityanddefence&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=National%20security%20and%20defence",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=environmentandnaturalresources&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Environment%20and%20natural%20resources"
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=health&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Health",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=immigrationandcitizenship&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Immigration%20and%20citizenship",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=jobsandtheworkplace&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Jobs%20and%20the%20workplace",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=moneyandfinances&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Money%20and%20finances",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=scienceandinnovation&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Science%20and%20innovation",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=taxes&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=taxes",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?topic=transportandinfrastructure&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Transport%20and%20infrastructure",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?subject=travel&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=travel"
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