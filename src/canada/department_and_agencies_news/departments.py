from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    urls = [
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=agricultureagrifood&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Agriculture%20and%20Agri-Food%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadianheritage&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Heritage",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=crownindigenousrelationsandnorthernaffairscanada&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Crown-Indigenous%20Relations%20and%20Northern%20Affairs%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofemploymentandsocialdevelopment&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Employment%20and%20Social%20Development%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentoftheenvironment&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Environment%20and%20Climate%20Change%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentfinance&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Department%20of%20Finance%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=fisheriesoceans&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Fisheries%20and%20Oceans%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofforeignaffairstradeanddevelopment&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Global%20Affairs%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofhealth&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Health%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofcitizenshipandimmigration&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Immigration,%20Refugees%20and%20Citizenship%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=indigenousservicescanada&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Indigenous%20Services%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofindustry&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Innovation,%20Science%20and%20Economic%20Development%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentjustice&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Department%20of%20Justice%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentnationaldefense&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=National%20Defence",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=publicsafetycanada&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Public%20Safety%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofpublicworksandgovernmentservices&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Public%20Services%20and%20Procurement%20Canada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentoftransport&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Transport%20Canada"
        ]
    schema = 'canada'
    topic = 'Department News'
    link_variable_name = 'link'
    notification_title = ''
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()


    

    
    for url in urls:
        data = []
        resp = Response('news_by_departments', topic, url, link_variable_name, item_name)
        response = resp.request_content()
        xml_string = BeautifulSoup(response.content, 'xml')
        table = xml_string.find('title').text
        print(table)
        """
        Edit the XML based on your needs
        """
        for item in xml_string.find_all('entry'):
            entry_data = {}
            # Make sure to look for all the tags in content
            tags = item.find_all()
            entry_data['title'] = item.find('title').text
            entry_data['description'] = item.find('summary').text
            entry_data['author'] = item.find('author').text
            entry_data['category'] = item.find('category')['term'].title()
            entry_data['pubDate'] = item.find('updated').text
            entry_data['link'] = item.find('link')['href']
            data.append(entry_data)


        items = []
        print(data)
        for item in data:
            scrapped = ReadArticles(schema=schema).check_item(table.replace('-','_'), item[link_variable_name])
            if scrapped == False:
                item = resp.log_item(item, response)
                items.append(item)

        if len(items) > 0:
            number_of_items = len(items)
            print(number_of_items)
            cleaned = clean_items(items)
            print(cleaned)
            WriteItems(schema=schema).process_item(cleaned, table, 'executive')
            # recent = notify.get_recent_value(cleaned)
            # message = notify.message(cleaned, recent['title'])
            # notify.notification_push(topic,notification_title, str(message))
            
            logging.info(f'The total items needed are: {number_of_items}')
        else:
            logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()