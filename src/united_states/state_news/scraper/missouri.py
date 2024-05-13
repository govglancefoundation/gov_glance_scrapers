from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
from bs4 import BeautifulSoup
import logging
import xml.etree.ElementTree as ET
import re 
from dotenv import load_dotenv
load_dotenv()


def main():
    url = 'https://governor.mo.gov/press-releases'           # url
    table = 'Missouri'   
    schema = 'united_states_of_america'                                                                 # State name
    topic = 'state'                                                 # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'Missouri State Updates'                    # Notification title
    item_name = 'article'                                           # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    soup = BeautifulSoup(response.content, format)
    table_content = soup.find('div', {'class':'view-content'})
    content = table_content.find_all("div", {"class":'views-row'})

    data = []
    print(len(content))

    """
    Edit the XML based on your needs
    """
    for item in content: 
        item_dict = {}

        if item.find('a') is not None:
            item_dict['title'] = item.find('a').text
            item_dict['link'] = 'https://governor.mo.gov'+(item.find('a')['href']) # this is the pubDate
        if item.find('time') is not None:
            item_dict['pubDate'] = item.find('time')['datetime']
        if item.find('p') is not None:
            item_dict['description'] = item.find('p').text
        data.append(item_dict)

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
        
    #     logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    # else:
    #     logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()