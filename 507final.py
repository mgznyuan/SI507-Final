#################################
##### Name: Meixin Yuan #########
##### Uniqname: mayyuan #########
##### Final Project #############
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3


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
    
    subcate: string
        the name of a sub-category under the fisrt category (e.g. 'foundation')
     
    rating: string
        the overall rating of the product (e.g. 4.5 stars)

    price: string 
        the price of the product (e.g. 42)
    
    size: string
        the size of the product (e.g. 0.6oz)

    review_number: string
        the number of reviews of a product (e.g. 3.5k)

    product_url: float
        the url of the product
        
    '''

    def __init__(self, name, brand, subcate, star_level, price, size, review_number, product_url):
        
        self.name=name
        self.brand=brand
        self.subcate=subcate
        self.star_level=star_level
        self.price = price
        self.size=size
        self.review_number=review_number
        self.product_url=product_url
    def info(self):
        return (self.name+" ("+ self.subcate + "): " +"\nBrand: " + str(self.brand)+ "\nRating: " + str(self.star_level)+ "," + str(self.review_number) + "\nPrice: " + str(self.price) +"\nSize: " + str(self.size))




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
                    key=sub['href']
                    sub_link='https://www.sephora.com'+ key
                    #print(id, cate, subcate, sub_link)
                    sub_key=key.replace('/shop','').strip()
                    list.append((id, cate, subcate, sub_link, sub_key))
                    id+=1
                    cur.execute(insert_category,[cate, subcate, sub_link])
    return list


############################################ Scrape a list of products based on specified categories ##########################################

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def find_driver(chromepath):
    ''' this code defines a web driver for scraping interactive pages 
    
    Parameters
    ----------
    chromepath: string
        a path to local chromdriver location
        to download a chromdriver, please visit:https://chromedriver.chromium.org/

    Returns
    -------
    driver: a baisc driver with several options: in incognito mode, headless, and ignore certificate errors
    '''
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
    subcate= cate_list[int(cate_id)-1][2]

    driver.get(url)
    time.sleep(10)

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
        products.append((product_id, product_name, product_url, subcate))
        print(str(product_id) +'. '+ product_name)
        product_id +=1
        cur.execute(Insert_60product,(product_name, product_url,))

    #close the chrome
    driver.close()
    return products


############################################ Scrape basic product information from the product page ##########################################

def get_product_detail(products, product_sid):

    ''' Parse product detail from the product page
    
    Parameters
    ----------
    products: list 
        list of produt urls and names
    product_sid: string
        the id of product that the user wants to investigate

    Returns: 
    -------
 
        the product basic information (brand, name, price, star_level, review_number, size, subcategory, and product url)
    '''
    product_url=products[int(product_sid)-1][2]
    subcate= products[int(product_sid)-1][3]

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
    if 'SIZE' in size: 
        size = size.replace('SIZE ', '').strip()
    else: size="N/A"

    product=Makeup(name, brand, subcate, star_level, price, size, review_number,product_url)
    return product


############################################ Scrape the same type of products for selected brands #########################################

def brand_dict():

    ''' Parse all the brands (name and query url) listed on Sepohra 
    
    Parameters
    ----------
    None

    Returns
    -------
        brand_dict: a dictionary of brands {brand name : query url of a brand}
    '''

    brand_dict={}
    base_brand="https://www.sephora.com/brands-list"
    response=make_request_with_cache(base_brand)
    soup= BeautifulSoup(response, 'html.parser')
    brands= soup('a', 'css-xyl2uf e65zztl0')
    for b in brands:
        url= b['href']
        bs=b.text
        brand=bs.split('\xa0')[0]
        brand_url="https://www.sephora.com"+url
        brand_dict[brand]=brand_url
        cur.execute(Insert_brands,(brand, brand_url))
    return brand_dict

def find_brand_top(product_sid, products, cate_list, brand_dict):

    ''' Parse the (at most) 12 best-selling products of a brand
    
    Parameters
    ----------
    product_sid: integer
        the searchd id user inputs
    products: list
        a list of product name and url
    cate_list: list
        a list of all categories and the respective urls
    brand_dict: 
        a dictionary of brand and brand url

    Returns
    -------
        brand products: list 
            a list of tuples that include id, product name, product url, and sub-category of the product
        
    '''
    product=get_product_detail(products, product_sid)
    brand= product.brand
    subcate=product.subcate
    
    for i in cate_list:
        cate=i[2]
        if cate == subcate:
            sub_key= i[4]
    #print(sub_key)       
    brand_base_url=brand_dict[brand]
    brand_type_url = brand_base_url + sub_key
    #print(brand_type_url)
    response=make_request_with_cache(brand_type_url)
    soup= BeautifulSoup(response, 'html.parser')
    bps= soup('a', 'css-ix8km1')
    brand_products = []
    id=1
    for bp in bps:
        product_name= bp['aria-label']
        product_url= bp['href']
        product_url=product_url.split('grid:')[0].strip()
        product_url= 'https://www.sephora.com/'+product_url
        brand_products.append((id, product_name, product_url, subcate))
        #print(product_id , product_name , product_url)

        id +=1
        
    return brand_products


def find_brand_products(brand_products):
    ''' Parse the details of each product
    
    Parameters
    ----------

    products: list
        a list of product name and url
    cate_list: list
        a list of all categories and the respective urls
    brand_dict: 
        a dictionary of brand and brand url

    Returns
    -------
        brand products: list 
            a list of tuples that include id, product name, product url, and sub-category of the product
        
    '''
    brand_products_detail=[]
    id=1
    limit=len(brand_products)
    while id <= limit:
        product=get_product_detail(brand_products, id)
        brand_products_detail.append(product)
        id+=1
    return brand_products_detail

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
                        'product_id' INTEGER REFERENCES Top_products(product_id),
                        "brand_id" INTEGER REFERENCES Brands(brand_id)
                    );
                """
create_brands=""" 
                    CREATE TABLE IF NOT EXISTS "Brands" (
                        "brand_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        "brand_name" TEXT NOT NULL UNIQUE,
                        "brand_url" TEXT NOT NULL UNIQUE
                       
                    );
                """


Insert_brands="""
                    INSERT INTO Brands ('brand_name', 'brand_url') 
                    VALUES (?,?)
                    
                    """
      


insert_category="""
                    INSERT INTO Categories ('category', 'type','URL') 
                    VALUES (?,?,?)
                    
                    """
    

Insert_products=""" 
                    INSERT OR IGNORE INTO Products ('name','brand','price','star_level','review_number','size','sub_cate_id','product_id', 'brand_id')
                    VALUES  (?,?,?,?,?,?,?,?,?)
                    """

Insert_60product="""
                    INSERT OR IGNORE INTO Top_products ('full_name', 'url')
                    VALUES (?,?)         
                    """



   
def create_productdb(list):
    '''Insert the value to the table in database via sqlite
    
    Parameters
    ----------
    list:list
        a list of  product with detail information 

    Returns
    -------
    None
    '''

    for ls in list:
       
        brand=ls.brand
        name=ls.name
        price= float(re.findall('\d*\.?\d', ls.price)[0])
        star_level= float(re.findall('\d*\.?\d', ls.star_level)[0])
        review_number =ls.review_number
        subcate=ls.subcate
        size=ls.size
        product_url =ls.product_url
        
        sub_cate_id=cur.execute(f"SELECT sub_cate_id FROM Categories WHERE type='{subcate}'").fetchall()[0][0]
        try:
            product_id=cur.execute(f"SELECT product_id FROM Top_products WHERE url='{product_url}'").fetchall()[0][0]
        except:
            product_id = "N/A"
        brand_id=cur.execute(f"SELECT brand_id FROM Brands WHERE brand_name='{brand}'").fetchall()[0][0]

        cur.execute(Insert_products,(name,brand,price,star_level,review_number,size,sub_cate_id,product_id, brand_id))

    conn.commit()



############################################################ Interactive Command Lines ############################################################

import webbrowser
import os

#########################################
############### choice 1 ################
#########################################


def enter_category():

    ''' Request user input for a category that she/he wants to search
    automatically goes to the next step
    
    Parameters
    ----------
    None

    Returns
    -------
    id_list: list
        a list of subcategory ids 
    '''


    print("#-------------------------  Select a category ------------------------- #")
    while True:
        top_dict={ '1':'face',"2":"eye","3":'lip', "4":'cheek', "5":'brushes & applicators',"6":'accessories'}
        topcate= input('Enter a number representing a top-category of makeup products: \n1. Face \n2. Eye \n3. Lip \n4. Cheek \n5. Brushes & Applicators \n6. Accessories \nOr "exit" \n')
        if topcate.lower()=='exit':
            os._exit(1)

        elif topcate in ['1', '2', '3', '4', '5', '6'] :
            topcate=top_dict[topcate]
            print("Under "+ topcate+" category, you can choose from:")
            id_list=[]
            for i in cate_list:
                if topcate==i[1]:
                    print(str(i[0])+". "+ i[2])
                    id_list.append(str(i[0]))
            products=enter_sub_cate(id_list) # call the next step function
                    
        else:
            print('Please provide a valid input')

#########################################
############### choice 2 ################
#########################################

def enter_sub_cate(id_list):

    ''' Request user input for a subcategory that she/he wants to search, validate the input, allows user to go back to the last step or exit
      and automatically goes to next choice step

    Parameters
    ----------
    id_list: list
        a list of subcategory ids 

    Returns
    -------
    products: list
        a list of product name and url 
    '''

    while True:
        cate_id=input("Enter an ID for sub-category that you are interested in, or \"back\", or \"exit\": \n")
        if cate_id.lower()== 'back': # call the last step function
            id_list=enter_category()
        elif cate_id.lower() =='exit':
            os._exit(1)
        elif str(cate_id) in id_list:
            products= find_60_products(int(cate_id))
            choose_two_products(products, id_list) # call the next step function
        else:
            print('Please provide a valid input')

#########################################
############### choice 3 ################
#########################################


def choose_two_products(products, id_list):

    ''' Request user input for two products that the user wants to compare, validate the input, allows user to go back to the last step or exit
     and automatically goes to next choice step
    
    Parameters
    ----------
    products: list
        a list of product name and url

    id_list: list
        a list of subcategory ids     

    Returns
    -------
    id1, id2: integer
         two valid search integers represeting the id of products
    
    '''

    print("#------------------------- Choose products to compare -------------------------#")
    product_ids=[]
    for i in products:
        product_ids.append(str(i[0]))

    while True:
        query=input("Would you like to choose two products to \"compare\", or \"back\", or \"exit\": \n")
        if query.lower() == 'back':
            products=enter_sub_cate(id_list) # call the last step function
        elif query.lower()== 'exit':
            os._exit(1)
        elif query.lower()=="compare":
            id1=input("Choose the first product id:")
            id2=input('Choose the second product id:')
            if str(id1) in product_ids and str(id2) in product_ids and str(id1) != str(id2):
               brand1, brand2, list = print_product_details(products, id1, id2)
               brand_products_url, list =brand_products(id1, id2, products, cate_list, brand_dict, brand1, brand2, list)
               create_productdb(list)
               shop_url(brand_products_url, products, cate_list, brand_dict, id_list)  # call the next step function
            else:  print('Please provide a valid input')
        else:
             print('Please provide a valid input')

    
def print_product_details(products, id1, id2):

    '''print product details 
    
    Parameters
    ----------
    products: list
        a list of product name and url

    id1, id2: integer
         two valid search integers represeting the id of products

    Returns
    -------
    brand1, brand2: string
        name of the brands of the selected 2 
    list: list
        list of makeup product objects

    '''
    
    list=[]
    product1=get_product_detail(products, id1)
    product2=get_product_detail(products, id2)
    print("#------------------------- Your selected products are: -------------------------#")
    print(product1.info())
    print('+-------------------------------------------------------------------------------+')
    print(product2.info())
    brand1=product1.brand
    brand2=product2.brand
    list.append(product1)
    list.append(product2)
    return brand1, brand2, list

def brand_products(id1, id2, products, cate_list, brand_dict, brand1, brand2, list):   

    '''print procut details 
    
    Parameters
    ----------
    id1, id2: integer
         two valid search integers represeting the id of products

    products: list
        a list of product name and url

    products: list
        a list of product name and url

    cate_list: list
        a list of all categories and the respective urls

    brand_dict: dictionary
        a dictionary of brand and brand url

    brand1, brand2: string
        name of the brands of the selected 2 

    list: list
        list of makeup product objects

    Returns
    -------
    brand_products_url: dictionary
         a dictionary of product id and url of the product

    list: list
        a concatenate list of products that combines the two search products and all related products
    

    '''
    # acquire related products for both brands

    brand_products1= find_brand_top(id1, products, cate_list, brand_dict)
    brand_products2= find_brand_top(id2, products, cate_list, brand_dict)
    brand_products_l1=find_brand_products(brand_products1)
    brand_products_l2=find_brand_products(brand_products2)
    list=list + brand_products_l1 + brand_products_l2
        
    print("#------------------------- The selected brand has the following products under this category -------------------------#")
    print("##" + brand1 + "##")
    n=1
    
    brand_products_url = {}
    for item in brand_products_l1:
        print(str(n)+ ". " + item.info())
        brand_products_url[n]= item.product_url
        n+=1
    print("+--------------------------------------------------+")
    print("##" + brand2 + "##")
    for item in brand_products_l2:
        print(str(n)+ ". " + item.info())
        brand_products_url[n]= item.product_url
        n+=1
        brand_products_url[n]= item.product_url

    return brand_products_url, list

#########################################
############### choice 4 ################
#########################################

def shop_url(brand_products_url, products, cate_list, brand_dict, id_list):

    '''open a product webpage at the user's request, allows user to go back to the last step
     and automatically goes to next choice step

    Parameters
    ----------
    products: list
        a list of product name and url

    brand_products_url: dictionary
         a dictionary of product id and url of the product

    cate_list: list
        a list of all categories and the respective urls

    brand_dict: dictionary
        a dictionary of brand and brand url

    id_list: list
        a list of selected subcategory ids

    Returns
    -------

    '''
    brand_urls=[]
    for key in brand_products_url.items():
        brand_urls.append(str(key[0]))

    while True: 
        shop_id=input('Enter a product id to shop the product, or \"back\" or \"exit\" :\n')
        if shop_id.lower()=='exit':
            os._exit(1)
        if shop_id.lower() =='back':
            id1, id2=choose_two_products(products, id_list) # call the last step

        elif str(shop_id) in brand_urls:
            url=brand_products_url[int(shop_id)]
            print('Launching\n', url,'\nin web browser...') 
            webbrowser.open(url) #browse the url
        else:
            print('Please provide a valid input')

############################################ Executing #######################################################

if __name__ == '__main__':

    print("#-------------------------  Find your next make up product from Sephora ------------------------- #")
    print("#-------------------------   Meixin Yuna SI507 Final Project 2020 Fall  ------------------------- #")
    print("#-------------------------        Loading....Creating a database        ------------------------- #")

    chromepath="C:/Users/17349/Downloads/chromedriver"
    cur.execute("DROP TABLE IF EXISTS Categories")
    cur.execute("DROP TABLE IF EXISTS Top_products")
    cur.execute("DROP TABLE IF EXISTS Products")
    cur.execute("DROP TABLE IF EXISTS Brands")
    cur.execute(create_categroy)
    cur.execute(create_60product)
    cur.execute(create_brands)
    cur.execute(create_products)


    brand_dict=brand_dict() # get a dictionaryy of brands
    cate_list = build_subcate_list() # get a list of top and sub-categories

    while True:
        id_list=enter_category()
        conn.close()
    
        