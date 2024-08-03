"""
Recipe Scraper and Data Processor

This script automates the process of scraping recipe links from a website and extracting detailed recipe data. It uses Selenium WebDriver to navigate through pages, collect recipe URLs, and extract relevant information such as titles, ingredients, and instructions. The collected data is then saved into a CSV file, including metadata such as the load date and an incrementing batch number.

Modules Used:
- selenium: For web scraping and browser automation.
- csv: For writing data to CSV files.
- datetime: For timestamping the load date.
- os: For file and directory operations.

Functions:
- scrape_recipes(): Scrapes recipe links from the specified pages of the website and stores them in a global list.
- extract_recipe_data(recipe_url): Extracts the title, ingredients, and instructions from a given recipe URL.
- get_batch_number(): Manages and returns the current batch number by incrementing it from a persistent file.
- process_links(): Processes each collected recipe link, extracts the recipe data, and writes the results to a CSV file with additional metadata.

Usage:
1. Ensure that the path to the chromedriver executable is correctly set in the script.
2. Run the script to start scraping recipes from the website.
3. The script will collect links from the first three pages, extract recipe details, and save them to 'recipes.csv'.
4. The CSV file will include columns for the recipe title, ingredients, instructions, load date, and batch number.

Notes:
- The script uses a hardcoded path to the chromedriver executable; ensure this path is correct for your setup.
- The batch number is stored in 'batch_number.txt' and is incremented with each script run.
- The 'recipes.csv' file will be overwritten with each run, so previous data will be lost unless saved elsewhere.

Dependencies:
- Selenium WebDriver
- ChromeDriver (compatible with the installed version of Google Chrome)

Author: Jayson Roque
Date: 2024-08-03
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import csv

# Global variable to store recipe links
all_recipes_links = []

# Setup Chrome options
# Didn't use headless as it seems to cause CORS Policy issue
chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Setting up my WebDriver
service = Service(r'C:/Users/roque/Documents/chromedriver-win64/chromedriver.exe') 
driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_recipes():
    global all_recipes_links  # Use the global variable
    all_recipes_links = []  # Clear the list before scraping
    base_url = 'https://panlasangpinoy.com/recipes/'
    total_pages = 223  # Total number of pages to scrape, site uses pagination

    try:
        for page in range(1, total_pages + 1):
            page_url = base_url if page == 1 else f"{base_url}page/{page}/"
            driver.get(page_url)

            try:
                # Wait until the div with class "content-sidebar-wrap" is present
                content_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="content-sidebar-wrap"]'))
                )
                
                # Find all links with class "entry-title-link" within the specified div
                recipe_links = content_div.find_elements(By.XPATH, './/a[@class="entry-title-link"]')
                
                # Extract the href attributes
                for link in recipe_links:
                    try:
                        href = link.get_attribute('href')
                        all_recipes_links.append(href)
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
        print(f'An error occurred while processing {recipe_url}: {e}')
        return None, None, None

def process_links():
    all_recipes = []

    for link in all_recipes_links:
        print(f'Processing link: {link}')
        title, ingredients, instructions = extract_recipe_data(link)
        
        if title and ingredients and instructions:
            all_recipes.append({
                'Title': title,
                'Ingredients': ingredients,
                'Instructions': instructions
            })

    # Save collected results to CSV
    with open('recipes.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'Ingredients', 'Instructions'])
        writer.writeheader()  # Write the header only once
        writer.writerows(all_recipes)
    
    driver.quit()

# Run the scraping function to collect links
scrape_recipes()

# Run the processing function to extract data from the collected links
process_links()

