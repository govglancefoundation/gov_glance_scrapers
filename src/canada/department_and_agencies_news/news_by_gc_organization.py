# from process import clean_items
# from database import WriteItems, ReadArticles
# from response import Response
# from notification import SendNotification
# import logging
# import xml.etree.ElementTree as ET
# from bs4 import BeautifulSoup

# def main():
#     urls = [
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadianaccessibilitystandardsdevelopmentorganization&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Accessibility%20Standards%20Canada",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=agricultureagrifood&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Agriculture%20and%20Agri-Food%20Canada",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=atlanticcanadaopportunities&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-0-23&pick=50&format=atom&atomtitle=Atlantic%20Canada%20Opportunities%20Agency",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadaborderservicesagency&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canada%20Border%20Services%20Agency",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=economicdevelopmentquebecregions&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canada%20Economic%20Development%20for%20Quebec%20Regions",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadainfrastructurebank&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Canada%20Infrastructure%20Bank",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=researchchairs&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Canada%20Research%20Chairs",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadaresearchcoordinatingcommittee&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-10-25&pick=100&format=atom&atomtitle=Canada%20Research%20Coordinating%20Committee",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=revenueagency&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canada%20Revenue%20Agency",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadiancentreforoccupationalhealthandsafety&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Centre%20for%20Occupational%20Health%20and%20Safety",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadiancoastguard&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Coast%20Guard",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=foodinspectionagency&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Food%20Inspection%20Agency",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=graincommission&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Grain%20Commission",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadianheritage&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Heritage",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=instituteshealthresearch&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Institutes%20of%20Health%20Research",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=intellectualpropertyoffice&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Intellectual%20Property%20Office",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadianinternationaltradetribunal&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20International%20Trade%20Tribunal",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadiannortherneconomicdevelopmentagency&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Northern%20Economic%20Development%20Agency",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadiannuclearsafetycommission&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Nuclear%20Safety%20Commission",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadianradiotelevisionandtelecommunicationscommission&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Radio-television%20and%20Telecommunications%20Commission",
#         "https://api.io.canada.ca/io-server/gc/news/en/v2?dept=canadiansecurityintelligenceservice&sort=publishedDate&orderBy=desc&publishedDate%3E=2021-07-23&pick=50&format=atom&atomtitle=Canadian%20Security%20Intelligence%20Service",

#         ]
#     schema = 'canada'
#     topic = 'Provinces and Territories News'
#     link_variable_name = 'link'
#     notification_title = 'Dept. of Defense Updates'
#     item_name = 'item'
#     format = 'xml'
#     #notify = SendNotification()


    

    
#     for url in urls:
#         data = []
#         resp = Response('news_by_gc_organization', topic, url, link_variable_name, item_name)
#         response = resp.request_content()
#         xml_string = BeautifulSoup(response.content, 'xml')
#         table = xml_string.find('title').text
#         print(table)
#         """
#         Edit the XML based on your needs
#         """
#         for item in xml_string.find_all('entry')[:1]:
#             entry_data = {}
#             # Make sure to look for all the tags in content
#             tags = item.find_all()
#             entry_data['category'] = item.find('category')['term'].title()
#             entry_data['title'] = item.find('title').text
#             entry_data['description'] = item.find('summary').text
#             entry_data['author'] = item.find('author').text
#             entry_data['pubDate'] = item.find('updated').text
#             entry_data['link'] = item.find('link')['href']
#             data.append(entry_data)


#         items = []
#         print(data)
#         for item in data:
#             scrapped = ReadArticles(schema=schema).check_item(table, item[link_variable_name])
#             if scrapped == False:
#                 item = resp.log_item(item, response)
#                 items.append(item)

#         if len(items) > 0:
#             number_of_items = len(items)
#             print(number_of_items)
#             cleaned = clean_items(items)
#             print(cleaned)
#             WriteItems(schema=schema).process_item(cleaned, table, 'executive')
#             # recent = notify.get_recent_value(cleaned)
#             # message = notify.message(cleaned, recent['title'])
#             # notify.notification_push(topic,notification_title, str(message))
            
#             logging.info(f'The total items needed are: {number_of_items}')
#         else:
#             logging.info(f'No new items found for {table.title()}')



# if __name__ == '__main__':
#     main()