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

# 2.1 Reproducing the Scraping Code Without the Airflow Orchestration
- **Step 1:** Clone the repo using this command in your terminal git clone https://github.com/omar-elmaria/python_scrapy_airflow_pipeline.git

**Step 2:** Create a virtual environment by running this command python -m venv venv_scraping

**Step 3:** Activate the virtual environment by typing this source venv_scraping/bin/activate if you are on Mac/Linux or source venv_scraping/Scripts/activate if you are on Windows. You might need to replace the forwardslashes with a backslash if you are on Windows

**Step 4:** Double-check that you are using the correct Python path by typing which python and clicking enter (which python3 on Mac/Linux). It should point to the Python executable in the virtual environment you just created

**Step 5:** Ctrl-Shift-P to view the command palette in VSCode --> Python: Select Interpreter --> Browse to the Python executable in your virtual environment so that the Jupyter notebook uses the correct Python interpreter

**Step 6:** Run this command in the terminal to install the required dependencies pip install -r requirements.txt
