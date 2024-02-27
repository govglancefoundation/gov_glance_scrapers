from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()


# def main():
#     url = "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bcorrection%5D=0&conditions%5Bpresident%5D=&conditions%5Bpresidential_document_type%5D=executive_order&conditions%5Bsigning_date%5D%5Byear%5D=&conditions%5Btype%5D%5B%5D=PRESDOCU"
#     table = 'executive_orders'
#     topic = 'executive'
#     link_variable_name = 'link'
#     notification_title = 'White House Updates'



#     items = (get_needed_items(url, table, link_variable_name, topic))[:1]
#     if len(items) > 0:
#         number_of_items = len(items)
#         cleaned = clean_items(items)
#         print(cleaned)
#         WriteItems().process_item(cleaned, table, topic)
#         notify = SendNotification(topic)
#         recent = notify.get_recent_value(cleaned)
#         message = notify.message(cleaned, recent['title'])
#         notify.notification_push(notification_title, str(message))
        
#         logging.info(f'The total items needed are: {number_of_items}')
#     else:
#         logging.info(f'No new items found for {table.title()}')



# if __name__ == '__main__':
#     main()




def main():
    url = "https://www.nasa.gov/rss/dyn/breaking_news.rss"
    table = 'nasa'
    topic = 'science_and_tech'
    link_variable_name = 'link'
    notification_title = 'Medical Safety Alerts'
    item_name = 'item'
    notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup()
    data = []



    """
    Edit the XML based on your needs
    """
    for item in xml_string: 
        print(item)
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



    items = []
    for item in data:
        scrapped = ReadArticles().check_item(table, item[link_variable_name])
        if scrapped == False:
            item = resp.log_item(item, response)
            items.append(item)

    
    if len(items) > 0:
        number_of_items = len(items)
        print(number_of_items)
        cleaned = clean_items(items)
        print(cleaned)
        WriteItems().process_item(cleaned, table, topic)
        recent = notify.get_recent_value(cleaned)
        message = notify.message(cleaned, recent['title'])
        notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()