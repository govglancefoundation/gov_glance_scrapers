from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    url = 'http://fetchrss.com/rss/5f8e367522b58768783d2392636be3fe9f9b8c1494779a12.xml'
    table = 'election_assistance_commission'
    schema = 'united_states_of_america'
    topic = 'election'
    link_variable_name = 'link'
    notification_title = ''
    item_name = 'entry'
    format = 'xml'
    #notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    xml_string = BeautifulSoup(response.content, 'xml')
    # name = xml_string.find('title').text
    # print(name)
    data = []
    """
    Edit the XML based on your needs
    """
    for item in xml_string.find_all('item'): 
        print(item)
        entry_data = {}
        # Make sure to look for all the tags in content
        tags = item.find_all()
        for tag in tags:
            if tag.name == 'enclosure':
                entry_data['enclosure'] = item.find('enclosure')['url']
            if tag.name == 'creator':
                entry_data['creator'] = item.find('creator').text
            else:
                text = tag.text.replace('\n', '')
                entry_data[tag.name] = text
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
        WriteItems(schema=schema).process_item(cleaned, table, 'election')
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()