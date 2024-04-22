import logging
from bs4 import BeautifulSoup
from scrapeops_python_requests.scrapeops_requests import ScrapeOpsRequests
import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
                    # level=logging.INFO,filename=f"/var/log/cron.log",
                    level=logging.INFO,filename=f"log/cronjob.log", 
                    format='%(asctime)s - %(message)s', 
                    filemode='a')



class Response:

    def __init__(self, title, topic, link, link_variable_name, item_name):
        self.title = title
        self.topic = topic
        self.link = link
        self.link_variable_name = link_variable_name
        self.item_name = item_name
        self.scrapeops_logger =  ScrapeOpsRequests(
                        scrapeops_api_key=os.environ.get('SCRAPEOPS_API_KEY'), 
                        spider_name=f'{title}_Scraper',
                        job_name=f'{topic}_Job',
                        )
    
    def request_content(self, proxies=None, headers=None):  
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=headers)
        return response
    
    def get_soup(self, format, proxies=None, headers=None):
        
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=headers)
        soup = BeautifulSoup(response.content, features=format)
        xml_string = soup.find_all(self.item_name)
        return xml_string, response
    
    def log_item(self, item, response):
        logging.info(f'New item found{item}')
        self.scrapeops_logger.item_scraped(
                response=response,
                item=item,

        )
        return item
    
class Proxy:
    def __init__(self):
        self.username = os.environ.get('SMART_PROXY_USERNAME')
        self.passwrd = os.environ.get('SMART_PROXY_PASSWORD')

    def get_proxy(self):
        proxy = f"http://{self.username}:{self.passwrd}@gate.smartproxy.com:7000"
        return proxy
