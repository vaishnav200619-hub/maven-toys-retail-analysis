# Maven Toys Retail Sales & Inventory Analysis

## Project Overview
This project analyzes the real Maven Toys retail dataset to understand product performance, store performance, sales trends, and inventory levels.

## Business Problem
Maven Toys needs evidence-based insight into which products, categories, stores, and time periods drive the strongest retail performance and where operational attention is needed.

## Dataset
The project uses the actual raw files in data/raw. These files are kept unchanged and the cleaned data is saved in data/processed.

## Dataset Structure
The verified source tables are:
- sales.csv: transaction-level sales records
- products.csv: product catalog and pricing data
- stores.csv: store metadata and locations
- inventory.csv: store-level stock levels
- calendar.csv: date reference table

## Technologies
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter
- Plotly
- Streamlit
- OpenPyXL

## Data Cleaning
The cleaning workflow standardizes names, converts dates, cleans currency fields, removes duplicate rows, validates relationships, and saves the processed dataset in data/processed.

## Feature Engineering
Revenue, cost, profit, and profit margin were calculated using the actual sales and product data. Month, year, year-month, and quarter fields were also created for trend analysis.

## Exploratory Data Analysis
The EDA covers sales trends, category performance, product profitability, store revenue and profit, and inventory attention areas.

## Key Metrics
- Total revenue: approximately $14,444,572.35
- Total profit: approximately $4,014,029.00
- Overall profit margin: 27.79%
- Total units sold: 1,090,565
- Top category: Toys
- Top product: Lego Bricks
- Top store: Maven Toys Ciudad de Mexico 2

## Key Insights
- Total revenue across the analyzed period was approximately $14,444,572.35.
- Total profit was approximately $4,014,029.00, resulting in an overall profit margin of 27.79%.
- The Toys category generated the highest category revenue at approximately $5,093,241.00.
- The top product by revenue was Lego Bricks with approximately $2,388,882.63 in sales.
- The top store by revenue was Maven Toys Ciudad de Mexico 2 with approximately $554,553.43.

## Dashboard
The Streamlit dashboard is in dashboard/app.py and reads the processed dataset for interactive analysis.

## Project Structure
- data/raw: original unchanged source data
- data/processed: cleaned and merged datasets
- notebooks: data understanding, cleaning, and EDA notebooks
- outputs/charts: saved charts
- outputs/tables: analytical tables
- dashboard: interactive dashboard
- report: business report

## How to Run
1. Install requirements: pip install -r requirements.txt
2. Run the analysis: py build_project.py
3. Start the dashboard: streamlit run dashboard/app.py

## Author
BSc Data Science student
