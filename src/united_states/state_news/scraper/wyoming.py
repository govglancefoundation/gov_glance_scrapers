from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
from bs4 import BeautifulSoup
import logging
import xml.etree.ElementTree as ET
import re 
import json
import requests
from dotenv import load_dotenv
load_dotenv()


def main():
    url = 'https://governor.wyo.gov/api/cms/graphql' # url
    table = 'Wyoming'                               # State name
    schema = 'united_states_of_america'
    topic = 'state'                                 # The topic of the scraper
    link_variable_name = 'url'                     # Whatever the link variable name might be
    notification_title = 'Wyoming State Updates'    # Notification title
    item_name = 'article'                              # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()
    headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Fetch-Mode': 'cors',
    'Host': 'governor.wyo.gov',
    'Origin': 'https://governor.wyo.gov',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
    'Referer': 'https://governor.wyo.gov/news-releases',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Cookie': 'hkjhlkjhlj'
    }
    data = {
        "operationName": "PressReleaseSearch",
        "variables": {
            "parameters": "{\"fulltext\":\"\",\"year\":\"\",\"size\":\"10\",\"from\":\"0\"}"
        },
        "query": "query PressReleaseSearch($parameters: String!) {\n  pressReleaseSearch(parameters: $parameters) {\n    items {\n      ...PressRelease\n      __typename\n    }\n    total\n    __typename\n  }\n}\n\nfragment PressRelease on PressRelease {\n  path\n  displayText\n  releaseDate\n  htmlContent {\n    content {\n      html\n      __typename\n    }\n    __typename\n  }\n  image {\n    urls\n    __typename\n  }\n  __typename\n}"
    }

    resp = Response(table, topic, url, link_variable_name, item_name)

    response = resp.request_content_post(headers=headers, data=data)
    # print(xml_string)
    data = []
    payload = json.loads(response.text)


    """
    Edit the XML based on your needs
    """
    for item in payload['data']['pressReleaseSearch']['items']: 
        item_dict = {}
        item_dict['url'] = 'https://governor.wyo.gov/news-releases/' + (item['path']) # this is the link
        item_dict['title'] = (item['displayText'])   # this it the title
        item_dict['pubDate'] = (item['releaseDate'])  # this is the pubDate
        item_dict['description'] = item['htmlContent']['content']['html']
        print(item_dict)
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
