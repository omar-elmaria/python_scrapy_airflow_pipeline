from dotenv import load_dotenv
# Load environment variables
load_dotenv()

import pandas as pd
import json
import os
from pyairtable import Table
import numpy as np

##---------------------------------------------------------START OF JSON FILE CONVERSION TO PANDAS DFs---------------------------------------------------------##

class CombineJsons():
    # Declare the data frames that will take the data from json files
    df_home_page = pd.DataFrame(columns = ['cat_name', 'cat_url', 'response_url'])
    df_cat_page = pd.DataFrame(columns = ['sub_cat_name', 'sub_cat_url', 'response_url'])
    df_subcat_page = pd.DataFrame(columns = ['prod_name', 'last_pg', 'prod_page_rank', 'prod_url', 'response_url'])
    df_prod_page = pd.DataFrame(columns = 
            ['prod_disp_name', 'main_img_link', 'all_img_links', 'img_num', 
            'prod_desc', 'curr_price', 'discount_tag', 'original_price',
            'vendor_name', 'vendor_url_homzmart', 'promised_delivery', 'avail_type',
            'dims', 'material', 'country_origin', 'sku_name', 'response_url'])

    # Create a list with the names of all json files generated by the pervious scripts
    try:
        json_files = [pos_json for pos_json in os.listdir(os.getenv('DATA_FOLDER_PATH_AIRFLOW')) if pos_json.endswith('.json')] # List the JSON files via the Airflow JSON path
        path_to_json = os.getenv('DATA_FOLDER_PATH_AIRFLOW') # Specify the final JSON path to the Airflow path
    except FileNotFoundError:
        json_files = [pos_json for pos_json in os.listdir(os.getenv('DATA_FOLDER_PATH_LOCAL')) if pos_json.endswith('.json')] # List the JSON files via the local env JSON path
        path_to_json = os.getenv('DATA_FOLDER_PATH_LOCAL') # Specify the final JSON path to the local env path

    # Open the json files and store them in the right data frames
    for idx, js in enumerate(json_files):
        with open(os.path.join(path_to_json, json_files[idx])) as js_file:
            json_text = json.load(js_file)

        if json_files[idx] == 'Output_Home_Page.json':
            df_home_page = pd.DataFrame(json_text)
        elif json_files[idx] == 'Output_Cat_Page.json':
            df_cat_page = pd.DataFrame(json_text)
        elif json_files[idx] == 'Output_SubCat_Page.json':
            df_subcat_page = pd.DataFrame(json_text)
        elif json_files[idx] == 'Output_Prod_Page.json':
            df_prod_page = pd.DataFrame(json_text)

    ##---------------------------------------------------------START OF DATA FRAME MANIPULATION---------------------------------------------------------##

    # Merge the home_page and cat_page data frames
    df_home_cat = df_cat_page.merge(df_home_page, left_on = 'response_url', right_on = 'cat_url', how = 'left', suffixes = ('_cat', '_home')) # LEFT JOIN as the left DF is larger
    # Re-arrange the columns of "df_home_cat"
    cols = ['cat_name', 'cat_url', 'response_url_home', 'sub_cat_name', 'sub_cat_url', 'response_url_cat'] # Provide the right column order
    df_home_cat = df_home_cat[cols]

    # Merge "df_home_cat" with the subcat_page data frame
    # First, delete the duplicates in "df_subcat_page" that happen as a result of the random product sorting followed by Homzmart's website
    df_subcat_page = df_subcat_page.drop_duplicates(subset = ['prod_url'])

    # Second, create another version of the "response_url" column that does not have pagination so that you can join it to "sub_cat_url" without problems
    df_subcat_page['response_url_for_join'] = df_subcat_page['response_url'].replace('#[0-9].*', '#1', regex = True)

    # Third, perform the join
    df_home_cat_subcat = df_home_cat.merge(df_subcat_page, left_on = 'sub_cat_url', right_on = 'response_url_for_join', how = 'outer') # OUTER JOIN as we want to UNION both data frames

    # Merge "df_home_cat_subcat" with the prod_page data frame to get the complete data set
    df_prod_page = df_prod_page.replace('NA', None, regex = True) # Converting all NAs to "None" so that we don't face problems with data type consistency
    df_all = df_home_cat_subcat.merge(df_prod_page, left_on = 'prod_url', right_on = 'response_url', how = 'inner', suffixes = ('_sub_cat', '_prod')) # LEFT JOIN as the right DF could be smaller due timeouts. INNER JOIN is another option when you don't want NULLs

    ##---------------------------------------------------------START OF LOADING DFs TO AIRTABLE---------------------------------------------------------##

    # Load the Airtable's API key and base ID of the Homzmart's table
    api_key = os.environ['AIRTABLE_TOKEN']
    base_id = os.environ['AIRTABLE_BASE_ID']

    # Change the each pandas DF to a list of dictionaries because the "batch_create" method of the Airtable API only accepts that format
    # "lod" refers to "List of Dictionaries" 
    df_cat_subcat_lod = df_home_cat.replace({np.nan: None}).to_dict(orient='records') # All categories and sub-categories
    df_prod_links_lod = df_subcat_page.replace({np.nan: None}).to_dict(orient='records') # All individual product links under each scraped sub-category
    df_pdp_info_lod = df_prod_page.replace({np.nan: None}).to_dict(orient='records') # All PDP info of each scraped product link under the scraped sub-categories
    df_all_lod = df_all.replace({np.nan: None}).to_dict(orient='records') # All information combined. This method of replacing NaNs works with both Airflow and the local env
    
    # Access the tables created in Airtable
    table_cat_subcat = Table(api_key, base_id, 'df_cat_subcat')
    table_prod_links = Table(api_key, base_id, 'df_prod_links')
    table_pdp_info = Table(api_key, base_id, 'df_pdp_info')
    table_all = Table(api_key, base_id, 'df_all')

    # Push the data frames to Airtable
    table_cat_subcat.batch_create(df_cat_subcat_lod)
    table_prod_links.batch_create(df_prod_links_lod)
    table_pdp_info.batch_create(df_pdp_info_lod)
    table_all.batch_create(df_all_lod)