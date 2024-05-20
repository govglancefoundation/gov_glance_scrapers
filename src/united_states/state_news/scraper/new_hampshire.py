from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
from bs4 import BeautifulSoup
import logging
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
load_dotenv()




def main():
    url = 'https://www.governor.nh.gov/content/api/news?q=&sort=field_date%7Cdesc%7CALLOW_NULLS&view=list&page=1&size=10'           # url
    table = 'New Hampshire'   
    schema = 'united_states_of_america'                                                                 # State name
    topic = 'state'                                                 # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'New Hampshire State Updates'                    # Notification title
    item_name = 'data'                                           # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    json_payload, response = resp.request_content_json()

    # content = table_content.find_all('article',{'class':'news-item'})

    data = []

    """
    Edit the XML based on your needs
    """
    for item in json_payload: 
        print(item)
        entry_data = {}

        entry_data['title'] = item.get('fields', {}).get('title')[0]
        entry_data['pubDate'] = item.get('fields').get('field_date')[0]
        entry_data['description'] = item.get('fields', {}).get('body', {})[0]['#text']
        entry_data['link'] = 'https://www.governor.nh.gov' +(json.loads(item.get('fields', {}).get('path')[0]))['alias']

        data.append(entry_data)

    print(data)

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
        WriteItems(schema=schema).process_item(cleaned, table, topic)
    # #     # recent = notify.get_recent_value(cleaned)
    # #     # message = notify.message(cleaned, recent['title'])
    # #     # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()