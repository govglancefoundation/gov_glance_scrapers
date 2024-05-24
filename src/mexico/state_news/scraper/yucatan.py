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
    url = 'http://www.yucatan.gob.mx/saladeprensa/'          # url
    table = 'Yucatan'   
    schema = 'mexico'                                                                 # State name
    topic = 'state'                                                 # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'Yucatan State Updates'                    # Notification title
    item_name = 'article'                                           # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content(verify=False)
    soup = BeautifulSoup(response.content, format)
    content = soup.find_all('div',{'class':'col-sm-6'})
    data = []

    """
    Edit the XML based on your needs
    - Skip the first index of the list since its just headers of the table
    """

    # Range is only from 3 - 10 NO LESS OR MORE
    for item in content[3:10]:
        item_dict = {}

        if item.find('a'):
            item_dict['link'] = ('ver_nota.php?id=7868'+item.find('a')['href'])
        if item.find('img'):
            item_dict['image'] = ('http://www.yucatan.gob.mx' + item.find('img')['src'])
            item_dict['title'] = ('http://www.yucatan.gob.mx' + item.find('img')['alt'])
        if item.find('div', {'class':'fecha_not'}) or item.find('em').text:
            try:
                item_dict['pubDate'] = (item.find('div', {'class':'fecha_not'}).text)
            except:
                item_dict['pubDate'] = (item.find('em').text)
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
    # # #     # recent = notify.get_recent_value(cleaned)
    # # #     # message = notify.message(cleaned, recent['title'])
    # # #     # notify.notification_push(topic,notification_title, str(message))
        
    #     logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    # else:
    #     logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()