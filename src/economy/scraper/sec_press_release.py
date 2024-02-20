from process import clean_items
from response import get_needed_items
from database import WriteItems
from notification import SendNotification
import logging


def main():
    url = "https://www.sec.gov/news/pressreleases.rss"
    table = 'sec_updates'
    topic = 'economy'
    link_variable_name = 'link'
    notification_title = 'SEC Updates'

    items = (get_needed_items(url, table, link_variable_name, topic))
    if len(items) > 0:
        number_of_items = len(items)
        cleaned = clean_items(items)
        print(cleaned)
        WriteItems().process_item(cleaned, table)
        notify = SendNotification(topic)
        recent = notify.get_recent_value(cleaned)
        message = notify.message(cleaned, recent['title'])
        notify.notification_push(table, message)
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')

if __name__ == '__main__':
    main()