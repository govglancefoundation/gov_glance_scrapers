from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from bs4 import BeautifulSoup
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
load_dotenv()



def main():
    url = 'https://governor.ohio.gov/wps/wcm/connect/gov/Ohio%20Content%20English/governor?source=library&srv=cmpnt&cmpntid=67577e5a-f3af-4498-a9e3-0696d21ac7c9&location=Ohio+Content+English%2F%2Fgovernor%2Fmedia%2Fnews-and-media&category='           # url
    table = 'Ohio'   
    schema = 'united_states_of_america'                                                                 # State name
    topic = 'state'                                                 # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'Ohio State Updates'                    # Notification title
    item_name = 'data'                                           # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()
    



    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    json_payload = json.loads(response.content)    

    # content = table_content.find_all('article',{'class':'news-item'})

    data = []

    """
    Edit the XML based on your needs
    """
    for item in json_payload[:10]: 
        print(item)
        entry_data = {}
        
        entry_data['uuid'] = item.get('uuid')
        entry_data['title'] = item.get('title')
        if item.get('url'):
            entry_data['link'] = 'https://governor.ohio.gov' +item.get('url') 
        entry_data['description'] = item.get('summary')
        entry_data['pubDate'] = item.get('startTimeWCM')
        if item.get('thumbnail'):
            entry_data['thumbnail'] = 'https://governor.ohio.gov' + item.get('thumbnail')
        else:
            entry_data['thumbnail'] = None

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