from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    url = "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=righthonjustinpjtrudeau&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Right%20Hon.%20Justin%20P.%20J.%20Trudeau"
    table = 'prime_minister'
    schema = 'canada'
    topic = 'executive'
    link_variable_name = 'link'
    notification_title = 'Prime Minister Updates'
    item_name = 'entry'
    format = 'xml'
    #notify = SendNotification()


    resp = Response('prime_mister', topic, url, link_variable_name, item_name)
    response = resp.request_content()
    xml_string = BeautifulSoup(response.content, 'xml')
    name = xml_string.find('title').text
    print(name)
    data = []
    """
    Edit the XML based on your needs
    """
    for item in xml_string.find_all('entry'):
        entry_data = {}
        # Make sure to look for all the tags in content
        tags = item.find_all()
        entry_data['category'] = item.find('category')['term'].title()
        entry_data['title'] = item.find('title').text
        entry_data['description'] = item.find('summary').text
        entry_data['author'] = item.find('author').text
        entry_data['pubDate'] = item.find('updated').text
        entry_data['link'] = item.find('link')['href']
        entry_data['name'] = name
        data.append(entry_data)

    items = []
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
        WriteItems(schema=schema).process_item(cleaned, table, 'excutive')
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()