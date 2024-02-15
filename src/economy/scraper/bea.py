from datetime import datetime
startTime = datetime.now()
from process import clean_items
from response import get_needed_items
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
    notify = SendNotification(topic)
    recent = notify.get_recent_value(cleaned)
    message = notify.message(cleaned, recent['title'])
    notify.notification_push(table, message)
    
    logging.info(f'The total items needed are: {number_of_items}')



if __name__ == '__main__':
    main()
# def main(url: str, table: str):
#     items = clean_items(get_needed_items(url, table, 'link'))
#     for item in items:  
#         print(item)
#         # WriteItems().process_item(item, table)

# main(url, table)
# # make_rss(recent, path, name_table,recent.columns)
# # push_spaces(path, name_table, name_schema)

# most_recent_result = (df.iloc[0]['title'])
# print(most_recent_result)
# if len(df) == 1:
#     notification_message = f'{most_recent_result} is available to read'
# else:
#     notification_message = f'{most_recent_result[:80]}... and {len(df)-1} more are available to read!'

# notification_push(notification_title, notification_message, path)

print(datetime.now() - startTime)
