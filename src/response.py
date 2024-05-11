import logging
from bs4 import BeautifulSoup
from scrapeops_python_requests.scrapeops_requests import ScrapeOpsRequests
import os
import json
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
    
    def request_content(self, proxies=None, headers=None, verify=None):  
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=headers, verify=verify)
        return response
    
    def request_content_post(self, proxies=None, headers=None, data=None, verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.post(self.link, proxies=proxies, headers=headers, json=data, verify=verify)
        return response
    
    def request_content_json(self, proxies=None, headers=None, verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=headers, verify=verify)
        return json.loads(response.content)[self.item_name], response
    
    def get_soup(self, format, proxies=None, headers=None,verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=headers, verify=verify)
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
    
    def get_mexico_proxy(self):
        proxy = f"https://{self.username}:{self.passwrd}@mx.smartproxy.com:20001"
        return proxy
