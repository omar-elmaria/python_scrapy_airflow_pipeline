# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Compose
from w3lib.html import remove_tags
import re

def domain_func(url_part):
    return 'https://homzmart.com' + url_part

def symbols_func(string_val):
    return string_val.replace('x', 'X').replace('amp;', ' and ').replace('&', '').replace('×', 'X').replace('\u00a0', '')

def ampersand_func(string_val):
    return string_val.replace('amp;', '')

def img_links_func_input(links):
    temp_var = re.findall('(?<=url\(")(.+)(?="\);)', links) # Extract the link from the style attribute
    return temp_var

def text_list_collapse_fun(elem_list):
    return ' | '.join([str(elem) for elem in elem_list]).replace(' | NA', '') # Collapse and join the elements via ' | ', then remove the NA that gets added at the end of thr string

def img_num_func(elem):
    return len(elem) # Find the length of the list of image links

def price_symbols_func(string_val):
    return string_val.replace('-', '').replace('%', '').replace('EGP', '').replace(' ', '').replace(',', '').replace('\n', '') # Remove the unnecessary symbols from price data

def price_head_func(price):
    return price.split('\n')[0].replace(',', '') # To select the first text element that has the current price

def colon_func(string_val):
    if string_val != 'NA':
        return string_val.split(':')[1]
    else:
        return 'NA' # If the returned value from the logic in the spider = 'NA', do not use the split method to prevent the "index is out of bounds error". Instead, simply return NA

def process_num_or_string(value): # Automatically detect the data tyoe of "value" (string, numeric, etc.)
    try:
        return eval(value)
    except:
        return value

def process_na_or_val_exist_discount(value): # If the discount value does not exist, return "NA". If it does, return discount / 100 so that it can be treated as a percentage
    if value == 'NA':
        return 'NA'
    else:
        return value / 100

def arabic_func(string_val): # Replace non-Ascii (e.g., Arabic) characters with the literal string " {Arabic Chars}" 
    return ''.join([i if ord(i) < 128 else ' [Ar]' for i in string_val]).strip()

# Note: The order of functions in the MapCompose function is important
class HomePageItem(scrapy.Item): # For the class "HomePageSpider"
    # define the fields for your item here like:
    cat_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    cat_url = scrapy.Field(input_processor = MapCompose(domain_func), output_processor = TakeFirst())
    response_url = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())

class CatPageItem(scrapy.Item): # For the class "CatPageSpider" --> Getting the sub-category page links
    # define the fields for your item here like:
    sub_cat_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    sub_cat_url = scrapy.Field(input_processor = MapCompose(domain_func), output_processor = TakeFirst())
    response_url = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())

class SubCatPageItem(scrapy.Item): # For the class "SubCatPageSpider" --> Getting the individual product page links
    # define the fields for your item here like:
    prod_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, symbols_func, arabic_func), output_processor = TakeFirst())
    prod_pg_rank = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = Compose(TakeFirst(), process_num_or_string))
    last_pg = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = Compose(TakeFirst(), process_num_or_string))
    prod_url = scrapy.Field(input_processor = MapCompose(domain_func), output_processor = TakeFirst())
    response_url = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())

class ProdPageItem(scrapy.Item): # For the class "ProdPageSpider" --> Getting data from individual product pages
    # define the fields for your item here like:
    # General page info
    prod_disp_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, symbols_func, arabic_func), output_processor = TakeFirst())
    
    # Merchandising data
    main_img_link = scrapy.Field(output_processor = TakeFirst())
    all_img_links = scrapy.Field(input_processor = MapCompose(img_links_func_input), output_processor = text_list_collapse_fun)
    img_num = scrapy.Field(input_processor = MapCompose(img_links_func_input), output_processor = img_num_func)
    prod_desc = scrapy.Field(input_processor = MapCompose(remove_tags, arabic_func), output_processor = text_list_collapse_fun)

    # Price data
    curr_price = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, price_head_func, process_num_or_string), output_processor = TakeFirst())
    discount_tag = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, price_symbols_func, process_num_or_string), output_processor = Compose(TakeFirst(), process_na_or_val_exist_discount))
    original_price = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, price_symbols_func, process_num_or_string), output_processor = TakeFirst())

    # Product Info List
    vendor_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    vendor_url_homzmart = scrapy.Field(input_processor = MapCompose(domain_func), output_processor = TakeFirst())
    promised_delivery = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, str.strip), output_processor = TakeFirst())
    avail_type = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, str.strip), output_processor = TakeFirst())
    dims = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, str.strip, symbols_func), output_processor = TakeFirst())
    material = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, ampersand_func, str.strip), output_processor = TakeFirst())
    country_origin = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, str.strip), output_processor = TakeFirst())
    sku_name = scrapy.Field(input_processor = MapCompose(remove_tags, colon_func, str.strip), output_processor = TakeFirst())

    # Response URL
    response_url = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
