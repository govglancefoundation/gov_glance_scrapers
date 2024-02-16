from process import clean_items
from response import get_needed_items
from database import WriteItems
from notification import SendNotification
import logging


def main():
    url = 'https://apps.bea.gov/rss/rss.xml'
    table = 'bea'
    topic = 'economy'
    link_variable_name = 'link'
    notification_title = 'BEA Updates'

    logging.basicConfig(level=logging.INFO,filename=f"log/{table}.log", 
                        format='%(asctime)s - %(message)s', 
                        filemode='a')

    items = (get_needed_items(url, table, link_variable_name, topic))
    number_of_items = len(items)
    cleaned = clean_items(items)
    print(cleaned)
    # WriteItems().process_item(cleaned, table)
    # notify = SendNotification(topic)
    # recent = notify.get_recent_value(cleaned)
    # message = notify.message(cleaned, recent['title'])
    # notify.notification_push(table, message)
    
    logging.info(f'The total items needed are: {number_of_items}')



if __name__ == '__main__':
    main()