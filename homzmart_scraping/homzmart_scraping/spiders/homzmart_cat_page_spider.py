from dotenv import load_dotenv
# Load environment variables
load_dotenv()
import os
try:
    # For Airflow - Changing the current working directory to the data folder so that the script stores the output JSON file there
    os.chdir(os.getenv('DATA_FOLDER_PATH_AIRFLOW'))
except FileNotFoundError:
    # For local env - Changing the current working directory to the data folder so that the script stores the output JSON file there
    os.chdir(os.getenv('DATA_FOLDER_PATH_LOCAL'))
from dotenv import load_dotenv
import scrapy
from scrapy.crawler import CrawlerProcess
from homzmart_scraping.homzmart_scraping.items import CatPageItem
from scrapy.loader import ItemLoader
import json
from scraper_api import ScraperAPIClient

# Scrapper API for rotating through proxies
client = ScraperAPIClient(os.getenv('SCRAPER_API_KEY'))

# Access the output of the "homzmart_home_page_spider" script stored in the JSON file 'Output_Home_Page.json'
try:
    with open(os.getenv('DATA_FOLDER_PATH_AIRFLOW') + '/Output_Home_Page.json', 'r') as file: # ADDED the path to the data folder to tell Airflow where to look for the JSON file
        data = json.load(file)
except FileNotFoundError:
    with open(os.getenv('DATA_FOLDER_PATH_LOCAL') + '/Output_Home_Page.json', 'r') as file: # If you are using the local env, the interpreter will look for the JSON file in a different directory
        data = json.load(file)

urls_from_home_page = [d['cat_url'] for d in data] # No need to define first_url in the spider class below anymore as we are reading the output of the previous script

class CatPageSpider(scrapy.Spider): # Extract the sub-cateogry names and URLs from the category pages
    name = 'cat_page_spider'
    allowed_domains = ['homzmart.com']
    custom_settings = {"FEEDS":{"Output_Cat_Page.json":{"format":"json", "overwrite": True}}}

    def start_requests(self):
        for url in urls_from_home_page:
            yield scrapy.Request(client.scrapyGet(url = url, render=True, country_code='de'), callback = self.parse)
    
    async def parse(self, response):
        for sub_cat in response.css('div[role=tabpanel]'):
            l = ItemLoader(item = CatPageItem(), selector = sub_cat)
            l.add_css('sub_cat_name', 'a div.header::text')
            l.add_css('sub_cat_url', 'a::attr(href)')
            l.add_value('response_url', response.headers['Sa-Final-Url']) # Use this instead of response.url if you are using a proxy rotation service such as ScraperAPI

            yield l.load_item()

#Run the spider
process = CrawlerProcess(settings = {
    # Adjusting the scraping behavior to rotate appropriately through proxies and user agents
    "CONCURRENT_REQUESTS": 3, # The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader
    "DOWNLOAD_TIMEOUT": 60, # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
    "RETRY_TIMES": 5, # Catch and retry failed requests up to 5 times
    "ROBOTSTXT_OBEY": False, # Saves one API call
})
process.crawl(CatPageSpider)
process.start()