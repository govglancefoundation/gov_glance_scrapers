from process import clean_items
from database import WriteItems, ReadArticles
from response import Response, Proxy
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
import json


def convert_strin_todict(content):
    
    edit1 = content.split('(',1)[1]
    response = edit1.split(');',1)[0]
    return json.loads(response)

def main():
    # url = "https://www.state.gov/rss-feed/press-releases/feed/"
    url = "https://www.state.gov/rss-feed/press-releases/feed/"
    table = 'state'
    topic = 'executive'
    link_variable_name = 'link'
    notification_title = 'Dept. of State Updates'
    item_name = 'item'
    format = 'xml'
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}
    #notify = SendNotification()
    # proxy = Proxy().get_proxy()
    # proxies = {"http": proxy, "https": proxy}
    
    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup(format, headers=headers)
    
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
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()