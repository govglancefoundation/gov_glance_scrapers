from process import clean_items
from database import WriteItems, ReadArticles
from response import Response, Proxy
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.nationalguard.mil/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=688&Category=11199&max=20"
    table = 'national_guard'
    topic = 'executive'
    link_variable_name = 'link'
    notification_title = 'National Guard News'
    item_name = 'item'
    format = 'xml'
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}

    #notify = SendNotification()
    
    # resp = Response(table, topic, url, link_variable_name, item_name)
    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup(format, headers=headers)
    print(response.status_code)

    data = []


    """
    Edit the XML based on your needs
    """
    for item in xml_string:
        entry_data = {}
        # Make sure to look for all the tags in content
        tags = item.find_all()
        for tag in tags:
            text = tag.text.replace('\n', '')
            entry_data[tag.name] = text
        data.append(entry_data)

    items = []
    for item in data:
        scrapped = ReadArticles().check_item(table, item[link_variable_name])
        if scrapped == False:
            item = resp.log_item(item, response)
            items.append(item)

    if len(items) > 0:
        number_of_items = len(items)
        print(number_of_items)
        cleaned = clean_items(items)
        print(cleaned)
        WriteItems().process_item(cleaned, table, topic)
        # notify = SendNotification(topic)
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()