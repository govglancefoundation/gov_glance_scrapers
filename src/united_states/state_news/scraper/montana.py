from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()
import json



def main():
    url = "https://news.mt.gov/Governors-Office/articles.json"      # url
    table = 'Montana'                               # State name
    schema = 'united_states_of_america'
    topic = 'State Governer News'                                 # The topic of the scraper
    link_variable_name = 'link'                     # Whatever the link variable name might be
    notification_title = 'Montana State Updates'    # Notification title
    item_name = None                           # Make sure that you using the right item tag name
    format = 'json'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    json_payload = json.loads(response.content)
    # print(json_payload)
    data = []



    """
    Edit the XML based on your needs
    """
    for item in json_payload[:10]: 
        # print(item)
        entry_data = {}
        # Make sure to look for all the tags in content
        entry_data['title'] = item.get('title')
        entry_data['link'] = item.get('link')
        entry_data['description'] = item.get('summary')
        entry_data['teaser'] = item.get('teaser')
        entry_data['author'] = item.get('author')
        entry_data['pubDate'] = item.get('date')
        if item.get('image') is not None:
            entry_data['image'] = item.get('image', {}).get('src')
        if item.get('agency') is not None:
            entry_data['agency_name'] = item.get('agency', {}).get('name')
            entry_data['agency_link'] = item.get('agency', {}).get('link')
        if item.get('tag') is not None:
            entry_data['tag_name'] = item.get('tag', {}).get('name')
            entry_data['tag_link'] = item.get('tag', {}).get('link')
        
        data.append(entry_data)


    # print(data)

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
    #     # recent = notify.get_recent_value(cleaned)
    #     # message = notify.message(cleaned, recent['title'])
    #     # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()