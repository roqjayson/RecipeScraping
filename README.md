# Recipe Data Processing Solution

## Overview

The solution involves scraping recipe data from a website, storing it in CSV files, loading and processing the data in a database, and finally normalizing and presenting it for analysis. The data flow consists of several stages, from data collection to reporting.

## Data Flow Diagram

Here is a conceptual data flow diagram (DFD) for the solution:

1. **Data Collection**
   - **Source**: [Panlasang Pinoy](https://panlasangpinoy.com/)
   - **Process**: Web Scraping Script using Selenium in Python
   - **Output**: Raw Recipe Data in CSV Files

2. **Data Storage**
   - **Process**: CSV File Management
   - **Output**: Batch-wise CSV Files

3. **Data Loading** (Not sure yet what DBMS to use)
   - **Process**: CSV to Database 
   - **Database**: Recipe Data Database
   - **Output**: Data Loaded by Batch Number

4. **Data Cleaning and Transformation** (Not sure yet if ETL or Python to use)
   - **Process**: ETL Tool / Python Script
   - **Output**: Cleaned Data in Data Vault Schema

5. **Data Normalization**
   - **Process**: Data Normalization
   - **Output**: Data Mart Schema

6. **Data Presentation**
   - **Process**: Data View Creation
   - **Output**: Reports/Views in Presentation Schema
  


```plaintext
+----------------+       +---------------------+       +-----------------+
|   Website      |  ---> |extract_create_csv.py| ---> |  Raw CSV Files  |
+----------------+       +---------------------+       +-----------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      | CSV File Management |
                                                      +---------------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |   Database Loading  |
                                                      | (recipe_data DB)    |
                                                      +---------------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |  Data Cleaning &    |
                                                      |  Transformation     |
                                                      |  (ETL/Python)       |
                                                      +---------------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |  Data Vault Schema  |
                                                      +---------------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |  Data Mart Schema   |
                                                      +---------------------+
                                                                 |
                                                                 |
                                                                 v
                                                      +---------------------+
                                                      |  Data Presentation  |
                                                      |  (Views/Reports)    |
                                                      +---------------------+
```

## Detailed Data Solution

1. **Data Collection**
   - **Source**: The source of the data is a website that lists recipes.
   - **Process**: Use the `Recipe Scraper and Data Processor` script to scrape recipe links and extract detailed data (title, ingredients, instructions).
   - **Output**: The data is initially saved in a CSV file named `recipes.csv`. The file is divided into smaller CSV files based on batch numbers for efficient processing.

2. **Data Storage**
   - **Process**: Manage and archive CSV files according to batch numbers. For example, `recipes_batch_001.csv`, `recipes_batch_002.csv`, etc.
   - **Details**: Store these files in a designated directory for batch-wise management.

3. **Data Loading**
   - **Process**: Use a database management tool or SQL script to load data from CSV files into a database.
   - **Database Name**: `recipe_data`
   - **Details**: Load data into a staging table or a raw data table for each batch. Ensure batch numbers are tracked for proper data integration.

4. **Data Cleaning and Transformation**
   - **Process**: Clean and preprocess the raw data using an ETL tool (like Apache NiFi, Talend) or a Python script.
   - **Details**: Handle missing values, normalize data formats, and apply necessary transformations.
   - **Output**: Cleaned data is loaded into the `data_vault` schema.

5. **Data Normalization**
   - **Process**: Transform the cleaned data into a normalized format.
   - **Schema Name**: `data_vault`
   - **Details**: Organize data into dimension and fact tables for better querying and analysis.

6. **Data Presentation**
   - **Process**: Create views or reports based on the normalized data.
   - **Schema Name**: `presentation_schema`
   - **Details**: Define views to aggregate, filter, and present data as needed for reporting and analysis.
