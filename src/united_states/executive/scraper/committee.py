from process import clean_items
from database import WriteItems, ReadArticles
from response import Response
from notification import SendNotification
import logging
import xml.etree.ElementTree as ET


def main():
    url = "https://docs.house.gov/Committee/RSS.ashx?Code=IG00"
    table = 'permanent_select_committee_on_intelligence'
    schema = 'united_states_of_america'
    topic = 'foreignAffairs'
    link_variable_name = 'link'
    notification_title = 'Committee on Intelligence Updates'
    item_name = 'item'
    format = 'xml'
    #notify = SendNotification()
    
    resp = Response(table, topic, url, link_variable_name, item_name)
    xml_string, response = resp.get_soup(format)

    data = []

    """
    Edit the XML based on your needs
    """
    for item in xml_string:
        print(item)
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
        logging.info(f"Checking {table} table in the database for results")
        scrapped = ReadArticles(schema=schema).check_item(table, item[link_variable_name])
        if scrapped == False:
            item = resp.log_item(item, response)
            items.append(item)

    if len(items) > 0:
        number_of_items = len(items)
        cleaned = clean_items(items)
        print(cleaned)
        WriteItems(schema=schema).process_item(cleaned, table, topic)
        # recent = notify.get_recent_value(cleaned)
        # message = notify.message(cleaned, recent['title'])
        # notify.notification_push(topic,notification_title, str(message))
        
        logging.info(f'The total items needed are: {number_of_items}')
    else:
        logging.info(f'No new items found for {table.title()}')



if __name__ == '__main__':
    main()