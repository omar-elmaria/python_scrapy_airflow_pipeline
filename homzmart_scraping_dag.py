# Import the standard Airflow libraries
from airflow.models import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.contrib.sensors.file_sensor import FileSensor
import pendulum
import os

# Import the python scripts as classes and define methods out of these classes
def home_page_spider():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_home_page_spider import HomePageSpider

def cat_page_spider():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_cat_page_spider import CatPageSpider

def subcat_page_spider():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_subcat_page_spider import SubCatPageSpider

def prod_page_spider():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_prod_page_spider import ProdPageSpider

def combine_jsons():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_combine_jsons import CombineJsons

def delete_tables():
    from homzmart_scraping.homzmart_scraping.spiders.homzmart_delete_tables import DeleteTables

def delete_json_files():
    path_to_json_airflow = '/opt/airflow/python_scrapy_airflow_pipeline/homzmart_scraping/data'
    json_files = [pos_json for pos_json in os.listdir(path_to_json_airflow) if pos_json.endswith('.json')] # List all JSON files in the data directory
    for i in json_files:
        os.remove(path_to_json_airflow + '/' + i)

# Define the DAG
default_args = {
    'owner': 'oelmaria',
    'email': ['omar.elmaria@deliveryhero.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'start_date': pendulum.datetime(2022, 5, 31),
    'depends_on_past': False, 
}

dag = DAG(dag_id = 'homzmart_scraping_dag', default_args = default_args, schedule_interval = '*/20 * 31 5 *', catchup = False) # For production. Cron expression --> Every 15 minutes of every hour only for the 29th of May

# Define the Python operators which will run the scripts
home_page_task = PythonOperator(
    task_id = 'home_page',
    python_callable = home_page_spider,
    dag = dag
)

file_sensor_task_home_page = FileSensor(
    task_id = 'file_sense_home_page',
    fs_conn_id = 'json_files_directory', # Must be configured in the Airflow UI via Admin --> Connections
    filepath = '/opt/airflow/python_scrapy_airflow_pipeline/homzmart_scraping/data/Output_Home_Page.json',
    mode = 'poke', # Keep checking until true or a timeout occurs
    poke_interval = 60, # Check for the existence of the JSON file every 60 seconds
    timeout = 300, # Fail the task if the file does not exist after 5 minutes (i.e., 5 trials)
    dag = dag
)

cat_page_task = PythonOperator(
    task_id = 'cat_page',
    python_callable = cat_page_spider,
    dag = dag
)

file_sensor_task_cat_page = FileSensor(
    task_id = 'file_sense_cat_page',
    fs_conn_id = 'json_files_directory',
    filepath = '/opt/airflow/python_scrapy_airflow_pipeline/homzmart_scraping/data/Output_Cat_Page.json',
    mode = 'poke',
    poke_interval = 60,
    timeout = 300, 
    dag = dag
)

subcat_page_task = PythonOperator(
    task_id = 'subcat_page',
    python_callable = subcat_page_spider,
    dag = dag
)

file_sensor_task_subcat_page = FileSensor(
    task_id = 'file_sense_subcat_page',
    fs_conn_id = 'json_files_directory',
    filepath = '/opt/airflow/python_scrapy_airflow_pipeline/homzmart_scraping/data/Output_SubCat_Page.json',
    mode = 'poke',
    poke_interval = 60,
    timeout = 300, 
    dag = dag
)

prod_page_task = PythonOperator(
    task_id = 'prod_page',
    python_callable = prod_page_spider,
    dag = dag
)

file_sensor_task_prod_page = FileSensor(
    task_id = 'file_sense_prod_page',
    fs_conn_id = 'json_files_directory',
    filepath = '/opt/airflow/python_scrapy_airflow_pipeline/homzmart_scraping/data/Output_Prod_Page.json',
    mode = 'poke',
    poke_interval = 60,
    timeout = 300, 
    dag = dag
)

combine_jsons_task = PythonOperator(
    task_id = 'combine_jsons',
    python_callable = combine_jsons,
    retries = 0, # Overrides the default # of retries. We don't want to add duplicates to the Airtable database
    dag = dag
)

delete_json_files_task = PythonOperator(
    task_id = 'delete_json_files',
    python_callable = delete_json_files,
    dag = dag
)

# To see how to send emails via Airflow, check these two blog posts --> https://naiveskill.com/send-email-from-airflow/ + https://stackoverflow.com/questions/58736009/email-on-failure-retry-with-airflow-in-docker-container
success_email_body = f'The homzmart scraping DAG has been successfully executed at {datetime.now()}'
send_email_task = EmailOperator(
    task_id = 'send_email',
    to = ['<omar_moataz@aucegypt.edu>'], # The <> are important. Don't forget to include them. You can add more emails to the list
    subject = "The Airflow DAG Run of Homzmart's Crawler Has Been Successfully Executed",
    html_content = success_email_body,
    dag = dag
)

# This task is NOT needed in the normal DAG run
# delete_tables_task = PythonOperator(
#     task_id = 'delete_tables',
#     python_callable = delete_tables,
#     dag = dag
# )

# Set the order of the tasks
delete_json_files_task >> home_page_task >> file_sensor_task_home_page >> cat_page_task >> file_sensor_task_cat_page >> subcat_page_task >> file_sensor_task_subcat_page
file_sensor_task_subcat_page >> prod_page_task >> file_sensor_task_prod_page >> combine_jsons_task >> send_email_task # Completing the dependency definitions in a second line
