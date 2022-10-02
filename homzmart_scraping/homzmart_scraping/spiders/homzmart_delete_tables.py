import os
from pyairtable import Table
from dotenv import load_dotenv
import operator as op

# Load environment variables
load_dotenv()

# Load the Airtable's API key and base ID of the Homzmart's table
api_key = os.environ['AIRTABLE_TOKEN']
base_id = os.environ['AIRTABLE_BASE_ID']

class DeleteTables():
    # Access the tables created in Airtable
    table_cat_subcat = Table(api_key, base_id, 'df_cat_subcat')
    table_prod_links = Table(api_key, base_id, 'df_prod_links')
    table_pdp_info = Table(api_key, base_id, 'df_pdp_info')
    table_all = Table(api_key, base_id, 'df_all')

    # Delete records (for testing)
    # Note: With Python 3, since map returns an iterator, use list to return a list
    get_value = op.itemgetter('id')
    table_cat_subcat.batch_delete(list(map(get_value, table_cat_subcat.all())))
    table_prod_links.batch_delete(list(map(get_value, table_prod_links.all())))
    table_pdp_info.batch_delete(list(map(get_value, table_pdp_info.all())))
    table_all.batch_delete(list(map(get_value, table_all.all())))