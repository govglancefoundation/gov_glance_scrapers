from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

def main():


    urls = []
    schema = 'united_states_of_america'
    topic = 'Economy'
    link_variable_name = 'link'
    notification_title = ''
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()

    with open('united_states/economy/scraper/federal_reserve/federal_reserve_feeds.json', 'r') as f:
        federal_reserve_feeds = (json.load(f))

    for media_type in federal_reserve_feeds:
        key = list(media_type.keys())[0]
        for feed in media_type[key]:
            feed_url = feed['url']
            print(feed_url)
            feed_title = feed['title']
            feed_media_type = feed['media_type']



            data = []
            resp = Response('federal_reserve', topic, feed_url, link_variable_name, item_name)
            response = resp.request_content()
            xml_string = BeautifulSoup(response.content, 'xml')
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
                    elif tag.name == 'creator':
                        entry_data['creator'] = 'Agriculture Department'
                    elif tag.name == 'date':
                        entry_data['pubDate'] = item.find('dc:date').text
                    elif tag.name == 'category':
                        categories = item.find_all('category')
                        categories_text = [i.text for i in categories]
                        entry_data['category'] = str(categories_text)
                    else:
                        text = tag.text.replace('\n', '')
                        entry_data[tag.name] = text
                    entry_data['feedTitle'] = feed_title
                    entry_data['mediaType'] = feed_media_type
                data.append(entry_data)

            items = []
            print(data)
            for item in data:
                scrapped = ReadArticles(schema=schema).check_item('federal_reserve', item[link_variable_name])
                if scrapped == False:
                    item = resp.log_item(item, response)
                    items.append(item)

            if len(items) > 0:
                number_of_items = len(items)
                print(number_of_items)
                cleaned = clean_items(items)
                print(cleaned)
                WriteItems(schema=schema).process_dynamic_columns(cleaned, 'federal_reserve', 'economy')
                # recent = notify.get_recent_value(cleaned)
                # message = notify.message(cleaned, recent['title'])
                # notify.notification_push(topic,notification_title, str(message))
                
                logging.info(f'The total items needed are: {number_of_items}')
            else:
                logging.info(f'No new items found for {feed_title}')



if __name__ == '__main__':
    main()