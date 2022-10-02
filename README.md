# python_scrapy_airflow_pipeline
This repo contains a full-fledged Python-based script that scrapes a JavaScript-rendered website (homzmart.com/en), cleans the data, and pushes the results to a cloud-based database. The workflow is orchestrated on Airflow to run automatically

# 1. Objective of the Project
The goal of the project was to scrape an E-commerce website that sells furniture online (homzmart.com/en) to get insights about the company's **product assortment** and **pricing**. The aim was to create a table containing all kinds of information about the products on the website including:
- **Product name** + **Product Display Page** (PDP) URL
- **Category name** of the product + **Category URL**
- **Sub-category name** of the product + **Sub-category URL**
- **Number of product pages** under the product's sub-category
- **Page rank** of the product in the browsing area
- The link to the **product's main image**
- **Product description**
- **Current Price**
- **Discount Tag**
- **Strikethrough Price**
- **Vendor Name**
- **Promised Delivery Time**
- **Availability Type** (On-demand vs. In Stock)
- **Dimensions** (L x W x H)
- **SKU Name**

The website employed several **throttling** and **anti-bot** mechanisms and its content was **rendered by Javascript**, making it a very challenging website to scrape effectively at scale.

The website has **4 sections**:
1. The **Home Page** --> This is the **landing page** of the website ```https://homzmart.com/en```
  - This page was used to scrape the **category names** and **links**
2. The **Category Pages** --> These are pages that contain **all** products under a particular category (e.g., Beds, Sofas, Storage, etc.)
  - An example of a category page (Beds) --> ```https://homzmart.com/en/products/3#1```
  - These pages were used to obtain the **sub-category names** and **links**
3. The **Sub-category Pages** --> These are pages that contain **all** products under a particular sub-category (e.g., )
  - An example of a sub-category page under Beds (King Beds) --> ```https://homzmart.com/en/products/4288#1```
  - These pages were used to obtain the **product page links**
4. The **Product Pages**
  - An example of a product page under King Beds --> ```https://homzmart.com/en/product-details/FF.A022```
  - These pages were used to obtain all the remaining information from the list above
 
The result of the pipeline after it finishes execution looks as follows (only a snippet of the table is shown because it is huge):

![image](https://user-images.githubusercontent.com/98691360/193466397-25d667ed-8ba1-4ac5-a21e-0aae43e7a2e1.png)

Since the crawling process had to be done repeatedly, it was necessary to orchestrate the entire process via Airflow so that it runs at a regular cadence. I will explain the process of reproducing the code on your own machine below.

# 2. Usability and Reproducability
This section is split into two parts. Section one explains how to replicate the crawling code **without the Airflow orchestration**. Section two demonstrates how to create a **pipeline out of the scrapy spiders**. The Airflow pipeline uses the **Python Operator**, **Email Operator**, and **File Sensor** to orchestrate the process.

## 2.1 Reproducing the Scraping Code Without the Airflow Orchestration
**Step 1:** **Clone the repo** using this command in your terminal
```git clone https://github.com/omar-elmaria/about_you_case_study.git```

**Step 2:** **Create a virtual environment** by running this command ```python -m venv venv_scraping```

**Step 3:** **Activate the virtual environment** by typing this ```source venv_scraping/bin/activate``` if you are on Mac/Linux or ```source venv_scraping/Scripts/activate``` if you are on Windows. You might need to replace the forwardslashes with a backslash if you are on Windows

**Step 4:** **Double-check that you are using the correct Python path** by typing ```which python``` and clicking enter (```which python3 on Mac/Linux```). It should point to the Python executable in the virtual environment you just created

**Step 5:** ```Ctrl-Shift-P``` to **view the command palette in VSCode** --> ```Python: Select Interpreter``` --> **Browse to the Python executable in your virtual environment** so that the Jupyter notebook uses the correct Python interpreter

**Step 6:** Run this command in the terminal to **install the required dependencies** ```pip install -r requirements.txt```

**Step 7:** This website is dynamically rendered by Java Script, so we have three options to scrape it
- **scrapy-playwright**
- **scrapy-splash**
- **Proxy service with JS-rendering capability** (e.g., [ScraperAPI](https://www.scraperapi.com/documentation/python/))

Since this is a **high volume** scraping job, I opted for **option #3**. My preferred service is **ScraperAPI**. You can easily sign up in a couple of minutes with your Email and get an **API key with 5000 API credits**. This should more than suffice for testing purposes.

**Step 8:** Create a .env file with the following parameters **without the curly braces**
```
SCRAPER_API_KEY={API_KEY_FROM_SCRAPER_API}
DATA_FOLDER_PATH_LOCAL="{INSERT_LOCAL_PATH_TO_FOLDER_CONTAINING_THE_JSON_FILES_GENERATED_FROM_SCRAPING}"
DATA_FOLDER_PATH_AIRFLOW="{INSERT_VIRTUAL_PATH_TO_FOLDER_CONTAINING_THE_JSON_FILES_GENERATED_FROM_SCRAPING}"
```
The local path can look something like this:
```"I:\scraping_gigs\python_scrapy_airflow_project\homzmart_scraping\data"```
Note that I used backslashes because I using the Windows OS

The virtual path is **ONLY required for the Airflow step**, so you can skip it you don't want to orchestrate the process. That said, it can look something like this:
```"/opt/airflow/python_scrapy_airflow_project/homzmart_scraping/data"```

Note that I used forwardslashes here because the Airflow container is usually created in a Linux environment. Also, keep in mind that the ending of both paths are the **same**. You are simply **cloning** the data folder on your local computer to the Airflow environment. If you want more elaboration on this step, please check out my [guide](https://github.com/omar-elmaria/airflow_installation_instructions) on how to **install Airflow locally on your machine** and navigate to step 11 under section 1.

**Step 9:** Add a new environment variable to ```PYTHONPATH``` pointing to the location of your ```python_scrapy_airflow_pipeline``` project folder.

![image](https://user-images.githubusercontent.com/98691360/193468732-428f0d19-a0b7-469d-bdbb-39ebbeca7b31.png)

The new value that will be added under the Path variable is --> %PYTHONPATH%

N.B. You will need to restart your computer for this change to come into effect

**Step 10:** Delete the JSON files from the data folder to start on a clean slate

**Step 11:** Now, you are ready to scrape the website. The order of running the scripts should be as follows:
- ```homzmart_home_page_spider.py```
- ```homzmart_cat_page_spider.py```
- ```homzmart_subcat_page_spider.py```
- ```homzmart_prod_page_spider.py```

You can ignore the last two spiders ```homzmart_combine_jsons.py``` and ```homzmart_delete_tables.py```. These scripts are used to push the scraped data to an **Airtable** database hosted on the cloud. You will **not** be able to replicate these steps because you will not have the API keys required to access these private databases.

You can also ignore the ```test_crawlera.py``` and ```test_scraperapi.py```. These test scripts were created to play around with the most popular Proxy API services on the market, **Zyte Smart Proxy Manager (Formerly Crawlera)** and **ScraperAPI**

**Step 12.1:** The output of the ```homzmart_home_page_spider.py``` script should look something like this

![image](https://user-images.githubusercontent.com/98691360/193467592-0a54c4b5-4b4e-4293-b3d4-03228509de19.png)

**Step 12.2:** The output of the ```homzmart_cat_page_spider.py``` script should look something like this. Please note that the screenshot is truncated to preserve space

![image](https://user-images.githubusercontent.com/98691360/193467614-a351c680-23b0-4685-b880-ba1c41e435c3.png)

**Step 12.3:** The output of the ```homzmart_subcat_page_spider.py``` script should look something like this. Please note that the screenshot is truncated to preserve space

![image](https://user-images.githubusercontent.com/98691360/193467661-c3e5fc04-d605-48d6-aeb2-33d42f777d15.png)

**Step 12.4:** The output of the ```homzmart_prod_page_spider.py``` script should look something like this. Please note that the screenshot is truncated to preserve space

![image](https://user-images.githubusercontent.com/98691360/193467675-ea1df684-076a-4a3d-b888-dc0bb85670d6.png)

**N.B.** I purposely adjusted the script to only scrape a small portion of the website because the website has **more than 60,000 pages** and the entire process takes **several hours to complete**. The entire script should run in under 5 minutes.

## 2.2 Building a pipeline from the Scrapy Spiders
The pre-requisite to this section is installing **Docker** and **Airflow** on your local machine. Please follow the steps explained in **section #1** of my other [guide](https://github.com/omar-elmaria/airflow_installation_instructions) excluding **step 7** and come back to this part once you're done.

- After installing Airflow, you will need to add the following commands to a ```Dockerfile```:
```
FROM apache/airflow:2.3.4
# Install the libraries required for scraping
RUN pip3 install scrapy scrapy-playwright pyairtable scrapy-proxy-pool scrapy-user-agents scraperapi-sdk python-dotenv pandas numpy
# Install the playwright headless browsers
RUN playwright install
# Add a default path
ENV PYTHONPATH="$PYTHONPATH:/opt/airflow/python_scrapy_airflow_pipeline"
```

- You will also need to add the following parameters to the **.env file** within the Airflow directory if you haven't already. Note that this might be different from the .env file you used in the first part.
```
AIRFLOW_IMAGE_NAME=apache/airflow:2.3.4
AIRFLOW_UID=50000
AIRFLOW__SMTP__SMTP_PASSWORD={GOOGLE_PASSWORD_WITHOUT_THE_CURLY_BRACES}
```
To generate the ```GOOGLE_PASSWORD``` and be able to send emails via Airflow, please follow the steps in this [guide](https://naiveskill.com/send-email-from-airflow/)

It is generally recommended to have one external directory to host the DAGs from **all of your projects**. I call it **airflow-local** and it looks something like this

![image](https://user-images.githubusercontent.com/98691360/193469052-46ba942e-3e83-4d23-aca4-c78dfd17f139.png)

- Finally, you will need to add a **new volume** to the docker-compose file under the ```volumes:``` section like this
```- {INSERT_LOCAL_PATH_TO_PYTHON_SCRAPY_AIRFLOW_PIPELINE_PROJECT}:/opt/airflow/python_scrapy_airflow_pipeline```

- Now, you are ready to launch Airflow, go to your browser and type in ```localhost:8080``` and enter the credentials
  - **username:** airflow
  - **password:** airflow

You should land on a page that looks like this

![image](https://user-images.githubusercontent.com/98691360/193469245-71d5798e-efcb-48e0-8488-55aa50474ef6.png)

The DAG itself will look something like this

![image](https://user-images.githubusercontent.com/98691360/193469308-3d920b4b-ed5e-4bcd-9a86-e5a6e222cd15.png)

- Before triggering the DAG, you will need to **set a new connection** for the file sensor steps. To do that, go to ```Admin``` --> ```Connections```, and click on the **plus** sign. Enter a new connection of type **"File (path)"** and enter the path to ```data``` folder in the Airflow environment. Typically, you will **not** need to change the path shown in the screenshot if you followed the steps of this guide

![image](https://user-images.githubusercontent.com/98691360/193469402-98cfc31b-937d-48bb-83c7-759516ac6089.png)

- Now, you are ready to fire up the DAG. Navigate to the **grid view**, click on the **play** button, and then **Trigger DAG**. The steps should be executed sequentially as shown in the screenshot below. The JSON files will gradually appear in your local directory

![image](https://user-images.githubusercontent.com/98691360/193469898-6c7bf612-ca5e-47b1-b593-41720df63914.png)

## 2.3 Things to Keep in Mind
- If you change anything in the ```Dockerfile``` (e.g., add more dependencies), you will need to re-build the docker image. Run the commands below in your terminal **from within the directory that hosts the Airflow folder structure**
```docker-compose down --volumes --rmi all```
```docker-compose up -d```

These two commands **remove the Airflow image** and **re-build** it using the new parameters in the **Dockerfile** and **docker-compose** file

- If you change anything in the ```docker-compose``` file (e.g., add a new volume), you don't need to re-build the image. It is enough to stop the **docker containers** and **spin them up again** by running the following commands, again from within the directory that hosts the Airflow folder structure
```docker-compose down```
```docker-compose up -d```

- If you face a ModuleNotFound Error, it is usually because you are importing modules from a path that is not recognized by Python. To remedy that, you will need to add that path to an environment variable pointing to the path **from which you start searching and importing your module**. The environment variable should be added to the following places:
  - **On your operating system** --> Check step 9 under section 2.1
  - **In the Dockerfile** --> Check step 1 under section 2.2
  - Possibly also a **new volume** in the docker-compose file if you are importing from a folder that is different from ```./dags```, ```./plugins```, or ```./logs``` --> Check step 3 under section 2.2

# 3. Questions?
If you have any questions or wish to build a scraper for a particular use case, feel free to contact me on [LinkedIn](https://www.linkedin.com/in/omar-elmaria/)
