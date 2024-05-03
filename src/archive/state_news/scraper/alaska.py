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
    url = "https://gov.alaska.gov/newsroom/"      # url
    table = 'alaska' 
    schema = 'united_states_of_america'                              # State name
    topic = 'state'                                 # The topic of the scraper
    link_variable_name = 'url'                     # Whatever the link variable name might be
    notification_title = 'alaska State Updates'    # Notification title
    item_name = 'article'                              # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    soup = BeautifulSoup(response.content, format)
    xml_string = soup.find('article')
    # print(xml_string)
    data = []
    print(len(xml_string))


    """
    Edit the XML based on your needs
    """
    for item in xml_string.find_all('article'): 
        print(item)
        item_dict = {}
        # Make sure to look for all the tags in content
        # tags = item.find_all()
        # for tag in tags:
        #     if tag.name == 'enclosure':
        #         entry_data['enclosure'] = item.find('enclosure')['url']
        #     else:
        #         text = tag.text.replace('\n', '')
        #         entry_data[tag.name] = text
        item_dict['postId'] = (item['id'])             # this is the id
        item_dict['url'] = (item.find('a', class_='')['href']) # this is the link

        if (item.find('time')) != None:
            item_dict['pub_date'] = (item.find('time').text)  # this is the pubDate
        if item.find('span', class_=re.compile(r'published')) != None:
            item_dict['pubDate'] = re.sub('[^ .,a-zA-Z0-9]', '',item.find('span', class_='published').text)
        if item.find('h4') == None:
            title =''
            item_dict['title'] = (title)
        else:
            item_dict['title'] = item.find('h4').text   # this it the title
        if item.find('p').text == 'Download':
            item_dict['description'] = ''
        else:
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
    #     # recent = notify.get_recent_value(cleaned)
    #     # message = notify.message(cleaned, recent['title'])
    #     # notify.notification_push(topic,notification_title, str(message))
        
    #     logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    # else:
    #     logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()