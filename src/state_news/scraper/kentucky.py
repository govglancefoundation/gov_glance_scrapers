from process import clean_items
from database import WriteItems, ReadArticles
from response import Response, Proxy
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import json
load_dotenv()



def convert_strin_todict(content):
    
    edit1 = content.split('(',1)[1]
    response = edit1.split(');',1)[0]
    return json.loads(response)


def main():
    url = "https://newsroom.ky.gov/_layouts/15/Fwk.Webparts.Agency.Ui/ActivityStream/GetActivities.ashx?callback=jQuery1124022783786884131396_1698176239283&PageIndex=0&Agencies=Lieutenant+Governor%7COffice+of+the+Governor&SearchText=&Category=&ShowDateAsHeader=false"
    table = 'kentucky'
    topic = 'state'
    link_variable_name = 'link'
    notification_title = 'Kentucky State Updates'
    item_name = None
    format = 'html.parser'
    notify = SendNotification()
    proxy = Proxy().get_proxy()
    proxies = {"http": proxy, "https": proxy}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

    resp = Response(table, topic, url, link_variable_name, item_name)

    response = resp.request_content(proxies=proxies, headers=headers)
    xml_string = convert_strin_todict(response.text)['Results']
    data = []

    """
    Edit the XML based on your needs
    """
    for item in xml_string[:1]: 
        item = (item['Items'])[0]
        print(item)
        entry_data = {}
        # Make sure to look for all the tags in content
        entry_data['link'] = (item['LinkUrl'])
        entry_data['title'] = (item['Title'])
        entry_data['pubDate'] = item['DisplayDateContent']
        entry_data['description'] = item['Summary']
        data.append(entry_data)


    print(data)
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