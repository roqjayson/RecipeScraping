"""
Recipe Scraper and Data Processor

This script automates the process of scraping recipe links from a website and extracting detailed recipe data. It uses Selenium WebDriver to navigate through pages, collect recipe URLs, and extract relevant information such as titles, ingredients, and instructions. The collected data is then saved into a CSV file, including metadata such as the load date and an incrementing batch number.

Modules Used:
- selenium: For web scraping and browser automation.
- csv: For read/writing data to CSV files.
- datetime: For timestamping the load date and managing page ranges.
- os: For file and directory operations.

Functions:
- scrape_recipes(): Scrapes recipe links from the specified pages of the website and stores them in a global list.
- extract_recipe_data(recipe_url): Extracts the title, ingredients, and instructions from a given recipe URL.
- get_batch_number(): Manages and returns the current batch number by incrementing it from a persistent file.
- get_page_range_for_today(): Determines the range of pages to process based on the current date.
- process_links(): Processes each collected recipe link, extracts the recipe data, and writes the results to a CSV file with additional metadata.

Usage:
1. Ensure that the path to the chromedriver executable is correctly set in the script.
2. Schedule the script to run daily using a task scheduler or cron job.
3. The script will collect links from 2 pages per day, extract recipe details, and append them to 'recipes.csv'.
4. The CSV file will include columns for the recipe title, ingredients, instructions, load date, and batch number.

Notes:
- The script uses a hardcoded path to the chromedriver executable; ensure this path is correct for your setup.
- The batch number is stored in 'batch_number.txt' and is incremented with each script run.
- The 'recipes.csv' file will be appended to with each run, preserving data from previous days.
- This script is attached to a task scheduler in Windows (see .bat file as execution script) which will run every 12AM UTC

Dependencies:
- Selenium WebDriver
- ChromeDriver (compatible with the installed version of Google Chrome)

Author: Jayson Roque
Date: 2024-08-03
"""

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import csv
import os

# Global variable to store recipe links and their page numbers
all_recipes_links = []

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Set up the WebDriver
service = Service(r'C:/Users/roque/Documents/chromedriver-win64/chromedriver.exe')  # This is the path of my own chromedriver, make sure to change it appropriately.
driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_recipes(start_page, end_page):
    global all_recipes_links  # Use the global variable
    all_recipes_links = []  # Clear the list before scraping
    base_url = 'https://panlasangpinoy.com/recipes/'

    try:
        for page in range(start_page, end_page + 1):
            page_url = base_url if page == 1 else f"{base_url}page/{page}/"
            driver.get(page_url)

            try:
                # Wait until the div with class "content-sidebar-wrap" is present
                content_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="content-sidebar-wrap"]'))
                )
                
                # Find all links with class "entry-title-link" within the specified div
                recipe_links = content_div.find_elements(By.XPATH, './/a[@class="entry-title-link"]')
                
                # Extract the href attributes and store page number
                for link in recipe_links:
                    try:
                        href = link.get_attribute('href')
                        all_recipes_links.append((href, page))  # Store the link and page number as a tuple
                    except StaleElementReferenceException:
                        # Handle the case where the element becomes stale
                        print(f"StaleElementReferenceException while processing link on page {page}")
                        continue

            except TimeoutException:
                print(f"TimeoutException while locating the content div or recipe links on page {page}")

            except Exception as e:
                print(f"An error occurred while locating recipe links on page {page}: {e}")
                continue

            # Pause to avoid overwhelming the server
            time.sleep(5)

    finally:
        print("All links collected!")

def extract_recipe_data(recipe_url):
    try:
        driver.get(recipe_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'oc-recipe-container'))
        )

        # Find the recipe container
        recipe_container = driver.find_element(By.CLASS_NAME, 'oc-recipe-container')

        # Extract title
        title = recipe_container.find_element(By.CLASS_NAME, 'wprm-recipe-name').text

        # Extract ingredients
        ingredients = recipe_container.find_element(By.CLASS_NAME, 'wprm-recipe-ingredients').text

        # Extract instructions
        instructions = recipe_container.find_element(By.CLASS_NAME, 'wprm-recipe-instructions').text

        return title, ingredients, instructions

    except Exception as e:
        print(f'An error occurred while processing {recipe_url}: No recipe or ingredients found!')
        return None, None, None

def get_batch_number():
    batch_file = 'batch_number/batch_number.txt'
    if os.path.exists(batch_file):
        with open(batch_file, 'r') as file:
            batch_number = int(file.read().strip())
    else:
        batch_number = 0
    batch_number += 1
    with open(batch_file, 'w') as file:
        file.write(str(batch_number))
    return batch_number

def get_page_range_for_today():
    current_date = datetime.now().date()
    pages_per_day = 2

    # Check if the CSV file exists and has content
    if os.path.exists('results/recipes.csv') and os.path.getsize('results/recipes.csv') > 0:
        with open('results/recipes.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            last_load_date = []
            last_page_num = []
            for row in reader:
                last_load_date = row['load_dte']
                last_page_num = row['page_number']
            get_date = datetime.strptime(last_load_date, '%Y-%m-%d %H:%M:%S').date()
            days_elapsed = (current_date - get_date).days
            start_page = int(last_page_num) + 1
    else:
        last_load_date = current_date
        days_elapsed = 0
        start_page = 1

    print(f"Last Load Date: {last_load_date}")
    print(f"Days Elapsed: {days_elapsed}")

    end_page = min(start_page + pages_per_day - 1, 223)  # Assuming there are 223 pages

    print(f"Start Page: {start_page}, End Page: {end_page}")

    return start_page, end_page

def process_links():
    all_recipes = []
    load_dte = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    batch_number = get_batch_number()

    for link, page_number in all_recipes_links:  # Unpack the link and page number
        print(f'Processing link: {link}')
        title, ingredients, instructions = extract_recipe_data(link)
        
        if title and ingredients and instructions:
            all_recipes.append({
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'load_dte': load_dte,
                'batch_number': batch_number,
                'page_number': page_number  
            })

    # Save collected results to CSV
    file_exists = os.path.isfile('results/recipes.csv')
    with open('results/recipes.csv', 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['title', 'ingredients', 'instructions', 'load_dte', 'batch_number', 'page_number']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # Write the header only once
        writer.writerows(all_recipes)
    
    driver.quit()

# Determine the range of pages to process today
start_page, end_page = get_page_range_for_today()

# Run the scraping function to collect links
scrape_recipes(start_page, end_page)

# Run the processing function to extract data from the collected links
process_links()
