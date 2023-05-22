# Ensure that you have the 'selenium','selenium-wire' package installed. If not, you can install it using the following command:
# pip install selenium
# pip install selenium-wire

# python --version= Python 3.8.10
# run command = python3 bigbasket.py

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from seleniumwire.utils import decode


import json
import time
import csv

class Scrapper:
    def __init__(self):
        """
        Initializes the Scrapper class with default values.
        """
        self.driver = self.initialize_driver()
        self.city = None
        self.categories = {}
        self.products = []


    def initialize_driver(self):
        """
        Initializes the Chrome WebDriver.
        
        Returns:
            WebDriver: The initialized Chrome WebDriver.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def  scrapCategory(self):
        """
        Scrapes the categories from the BigBasket website.
        """
        # Navigate to the BigBasket website
        self.driver.get("https://www.bigbasket.com/")

        # Wait for the page to fully load
        time.sleep(10)

        # Iterate over the requests made by the driver
        for request in self.driver.requests:
            if request.url.startswith("https://www.bigbasket.com/auth/get_page_data/"):
                # Extract the city information from the response
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                my_json = body.decode('utf8')
                my_json = json.loads(my_json)
                self.city = my_json['current_city']['name']

            elif request.url.startswith("https://www.bigbasket.com/auth/get_menu/"):
                # Extract the category information from the response
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                my_json = body.decode('utf8')
                my_json = json.loads(my_json)
                category_data = my_json["topcats"][:min(len(my_json["topcats"]), 5)]
                self.extractCategoryInfo(category_data)


    def extractCategoryInfo(self, jsonData):
        """
        Extracts the category information from the provided JSON data.

        Args:
            jsonData (dict): The JSON data containing category information.
        """
        for entry in jsonData:
            subcategory = []
            for subEntry in entry['sub_cats'][0]:
                subcategory.append(subEntry['sub_category'])
            category = entry['top_category']['name']
            self.categories[category] = subcategory


    def scrapProduct(self):
        """
        Scrapes the products for each category and subcategory.
        """
        for category in self.categories:
            for sub_cat in self.categories[category]:
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                driver = webdriver.Chrome(options=chrome_options)
                driver.get("https://www.bigbasket.com" + sub_cat[2])
                time.sleep(10)
                for request in driver.requests:
                    if request.url.startswith("https://www.bigbasket.com/custompage/sysgenpd/"):
                        body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                        my_json = body.decode('utf8')
                        my_json = json.loads(my_json)
                        products = my_json['tab_info'][0]['product_info']['products']
                        self.extractProductInfo(products[:min(len(products), 10)])


    def extractProductInfo(self,products):
        """
        Extracts the product information from the provided JSON data.

        Args:
            products (list): The list of products in JSON format.
        """
        for product in products:
            temp={}
            temp["City"]=self.city
            temp["Super Category (P0)"]=product.get("tlc_n","-")
            temp["Category (P1)"]=product.get("tlc_s","-")
            temp["Sub Category (P2)"]=product.get("llc_n","-")
            temp["SKU ID"]=product.get("sku","-")
            temp["Image"]=product.get("p_img_url","-")
            temp["Brand"]=product.get("p_brand","-")
            temp["SKU Name"]=product.get("p_desc","-")
            temp["SKU Size"]=product.get("w","-")
            temp["MRP"]=product.get("mrp","-")
            temp["SP"]=product.get("base_price","-")
            temp["Link"]="https://www.bigbasket.com"+product.get("absolute_url","-")
            temp["Active?"]=product.get("active","-")
            temp["Out of Stock?"]=product.get("out_of_stock","-")
            self.products.append(temp)
        


    def exportProduct(self):

        """
        Exports the extracted product information to a CSV file.
        If there are no products, the method returns without writing the file.
        """

        if len(self.products) == 0:
            return
    
        fieldnames = self.products[0].keys()

        with open("Big-Basket-Data.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)


if __name__ == '__main__':
    scrapper=Scrapper()
    scrapper.scrapCategory()
    scrapper.scrapProduct()
    scrapper.exportProduct()


