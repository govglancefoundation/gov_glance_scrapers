import logging
from bs4 import BeautifulSoup
import requests
from scrapeops_python_requests.scrapeops_requests import ScrapeOpsRequests
import os
import json
from lxml.html import fromstring
from dotenv import load_dotenv
from requests_html import HTMLSession
from fake_useragent import UserAgent
import itertools
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
        self.headers = RequestFakeUserAgentMiddleware().random_headers()
        self.scrapeops_logger =  ScrapeOpsRequests(
                        scrapeops_api_key=os.environ.get('SCRAPEOPS_API_KEY'), 
                        spider_name=f'{title}_Scraper',
                        job_name=f'{title}: {topic}_Job',
                        )
        logging.info(f'Initiated {title} scraper with headers: {self.headers}')
    
    def requests_(self, proxies=None, verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, verify=verify)

        return response
    def request_content(self, proxies=None, verify=None):  
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=self.headers, verify=verify)
        return response
    
    def request_render(self,tag_name= '',proxies=None, verify=None):
        session = self.scrapeops_logger.RequestsWrapper()
        session = HTMLSession()
        res = session.get(self.link, headers=self.headers, proxies=proxies, verify=verify) 
        res.html.render()
        return  res.html.find(tag_name), res
    
    def request_content_post(self, headers =None, proxies=None, data=None, verify=None):
        if headers:
            headers = headers
        else:
            headers= self.headers
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.post(self.link, proxies=proxies, headers=headers, json=data, verify=verify)
        return response
    
    def request_content_json(self, proxies=None, verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=self.headers, verify=verify)
        return json.loads(response.content)[self.item_name], response
    
    def get_soup(self, format, proxies=None,verify=None):
        requests = self.scrapeops_logger.RequestsWrapper()
        response = requests.get(self.link, proxies=proxies, headers=self.headers, verify=verify)
        soup = BeautifulSoup(response.content, features=format)
        xml_string = soup.find_all(self.item_name)
        return xml_string, response
    

    def log_item(self, item, response):
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

class FreeProxy:
    def __init__(self, title, topic):
        
        self.url = 'https://free-proxy-list.net/'
        self.scrapeops_logger =  ScrapeOpsRequests(
                        scrapeops_api_key=os.environ.get('SCRAPEOPS_API_KEY'), 
                        spider_name=f'{title}_Scraper',
                        job_name=f'{title}: {topic}_Job',
                        )

    def get_proxies(self):

        response = requests.get(self.url)   

        parser = fromstring(response.text)
        proxies = set()


        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):                            
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], 
                                i.xpath('.//td[2]/text()')[0]])                            
                proxies.add(proxy)
        return proxies
    
    def log_item(self, item, response):
        self.scrapeops_logger.item_scraped(
                response=response,
                item=item,

        )
        return item
    
    def use_free_proxies_request(self, link: str = ''):
        cookies = {
                '__uzmc': '916642282202',
                '__uzmd': '1715969571',
                'JSESSIONID': '355747E14B99DCF7395699B5235CC39D',
                'TS01889c2f': '01f6d3688aa55dc24be398f670dd01672352011a7ec37f15259e150f426315fe004e96e394e27a23992e944f44f61061107e496735c93bf4ce105b3c2303dd2d321d5e6d15791d0b56a9f138c01b209171ffac8bdf'
            }
        ips = self.get_proxies()
        if ips:
            proxy_pool = itertools.cycle(ips)
            for i in range(1, len(ips)):
                proxy = next(proxy_pool)
                try:
                    header = RequestFakeUserAgentMiddleware().random_headers()
                    resp = self.scrapeops_logger.RequestsWrapper()
                    resp = requests.get(link, proxies={"http": proxy, "https": proxy}, timeout=5, headers=header,cookies=cookies, verify=False)
                    print(resp.content)
                    soup = BeautifulSoup(resp.content, features="html.parser")
                    if resp.ok:                                    
                        print('Rotated IP %s succeed' % proxy)                                    
                        break
                except Exception as e:                                
                    print('Rotated IP %s failed (%s)' % (proxy, str(e)))
            return soup, resp

class RequestFakeUserAgentMiddleware:

    def __init__(self):
        self.rand_agent = UserAgent()

    def random_headers(self):
        ua = self.rand_agent.random
        
        headers = {
            'Content-Encoding': 'gzip',
            'Content-Type': 'text/xml',
            'Date': 'Fri, 17 May 2024 18:12:54 GMT',
            'Server-Timing': 'dtSInfo;desc="0", dtRpid;desc="-68555938"',
            'Vary': 'Accept-Encoding,User-Agent',
            'X-Frame-Options': 'SAMEORIGIN'
        }

        headers["User-Agent"] = str(ua)
        return headers