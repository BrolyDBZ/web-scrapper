# Ensure that you have the 'selenium','selenium-wire' package installed. If not, you can install it using the following command:
# pip install selenium
# pip install selenium-wire

# python --version= Python 3.8.10
# run command = python3 grab.py

#Make sure that you have right acess to grab site or you can use VPN.

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire import webdriver
from seleniumwire.utils import decode

import json
import time
import csv

class Scrapper:
    def __init__(self) -> None:
        self.driver = self.initialize_driver()
        self.restaurant_data = []

    def initialize_driver(self):
        """
        Initializes the Chrome WebDriver with headless mode enabled.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # driver = webdriver.Chrome(options=chrome_options)
        driver = webdriver.Chrome()

        return driver

    def search_location(self, location):
        """
        Performs a search for the specified location on the Grab Food website.
        
        Args:
            location (str): The location to search for.
        """
        self.driver.get("https://food.grab.com/ph/en/")
        time.sleep(10)

        # Find the location input field, clear it, and enter the desired location
        elem = self.driver.find_element(By.ID, 'location-input')
        elem.clear()
        elem.send_keys(location)
        elem.send_keys(Keys.RETURN)

        # Click the search button
        search_button = self.driver.find_element(By.XPATH, '//*[@id="page-content"]/div[3]/div/button')
        search_button.click()
        time.sleep(5)

    def scrapRestaurantData(self):
        """
        Scrapes restaurant data from the network requests made by the web page.
        """
        for request in self.driver.requests:
            if request.url.startswith("https://portal.grab.com/foodweb/v2/search"):
                # Decode the response body and parse the JSON data
                body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                json_data = json.loads(body.decode('utf8'))

                # Extract restaurant information from the JSON data
                self.extractRestaurantInfo(json_data["searchResult"]["searchMerchants"])


    def extractRestaurantInfo(self, json_data):
        """
        Extracts relevant information from the JSON data of restaurants and stores it in a list.
        
        Args:
            json_data (list): JSON data containing restaurant information.
        """
        for entry in json_data:
            temp = {}
            temp["Restaurant Name"] = entry["address"]["name"]
            temp["Latitude"] = entry["latlng"]["latitude"]
            temp["Longitude"] = entry["latlng"]["longitude"]
            self.restaurant_data.append(temp)


    def load_all_restaurants(self):
        """
        Scrolls down the web page to load all restaurants dynamically.
        """
        while True:
            try:
                self.scroll_down()
                time.sleep(3)
            except:
                break


    def scroll_down(self):
        """
        Scrolls down the web page to load more content.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = self.driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            raise EOFError("End of Page.")

        last_height = new_height
    


    def exportRestaurantData(self):
        """
        Exports the scraped restaurant data to a CSV file.
        """
        if len(self.restaurant_data) == 0:
            return

        fieldnames = self.restaurant_data[0].keys()

        with open("Restaurant-Latitude&Longitude.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.restaurant_data)





if __name__=="__main__":

    location = "30th St corner 5th Ave., Bonifacio Global City, Fort Bonifacio, Taguig City, Metro Manila, 1634, National Capital Region (Ncr), Philippines"
    scrapper=Scrapper()
    scrapper.search_location(location)
    scrapper.load_all_restaurants()
    scrapper.scrapRestaurantData()
    scrapper.exportRestaurantData()

