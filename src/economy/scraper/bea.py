from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()
import requests
from bs4 import BeautifulSoup

def main():
    url = 'https://apps.bea.gov/rss/rss.xml'

    table = 'bea'
    topic = 'economy'
    link_variable_name = 'link'
    notification_title = 'BEA Updates'
    item_name = 'item'

    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup()

    data = []


    """
    Edit the XML based on your needs
    """
    for item in xml_string: 
        entry_data = {}
        root = ET.fromstring(str(item))
        for child in root:
            entry_data[child.tag] = child.text.strip() if child.text else ''
        data.append(entry_data)

    items = []
    for item in data:
        scrapped = ReadArticles().check_item(table, item[link_variable_name])
        if scrapped == False:
            # item = resp.log_item(item, response)
            items.append(item)

    if len(items) > 0:
        number_of_items = len(items)
        print(number_of_items)
        cleaned = clean_items(items)
        print(cleaned)
        # WriteItems().process_item(cleaned, table, topic)
        notify = SendNotification(topic)
        recent = notify.get_recent_value(cleaned)
        message = notify.message(cleaned, recent['title'])
        notify.notification_push(notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()