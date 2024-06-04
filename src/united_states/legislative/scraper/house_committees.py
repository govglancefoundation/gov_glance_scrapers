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
    urls = ["https://docs.house.gov/Committee/RSS.ashx?Code=AG00", # Committee on Agriculture Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=AP00", # Committee on Appropriations Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=AS00", # Committee on Armed Services Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=BU00", # Committee on the Budget Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=ED00", # Committee on Education and the Workforce Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=IF00", # Committee on Energy and Commerce Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=SO00", # Committee on Ethics Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=BA00", # Committee on Financial Services Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=FA00", # Committee on Foreign Affairs Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=HM00", # Committee on Homeland Security Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=HA00", # Committee on House Administration Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=JU00", # Committee on the Judiciary Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=II00", # Committee on Natural Resources Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=GO00", # Committee on Oversight and Accountability Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=RU00", # Committee on Rules Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=SY00", # Committee on Science, Space, and Technology Meeting Feed 
    "https://docs.house.gov/Committee/RSS.ashx?Code=SM00", # Committee on Small Business Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=PW00", # Committee on Transportation and Infrastructure Meeting Feed
    "https://docs.house.gov/Committee/RSS.ashx?Code=VR00"] # Committee on Veterans' Affairs Meeting Feed
    
    scraper_name = 'house_committees'
    schema = 'united_states_of_america'
    topic = 'legislative'
    link_variable_name = 'link'
    notification_title = 'House Committee Meetings Updates'
    item_name = 'item'
    format = 'xml'
    # #notify = SendNotification()

    

    for url in urls:
        print(url)
        data = []
        resp = Response(scraper_name, topic, url, link_variable_name, item_name)
        xml_string, response = resp.get_soup(format)
        print(response.status_code)
        soup = BeautifulSoup(response.content, features='xml')
        table = soup.find('title').text.replace('U.S. House of Representatives - ','').replace("'", '').replace(',','').replace(' ','_')
        print(table)
        """
        Edit the XML based on your needs
        """
        for item in xml_string:
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