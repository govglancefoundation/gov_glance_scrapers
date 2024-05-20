from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()


"""
Might need a webdriver
"""

def main():
    url = "https://apps.oregon.gov/oregon-newsroom/OR/Posts/Search?x=y&"      # url
    table = 'Oregon'   
    schema = 'united_states_of_america'                            # State name
    topic = 'state'                                 # The topic of the scraper
    link_variable_name = 'link'                     # Whatever the link variable name might be
    notification_title = 'Oregon State Updates'    # Notification title
    item_name = 'item'                             # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content(headers=headers)
    soup = BeautifulSoup(response.content, features = format).find('div', {'class':'col-md-9'})
    data = []
    posts = soup.find_all('div', {'class': 'row', 'style': 'margin-top:1em'})


    """
    Edit the XML based on your needs
    """

    for item in posts: 
        entry_data = {}
        urls = item.find_all('a')
        entry_data['link'] = 'https://apps.oregon.gov'+urls[0]['href']
        entry_data['title'] = urls[0]['title']
        entry_data['image'] = 'https://apps.oregon.gov'+urls[0].find('img')['src']
        entry_data['category'] = urls[1]['title']
        entry_data['pubDate'] = urls[2]['title']
        entry_data['creator'] = urls[-1]['title']

    
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
#         # recent = notify.get_recent_value(cleaned)
#         # message = notify.message(cleaned, recent['title'])
#         # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()