#################################
##### Name: Meixin Yuan #########
##### Uniqname: mayyuan #########
##### Final Project #############
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import re

CACHE_FILENAME='cache_file.txt'

############################# Construct an object of makeup product ########################################
class Makeup:
    '''a sephora makeup category site
    Instance Attributes
    -------------------
    name: string
        name of the product (e.g. "Luminous Silk Perfect Glow Flawless Oil-Free Foundation")

    brand: string
        brand of the makeup product (e.g. "Amarni Beauty")

    category: string
        the category of the makeup product on Sephora site  (e.g. 'Face')
    
    subcate: string
        the name of a sub-category under the fisrt category (e.g. 'Foundation')
     
    rating: float
        the overall rating of the product (e.g. 4.5)

    price: float
        the price of the product (e.g. 42)
    
    size: float
        the size of the product (e.g. 0.6oz)

        
    '''

    def __init__(self, name, brand, category, subcate, star_level, price, size, review_number):
        
        self.name=name
        self.category=category
        self.subcate=subcate
        self.star_level=star_level
        self.price = price
        self.size=size
    def info(self):
        return (self.name+" ("+self.category+ ","+ self.subcate + "): " + "n\Rating: " + str(self.rating)+  "n\Price: " + str(self.price) +"n\Size: " + str(self.size))




########################################################## Build cache ##########################################################

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def make_request_with_cache(url):
    '''Check the cache for a saved result for this state. 
    If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    If the result is in your cache, print "Using Cache"
    If request a new result using get_sites_for_state(state_url), print "Fetching"

    Parameters
    ----------
    url: string
        the input url
    
    Returns
    -------
    result: str or dict
        the data returned from making the request in the form of 
        a string ro dictionary
    '''
    dict=open_cache()
    unique_key=url
    if unique_key not in dict:
        print("Fetching")
        response=requests.get(url)
        result=response.text
        dict[unique_key]=result     
        save_cache(dict)
    else:
        print("Using Cache")
        result=dict[unique_key]
    return result



################################################ Scrape a list of subcategory urls #####################################################

def build_subcate_list():
    ''' Make a dictionary that maps to subactegory page url from "https://www.sephora.com/"

    Parameters
    ----------
    None

    Returns
    -------
    list
        a list of product top and sub-categoris and their respective link
        e.g. [(1,face,foundation,https://www.sephora.com/shop/foundation-makeup)]
    '''
    baseurl= 'https://www.sephora.com/shop/makeup-cosmetics'
    #response=make_request_with_cache(baseurl)
    response=make_request_with_cache(baseurl)
    soup_main= BeautifulSoup(response, 'html.parser')
    main= soup_main.find_all('nav','css-1kfiypj e65zztl0')
    list=[]
    id=1
    for item in main:
        sections=item.find_all('div')
        for section in sections:
            sec=section.find_all('a',attrs={'data-at':"top_level_category"})
            subs=section.find_all('a',attrs={'data-at':"nth_level_category"})

            if sec:
                for s in sec:
                    cate=s.text.strip().lower()
                    cate_link=s['href']
                    cate_link='https://www.sephora.com'+ cate_link
            if subs:
                for sub in subs:
                    subcate=sub.text.strip().lower()
                    sub_link=sub['href']
                    sub_link='https://www.sephora.com'+ sub_link
                    print(id, cate, subcate, sub_link)
                    list.append((id, cate, subcate, sub_link))
                    id+=1
                    cur.execute(insert_category,[cate, subcate, sub_link])
    return list


############################################ Scrape a list of products based on specified categories ##########################################

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def find_driver(chromepath):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(chromepath, chrome_options=options)
    print('Driver defined')
    return driver


def scrollDown(driver, n_scroll):
    ''' credit for this code: https://www.hackerearth.com/fr/practice/notes/praveen97uma/crawling-a-website-that-loads-content-using-javascript-with-selenium-webdriver-in-python/
    this code creates a function that gets the browser to scroll down
    
    Parameters
    ----------
    driver: 
        the web browser driver
    n_scroll: integer
        the time of scrolling

    Returns
    -------
    driver: a web browser driver that enables scrolling down 
    '''
    body = driver.find_element_by_tag_name("body")
    while n_scroll >= 0:
        body.send_keys(Keys.PAGE_DOWN)
        n_scroll -= 1
    return driver


def find_60_products(cate_id):
    driver=find_driver(chromepath)

    url=cate_list[int(cate_id)-1][3]
    sub_cate= cate_list[int(cate_id)-1][2]

    driver.get(url)
    time.sleep(20)

    # to simplify the process, here I only scroll the first page of the first 60 products
    # sorted by best selling rank 

    browser = scrollDown(driver, 20) #scroll down the page
    time.sleep(10) #give it time to load
    slug = browser.find_elements_by_class_name('css-ix8km1') #look for the urls of products

    # extract the product name and product url for the products showing on the first page 
    products = []
    product_id=1
    for a in slug:
        product_name= a.get_attribute('aria-label')
        product_url= a.get_attribute('href')
        products.append((product_id, product_name, product_url, sub_cate))
        print(product_id , product_name , product_url, sub_cate)
        product_id +=1
        cur.execute(Insert_60product,(product_name, product_url,))

    #close the chrome
    driver.close()
    return products


############################################ Scrape basic product information from the product page ##########################################

def get_product_detail(products, product_id):

    ''' Parse product detail from the product page
    
    Parameters
    ----------
    products: list 
        list of produt urls and names
    product_id:
        the id of product that the user wants to investigate

    Returns: 
    -------
 
        the product basic information (brand, name, price, star_level, review_number, size, sub_category, and product url)
    '''
    product_url=products[int(product_id)-1][2]
    sub_cate= products[int(product_id)-1][3]

    response=make_request_with_cache(product_url)
    soup= BeautifulSoup(response, 'html.parser')
    nb= soup('h1', 'css-1wd4e6l e65zztl0')
    for n in nb:
        brand=n.find('span', 'css-57kn72').text
        name=n.find_all('span')[1].text
    pinfo= soup ('div', class_='css-1865ad6 e65zztl0')
    for p in pinfo:
        price=p.find('span').text

    sinfo=soup.find('div', 'css-jp4jy6')

    star_level= sinfo['aria-label']

    review_number=soup.find('span', 'css-2rg6q7').text

    size = soup.find('div', 'css-128n72s e65zztl0').text.split('•')[0] 
    return brand, name, price, star_level, review_number, size, sub_cate, product_url


############################################################ Create Database ############################################################


conn = sqlite3.connect('Sephora.sqlite')
cur = conn.cursor()


create_categroy=""" 
                CREATE TABLE IF NOT EXISTS "Categories" (
                    "sub_cate_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    "category" TEXT,
                    "type" TEXT NOT NULL ,
                    "URL" TEXT NOT NULL 
                    );
                """

create_60product=""" 
                    CREATE TABLE IF NOT EXISTS "Top_products" (
                        "product_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        'full_name' TEXT NOT NULL UNIQUE,
                        "url" TEXT NOT NULL UNIQUE
       
                    );
                """
create_products=""" 
                    CREATE TABLE IF NOT EXISTS "Products" (
                        "id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        "name" TEXT NOT NULL UNIQUE,
                        "brand" TEXT NOT NULL,
                        "price" NUMERIC NOT NULL,
                        "star_level" NUMERIC NOT NULL,
                        "review_number" TEXT,
                        "size" NUMERIC NOT NULL,
                        "sub_cate_id" INTEGER REFERENCES Categories(sub_cate_id),
                        'product_id' INTEGER REFERENCES Top_products(product_id)
                    );
                """

insert_category="""
                    INSERT INTO Categories ('category', 'type','URL') 
                    VALUES (?,?,?)
                    
                    """
    

Insert_products=""" 
                    INSERT INTO Products ('name','brand','price','star_level','review_number','size','sub_cate_id','product_id')
                    VALUES (?,?,?,?,?,?,?,?)
                    """

Insert_60product="""
                    INSERT INTO Top_products ('full_name', 'url')
                    VALUES (?,?)
                    """




   
def create_productdb(list):
    '''Insert the value to the table in database via sql
    
    Parameters
    ----------
    list:list
        a list of  product detail information 

    Returns
    -------
    None
    '''

    for ls in list:
       
        brand=ls[0]
        name=ls[1]
        price= float(re.findall('\d*\.?\d', ls[2])[0])
        star_level= float(re.findall('\d*\.?\d', ls[3])[0])
        review_number =ls[4]
        size= ls[5].replace('SIZE','').strip()
        sub_cate=ls[6]
        product_url =ls[7]
        
        sub_cate_id=cur.execute(f"SELECT sub_cate_id FROM Categories WHERE type='{sub_cate}'").fetchall()[0][0]
        product_id=cur.execute(f"SELECT product_id FROM Top_products WHERE url='{product_url}'").fetchall()[0][0]

        cur.execute(Insert_products,(name,brand,price,star_level,review_number,size,sub_cate_id,product_id))

    conn.commit()



############################################################ Project checkpoint ############################################################

chromepath="C:/Users/17349/Downloads/chromedriver"
cur.execute("DROP TABLE IF EXISTS Categories")
cur.execute("DROP TABLE IF EXISTS Top_products")
cur.execute("DROP TABLE IF EXISTS Products")
cur.execute(create_categroy)
cur.execute(create_60product)
cur.execute(create_products)

# get a list of products

cate_list = build_subcate_list()
cate_id=1
products=find_60_products(cate_id)
list =[]
i=1
while i < 21:
    item= get_product_detail(products, i)
    list.append(item)
    i+=1

create_productdb(list)

conn.close()