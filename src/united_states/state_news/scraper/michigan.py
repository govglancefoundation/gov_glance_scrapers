from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


def main():
    url = "https://www.michigan.gov/whitmer/sxa/search/results/?s={B7A692F7-5CC1-4AC2-8F1D-380CA54F9735}|{62E9FB6A-7717-4EF1-832C-E5ECBB9BB2D9}&itemid={DBE1F425-5DD1-4626-81EA-C19119DBC337}&sig=&autoFireSearch=true&v=%7BB7A22BE8-17FC-44A5-83BC-F54442A57941%7D&p=10&o=Article%20Date%2CDescending"      # url
    table = 'Michigan'                               # State name
    schema = 'united_states_of_america'
    topic = 'State Governer News'                                 # The topic of the scraper
    link_variable_name = 'link'                     # Whatever the link variable name might be
    notification_title = 'Michigan State Updates'    # Notification title
    item_name = 'Results'                              # Make sure that you using the right item tag name
    format = 'json'
    # notify = SendNotification()
    headers = {'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1"}

    resp = Response(table, topic, url, link_variable_name, item_name)
    json_payload, response = resp.request_content_json(headers=headers)
    # print(json_payload)
    data = []



    """
    Edit the XML based on your needs
    """
    for item in json_payload: 
        print(item)
        soup = BeautifulSoup(item["Html"], features ='html.parser')

        entry_data = {}
        # Make sure to look for all the tags in content
        if soup.find('a'):
            entry_data['link'] = 'https://www.michigan.gov' +soup.find('a')['href']
            entry_data['title'] = soup.find('a').text.lstrip().rstrip()
        if soup.find('strong'):
            entry_data['pubDate'] = soup.find('strong', {'class':'upcoming-event-location'}).text.lstrip().rstrip()
        print(entry_data)
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
    #     # recent = notify.get_recent_value(cleaned)
    #     # message = notify.message(cleaned, recent['title'])
    #     # notify.notification_push(topic,notification_title, str(message))
        
    #     logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    # else:
    #     logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()