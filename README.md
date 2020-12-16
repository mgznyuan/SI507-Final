# SI 507 Final Project

# Find Your Next Makeup Product

## Overview

This program helps user to compare make-up products available at Sephora.com by using interactive command prompt. The user is able to choose the product types, two products from the top 60 (or less, depending on the availability of each type) best-selling products. The program will also display other products of the same type and same brand. The user could further choose products to shop and the program will open webpages of selected products automatically.  

#### Project demo available at (accessable to UM accounts):
https://drive.google.com/file/d/1SsqQ6yFKDqGCN7_e-tIGQ5qgBb4o7HcK/view?usp=sharing

## Packages required
+ Beautifulsoup (bs4)
+ requests
+ sqlite3
+ time
+ selenium (webdriver, Keys)
+ webbrowser
+ re

### A chromedriver (v86) is used to enable selenium, to download one on your own terminal:
https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_win32.zip
    
Remeber to change the `chromepath' to your local chromdriver location in main section if you would like to run the code locally

## Data source
 
The entire proejct is scraping HTML data from：https://www.sephora.com/


## Options provided with command line prompt

### Choice 1: Enter a number representing a top-category of makeup products:
            1.Face
            2.Eye
            3.Lip
            4.Cheek
            5.Brushes & Applicators
            6.Accessories
            Or "exit"
User could choose from one of the top categories (note: for this project, I only included the 6 top categories. There are a few others such as Best-Selling which potentially have overlap with the existing data  and were not chosen) or type in exit to exit the program


### Choice 2: Enter an ID for sub-category that you are interested in, or "back", or "exit"
 
The first step would print a list of sub-category with id. User could choose an id or choose to return last step or exit. 


### Choice 3: Would you like to choose two products to "compare", or "back", or "exit"
 
The former step would print at most 60 best-selling products under the category. The user can choose to compare 2 products by typing in "compare" , back to last step, or exit. If 2 identical ids are provided, or invalid values are invalid, it will trigger an error message and back to the current query. 

### Choice 4: Enter a product id to shop the product, or "back" or "exit"

The user will be asked to provide an id of the product displayed. And the program will open a webpage. The user could also choose exit to terminate the program or back to the last step. 

User can go back to the former step at any point when "back" option is provided.

## Database

The program will create a databse of 4 tables. They are: 
+ Categories: corresponding to the first step, this table includes a unique category id, top-category and sub-category of makeup products.
+ Top_products: the top 60 ranked products for certain category. This table includes a unique product_id, the full name of the product (name with brand name), and the URL of the product.
+ Products: information from individual product page. This table include basic information (name, brand, etc.) and category id, product id. 
+ Brands: corresponding to the last step. This table include brand name and url for searching the brand
The database includes all the The foreign keys for my database are category id from Categories table, and product_id from Top_products table, brand_id from the Brands table. Since one brand includes multiple categories, Brands and Categories are two tables that stands isolate from each other. Product table has keys to all other tables



