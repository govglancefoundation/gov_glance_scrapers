from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
from bs4 import BeautifulSoup
import logging
import xml.etree.ElementTree as ET
import json
from dotenv import load_dotenv
load_dotenv()



def main():

    url = 'https://www.governor.ny.gov/views/ajax?page=2&_wrapper_format=drupal_ajax&view_name=filter_frame&view_display_id=news&view_args=&view_path=%2Fnode%2F103706&view_base_path=&view_dom_id=da805a9c6ad82f79f432dfe9c43fbbbcf9524501543fe3af0055109cc117d9fc&pager_element=0&page=0&_drupal_ajax=1&ajax_page_state%5Btheme%5D=nygov_theme&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=better_exposed_filters%2Fauto_submit%2Cbetter_exposed_filters%2Fdatepickers%2Cbetter_exposed_filters%2Fgeneral%2Cbetter_exposed_filters%2Fselect_all_none%2Cclassy%2Fbase%2Cclassy%2Fmessages%2Ccore%2Fnormalize%2Cgoogle_analytics%2Fgoogle_analytics%2Cnygov_core%2Fnygov-core%2Cnygov_theme%2Fglobal-styling%2Cnygov_theme%2Fnygov-textfill%2Cnygov_theme%2Fresponsive-table%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module'         # url
    table = 'New York'   
    schema = 'united_states_of_america'                                                                 # State name
    topic = 'state'                                                 # The topic of the scraper
    link_variable_name = 'link'                                      # Whatever the link variable name might be
    notification_title = 'New York State Updates'                    # Notification title
    item_name = 'data'                                           # Make sure that you using the right item tag name
    format = 'html.parser'
    # notify = SendNotification()


    resp = Response(table, topic, url, link_variable_name, item_name)
    response = resp.request_content()

    payload = json.loads(response.content)[2]
    soup = BeautifulSoup(payload['data'], features='html.parser')
    content = soup.find_all('article')
    # content = table_content.find_all('article',{'class':'news-item'})

    data = []

    """
    Edit the XML based on your needs
    """
    for item in content[:15]: 
        print(item)
        entry_data = {}

        if item.find('a') is not None:
            entry_data['link'] = 'https://www.governor.ny.gov/' + item.find('a')['href']
            entry_data['title'] = item.find('a').text
        if item.find('div', {'class': 'content-dates'}) is not None:
            entry_data['pubDate'] = item.find('div', {'class': 'content-dates'}).text.replace(' | ', ' ')
        if item.find('div', {'class': 'content-description'}) is not None:
            entry_data['description'] = item.find('div', {'class': 'content-description'}).text
        if item.find('img') is not None:
            entry_data['img'] = 'https://www.governor.ny.gov/' + item.find('img')['src']
        data.append(entry_data)

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
    # #     # recent = notify.get_recent_value(cleaned)
    # #     # message = notify.message(cleaned, recent['title'])
    # #     # notify.notification_push(topic,notification_title, str(message))
        
    #     logging.info(f'The total items needed for {table.title()} are: {number_of_items}')
    # else:
    #     logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()