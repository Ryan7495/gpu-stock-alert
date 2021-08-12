import warnings
warnings.filterwarnings("ignore")

import os, sys
import pandas as pd
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


keywords = 'gpu'
CANADA_COMPUTERS_GPU_PAGE = f'https://www.canadacomputers.com/search/results_details.php?language=en&keywords={keywords}&cpath=43'
#CANADA_COMPUTERS_GPU_PAGE = 'https://www.canadacomputers.com/search/results_details.php?language=en&keywords=cpu'

def main():

    check()
    pass


def check():
    driver = headless_chrome_driver()
    try:
        links = get_product_links(driver, CANADA_COMPUTERS_GPU_PAGE)

        data = product_info(driver, links)

        driver.close()

    except KeyboardInterrupt as e:
        driver.close()

    except WebDriverException as e:
        driver.close()


def product_info(driver, links):
    columns = ['time', 'name', 'cost', 'stock', 'link']
    #df = pd.DataFrame([], columns=columns)
    df = pd.read_csv('availability.csv', index_col=0)

    for link in links:
        try:
            driver.get(link)

            data = {'time':datetime.utcnow(), 'name':None, 'cost':None, 'stock':None, 'link':link}

            for element in driver.find_elements_by_tag_name('h1'):
                if element.get_attribute('class') is not None and element.get_attribute('class') == 'h3 mb-0':
                    data['name'] = element.find_element_by_tag_name('strong').text
                    break
            
            if '3060' in data['name'] or \
                '3070' in data['name'] or \
                '3070' in data['name']:
                pass
            else:
                continue

            for element in driver.find_elements_by_tag_name('span'):
                if element.get_attribute('class') is not None and element.get_attribute('class') == 'h2-big':
                    data['cost'] = element.find_element_by_tag_name('strong').text
                    break
            
            for element in driver.find_elements_by_tag_name('p'):
                if element.get_attribute('class') is not None and \
                    element.get_attribute('id') is not None and \
                    element.get_attribute('class') == 'font-weight-bold stocklevel mb-0' and \
                    element.get_attribute('id') == 'storeinfo':

                    if 'IN STOCK' in str(element.text):
                        data['stock'] = True
                    elif 'OUT OF STOCK' in str(element.text):
                        data['stock'] = False
                    else:
                        data['stock'] = False
                    break

            if data['stock']:
                df = df.append(data, ignore_index=True)

        except Exception as e:
            print(link, e)
            pass
        
        df.to_csv('availability.csv')

    return df


def get_product_links(driver, link):
    driver.get(link)

    product_links = []
    
    for element in driver.find_elements_by_tag_name('a'):
        if element.get_attribute('href') is not None and 'product_info' in element.get_attribute('href'):
            product_links.append(element.get_attribute('href'))

    return set(product_links)


def headless_chrome_driver():
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    return webdriver.Chrome(chrome_options=chrome_options)


if __name__ == '__main__':
    main()