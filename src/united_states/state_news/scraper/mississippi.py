from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()




def main():
    url = "https://governorreeves.ms.gov/feed/"      # url
    table = 'Mississippi'   
    schema = 'united_states_of_america'                            # State name
    topic = 'state'                                 # The topic of the scraper
    link_variable_name = 'link'                     # Whatever the link variable name might be
    notification_title = 'Mississippi State Updates'    # Notification title
    item_name = 'item'                              # Make sure that you using the right item tag name
    format = 'xml'
    # notify = SendNotification()
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}


    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup(format, headers=headers)
    print(xml_string)
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
            if tag.name == 'enclosure':
                entry_data['enclosure'] = item.find('enclosure')['url']
            else:
                text = tag.text.replace('\n', '')
                entry_data[tag.name] = text
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
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()