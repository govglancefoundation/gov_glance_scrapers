from process import clean_items
from database import WriteItems, ReadArticles
from response import FreeProxy, Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()
from lxml.html import fromstring
from bs4 import BeautifulSoup



def main():
    url = "https://mn.gov/governor/rest/rss/Newsroom?id=1055-35332&detailPage=/governor/newsroom/press-releases/index.jsp"      # url
    table = 'Minnesota'   
    schema = 'united_states_of_america'                            # State name
    topic = 'state'                                 # The topic of the scraper
    link_variable_name = 'link'                     # Whatever the link variable name might be
    notification_title = 'Minnesota State Updates'    # Notification title
    item_name = 'item'                              # Make sure that you using the right item tag name
    format = 'xml'
    # notify = SendNotification()
    

    resp = Response(table, topic, url, link_variable_name, item_name)
    # xml_string, response = resp.request_content(format, verify=False)
    response = resp.requests_(verify=False)
    print(response.content)
    xml_string = BeautifulSoup(response.content, 'xml').find_all('item')
    # resp = FreeProxy(table, topic)
    # soup, response = resp.use_free_proxies_request(url)
    # print(response.content)
    # xml_string = soup.find_all('item')
    # xml_string, response = resp.get_soup(format, verify=False)
    # print(response.status_code)
    # print(response.content)
    data = []



    """
    Edit the XML based on your needs
    """
    for item in xml_string: 
        # print(item)
        entry_data = {}
        # Make sure to look for all the tags in content
        tags = item.find_all()
        for tag in tags:
            if tag.name == 'pubdate':
                entry_data['pubDate'] = item.find('pubdate')
            else:
                text = tag.text.replace('\n', '')
                entry_data[tag.name] = text
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
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()