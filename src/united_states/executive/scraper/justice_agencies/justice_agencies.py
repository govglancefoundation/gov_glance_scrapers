from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    urls = [
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=alcohol-tobacco-firearms-and-explosives-bureau",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=antitrust-division",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=drug-enforcement-administration",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=executive-office-for-immigration-review",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=federal-bureau-of-investigation",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=federal-prison-industries",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=foreign-claims-settlement-commission",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=immigration-and-naturalization-service",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=justice-programs-office",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=juvenile-justice-and-delinquency-prevention-office",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=national-institute-of-corrections",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=national-institute-of-justice",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=parole-commission",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=prisons-bureau",
        "https://www.federalregister.gov/api/v1/documents.rss?conditions%5Bagencies%5D%5B%5D=united-states-marshals-service"
        ]
    schema = 'united_states_of_america'
    topic = 'Agency News'
    link_variable_name = 'link'
    notification_title = ''
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()


    

    
    for url in urls:
        data = []
        resp = Response('justice_agencies', topic, url, link_variable_name, item_name)
        response = resp.request_content()
        xml_string = BeautifulSoup(response.content, 'xml')
        agency_name = xml_string.find('title').text
        print(agency_name)
        """
        Edit the XML based on your needs
        """
        for item in xml_string.find_all('item'): 
            print(item)
            entry_data = {}
            # Make sure to look for all the tags in content
            tags = item.find_all()
            for tag in tags:
                if tag.name == 'enclosure':
                    entry_data['enclosure'] = item.find('enclosure')['url']
                if tag.name == 'creator':
                    entry_data['creator'] = 'Agriculture Department'
                if tag.name == 'category':
                    categories = item.find_all('category')
                    categories_text = [i.text for i in categories]
                    entry_data['category'] = str(categories_text)
                else:
                    text = tag.text.replace('\n', '')
                    entry_data[tag.name] = text
                entry_data['agency'] = agency_name.replace('Federal Register Documents from ', '')
            data.append(entry_data)

        items = []
        print(data)
        for item in data:
            scrapped = ReadArticles(schema=schema).check_item('justice', item[link_variable_name])
            if scrapped == False:
                item = resp.log_item(item, response)
                items.append(item)

        if len(items) > 0:
            number_of_items = len(items)
            print(number_of_items)
            cleaned = clean_items(items)
            print(cleaned)
            WriteItems(schema=schema).process_item(cleaned, 'justice', 'executive')
            # recent = notify.get_recent_value(cleaned)
            # message = notify.message(cleaned, recent['title'])
            # notify.notification_push(topic,notification_title, str(message))
            
            logging.info(f'The total items needed are: {number_of_items}')
        else:
            logging.info(f'No new items found for {agency_name.title()}')



if __name__ == '__main__':
    main()