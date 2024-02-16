import logging
import os
import xmltodict
from scrapeops_python_requests.scrapeops_requests import ScrapeOpsRequests
from database import ReadArticles, WriteItems
from rss import ParseXml
from bs4 import BeautifulSoup

def get_needed_items(link: str, table: str, link_variable_name: str, topic: str):
    title = table.title()
    topic = topic.title()
    scrapeops_logger =  ScrapeOpsRequests(
                    scrapeops_api_key=os.environ.get('SCRAPEOPS_API_KEY'), 
                    spider_name=f'{title}_Scraper',
                    job_name=f'{topic}_Job',
                    )
    try:
        requests = scrapeops_logger.RequestsWrapper()

        response = requests.get(link)
        soup = BeautifulSoup(response.content, features="xml")
        soup.find_all('item')
        data = ParseXml(soup.find_all('item')).getItems()
        print(data)
    except Exception as e:
            logging.critical("Critical: Issue data, requests, or scrapeops! : %s", str(e))
            
    """
    Make sure that the rss feed is in the correct format. If not then you will need to change the keys to match the rss feed
    """
    
    needed = []
    for item in data:
            scrapped = ReadArticles().check_item(table, item[link_variable_name])
            if scrapped == False:
                logging.info(f'New item found{item}')
                print(item['link'])
                scrapeops_logger.item_scraped(
                    response=response,
                    item=item,
                )
                needed.append(item)
    return needed