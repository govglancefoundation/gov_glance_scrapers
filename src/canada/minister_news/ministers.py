from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    urls = [
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honahmeddhusse&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Ahmed%20D.%20Hussen",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honanitaanand&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Anita%20Anand",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honarifvirani&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Arif%20Virani",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honcarlaqualtrough&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Carla%20Qualtrough",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honchrystiafreeland&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Chrystia%20Freeland",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=hondanvandal&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Dan%20Vandal",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=hondianelebouthillier&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Diane%20Lebouthillier",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=hondominicleblanc&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Dominic%20LeBlanc",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honfilomenatassi&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Filomena%20Tassi",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honfran%C3%A7oisphilippechampagne&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Fran%C3%A7ois-Philippe%20Champagne",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honginettepetitpastaylor&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Ginette%20Petitpas%20Taylor",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=hongudiehutchings&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Gudie%20Hutchings",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honharjitsinghsajjan&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Harjit%20Singh%20Sajjan",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honjanephilpott&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Jane%20Philpott",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honjeanyvesduclos&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Jean-Yves%20Duclos",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honjennasudds&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Jenna%20Sudds",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honjonathanwilkinson&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Jonathan%20Wilkinson",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honkamalkhera&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Kamal%20Khera",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honkarinagould&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Karina%20Gould",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honkenthehr&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Kent%20Hehr",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honlawrencemacaulay&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Lawrence%20MacAulay",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmarciien&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Marci%20Ien",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmarcmiller&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Marc%20Miller",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmarieclaudebibeau&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Marie-Claude%20Bibeau",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmarkholland&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Mark%20Holland",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmaryng&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Mary%20Ng",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honmelaniejoly&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20M%C3%A9lanie%20Joly",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honpablorodriguez&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Pablo%20Rodriguez",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honrandyboissonnault&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Pascale%20St-Onge",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honpatriciaa.hajdu&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Patricia%20A.%20Hajdu",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honrandyboissonnault&sort=publishedDate&orderBy=desc&publishedDate%3E=2020-08-09&pick=50&format=atom&atomtitle=Hon.%20Randy%20Boissonnault",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honrechievaldez&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Rechie%20Valdez",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honseamusoregan&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Seamus%20O%E2%80%99Regan",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honseanfraser&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Sean%20Fraser",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honsorayamartinezferrada&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Soraya%20Martinez%20Ferrada",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honstevenguilbeault&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Steven%20Guilbeault",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honterrybeech&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Terry%20Beech",
        "https://api.io.canada.ca/io-server/gc/news/en/v2?minister=honyaarasaks&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Hon.%20Ya%E2%80%99ara%20Saks"
        ]
    schema = 'canada'
    topic = 'Minister News'
    table = 'ministers'
    link_variable_name = 'link'
    notification_title = ''
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()


    
    
    for url in urls:
        data = []
        resp = Response(table, topic, url, link_variable_name, item_name)
        response = resp.request_content()
        xml_string = BeautifulSoup(response.content, 'xml')
        rss_title = xml_string.find('title').text
        print(rss_title)
        """
        Edit the XML based on your needs
        """
        for item in xml_string.find_all('entry')[:1]:
            entry_data = {}
            # Make sure to look for all the tags in content
            tags = item.find_all()
            entry_data['category'] = item.find('category')['term'].title()
            entry_data['title'] = item.find('title').text
            entry_data['description'] = item.find('summary').text
            entry_data['author'] = item.find('author').text
            entry_data['pubDate'] = item.find('updated').text
            entry_data['link'] = item.find('link')['href']
            entry_data['minister'] = rss_title
            
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
            WriteItems(schema=schema).process_item(cleaned, table, 'executive')
            # recent = notify.get_recent_value(cleaned)
            # message = notify.message(cleaned, recent['title'])
            # notify.notification_push(topic,notification_title, str(message))
            
            logging.info(f'The total items needed are: {number_of_items}')
        else:
            logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()