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
import scrapy
from scrapy.crawler import CrawlerProcess
from homzmart_scraping.homzmart_scraping.items import HomePageItem
from scrapy.loader import ItemLoader
from scraper_api import ScraperAPIClient

# Scrapper API for rotating through proxies
client = ScraperAPIClient(os.getenv('SCRAPER_API_KEY'))

class HomePageSpider(scrapy.Spider): # Extract the names and URLs of the categories from the homepage
    name = 'home_page_spider'
    allowed_domains = ['homzmart.com']
    first_url = 'https://homzmart.com/en'
    custom_settings = {"FEEDS":{"Output_Home_Page.json":{"format":"json", "overwrite": True}}}

    def start_requests(self):
        yield scrapy.Request(client.scrapyGet(url = HomePageSpider.first_url, render=True, country_code='de'), callback = self.parse, dont_filter = True)

    async def parse(self, response):
        for cat in response.css('div.site-menu__item'):
            l = ItemLoader(item = HomePageItem(), selector = cat)
            l.add_css('cat_name', 'a')
            l.add_css('cat_url', 'a::attr(href)')
            l.add_value('response_url', response.headers['Sa-Final-Url'])
            
            yield l.load_item()

# Run the spider
process = CrawlerProcess(settings = {
    # Adjusting the scraping behavior to rotate appropriately through proxies and user agents
    "CONCURRENT_REQUESTS": 3, # The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader
    "DOWNLOAD_TIMEOUT": 60, # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
    "RETRY_TIMES": 5, # Catch and retry failed requests up to 5 times
    "ROBOTSTXT_OBEY": False, # Saves one API call
})
process.crawl(HomePageSpider)
process.start()