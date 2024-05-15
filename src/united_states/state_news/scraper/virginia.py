from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from bs4 import BeautifulSoup
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
load_dotenv()



def main():
    url = 'https://www.governor.virginia.gov/newsroom/news-releases/govnewsfeed.php/?'          # url
    table = 'Virginia'   
    schema = 'united_states_of_america'                                                         # State name
    topic = 'state'                                                  # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'Virginia State Updates'                    # Notification title
    item_name = 'items'                                              # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}



    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()
    json_payload = json.loads(response.content)


    # content = table_content.find_all('article',{'class':'news-item'})

    items = []

    """
    Edit the XML based on your needs
    """
    for item in json_payload[:10]:
        url = 'https://www.governor.virginia.gov/' + item.get('link')

        scrapped = ReadArticles(schema=schema).check_item(table, url)
        if scrapped == False:
            item = resp.log_item(item, response)
            print(item)
            entry_data = {}
            
            entry_data['title'] = item.get('headline')
            entry_data['pubDate'] = item.get('date')
            entry_data['link'] = 'https://www.governor.virginia.gov/' + item.get('link')
            entry_data['category'] = item.get('category')
            entry_data['tags'] = item.get('tag')
            entry_data['description'] = item.get('brief')

            items.append(entry_data)



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