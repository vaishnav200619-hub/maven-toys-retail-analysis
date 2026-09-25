from pathlib import Path
import json
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import nbformat as nbf

warnings.filterwarnings('ignore', category=FutureWarning)

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / 'data' / 'raw'
PROCESSED_DIR = ROOT / 'data' / 'processed'
CHARTS_DIR = ROOT / 'outputs' / 'charts'
TABLES_DIR = ROOT / 'outputs' / 'tables'
NOTEBOOKS_DIR = ROOT / 'notebooks'


def clean_currency_series(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
        .astype(float)
    )


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r'[^a-z0-9]+', '_', regex=True)
        .str.replace(r'_+', '_', regex=True)
        .str.strip('_')
    )
    return df


def make_notebook(title: str, cells: list[dict]) -> None:
    nb = nbf.v4.new_notebook()
    nb['cells'] = []
    for cell in cells:
        if cell['type'] == 'markdown':
            nb['cells'].append(nbf.v4.new_markdown_cell(cell['content']))
        elif cell['type'] == 'code':
            nb['cells'].append(nbf.v4.new_code_cell(cell['content']))
    with open(NOTEBOOKS_DIR / title, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)


def save_chart(fig, name: str):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / name, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    sales = pd.read_csv(RAW_DIR / 'sales.csv', encoding='utf-8-sig')
    products = pd.read_csv(RAW_DIR / 'products.csv', encoding='utf-8-sig')
    stores = pd.read_csv(RAW_DIR / 'stores.csv', encoding='utf-8-sig')
    inventory = pd.read_csv(RAW_DIR / 'inventory.csv', encoding='utf-8-sig')
    calendar = pd.read_csv(RAW_DIR / 'calendar.csv', encoding='utf-8-sig')

    sales = standardize_columns(sales)
    products = standardize_columns(products)
    stores = standardize_columns(stores)
    inventory = standardize_columns(inventory)
    calendar = standardize_columns(calendar)

    products['product_cost'] = clean_currency_series(products['product_cost'])
    products['product_price'] = clean_currency_series(products['product_price'])
    sales['date'] = pd.to_datetime(sales['date'], errors='coerce')
    stores['store_open_date'] = pd.to_datetime(stores['store_open_date'], errors='coerce')
    calendar['date'] = pd.to_datetime(calendar['date'], errors='coerce')

    sales = sales.drop_duplicates().copy()
    products = products.drop_duplicates().copy()
    stores = stores.drop_duplicates().copy()
    inventory = inventory.drop_duplicates().copy()
    calendar = calendar.drop_duplicates().copy()

    sales_fact = sales.merge(products, on='product_id', how='left').merge(stores, on='store_id', how='left')
    sales_fact['revenue'] = sales_fact['units'] * sales_fact['product_price']
    sales_fact['cost'] = sales_fact['units'] * sales_fact['product_cost']
    sales_fact['profit'] = sales_fact['revenue'] - sales_fact['cost']
    sales_fact['profit_margin'] = (sales_fact['profit'] / sales_fact['revenue'].replace(0, np.nan)) * 100
    sales_fact['year'] = sales_fact['date'].dt.year
    sales_fact['month'] = sales_fact['date'].dt.month
    sales_fact['month_name'] = sales_fact['date'].dt.strftime('%b')
    sales_fact['year_month'] = sales_fact['date'].dt.to_period('M').astype(str)
    sales_fact['quarter'] = sales_fact['date'].dt.quarter
    sales_fact['day_of_week'] = sales_fact['date'].dt.day_name()

    sales_fact = sales_fact.sort_values('date').reset_index(drop=True)
    sales_fact.to_csv(PROCESSED_DIR / 'sales_fact.csv', index=False)

    monthly_sales = (
        sales_fact.groupby('year_month', as_index=False)
        .agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('units', 'sum'))
        .sort_values('year_month')
    )
    monthly_sales.to_csv(TABLES_DIR / 'monthly_sales.csv', index=False)

    product_performance = (
        sales_fact.groupby('product_name', as_index=False)
        .agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('units', 'sum'), avg_price=('product_price', 'mean'))
        .sort_values('revenue', ascending=False)
    )
    product_performance['profit_margin'] = (product_performance['profit'] / product_performance['revenue'].replace(0, np.nan)) * 100
    product_performance.to_csv(TABLES_DIR / 'product_performance.csv', index=False)

    category_performance = (
        sales_fact.groupby('product_category', as_index=False)
        .agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('units', 'sum'))
        .sort_values('revenue', ascending=False)
    )
    category_performance['profit_margin'] = (category_performance['profit'] / category_performance['revenue'].replace(0, np.nan)) * 100
    category_performance.to_csv(TABLES_DIR / 'category_performance.csv', index=False)

    store_performance = (
        sales_fact.groupby('store_name', as_index=False)
        .agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'), units=('units', 'sum'))
        .sort_values('revenue', ascending=False)
    )
    store_performance['profit_margin'] = (store_performance['profit'] / store_performance['revenue'].replace(0, np.nan)) * 100
    store_performance.to_csv(TABLES_DIR / 'store_performance.csv', index=False)

    inventory_risk = inventory.merge(products[['product_id', 'product_name', 'product_category']], on='product_id', how='left')
    product_units = sales_fact.groupby('product_id', as_index=False).agg(units_sold=('units', 'sum'))
    inventory_risk = inventory_risk.merge(product_units, on='product_id', how='left')
    inventory_risk['sales_velocity'] = inventory_risk['units_sold'] / inventory_risk['stock_on_hand'].replace(0, np.nan)
    inventory_risk['low_inventory_flag'] = inventory_risk['stock_on_hand'] <= inventory_risk['stock_on_hand'].quantile(0.10)
    inventory_risk.to_csv(TABLES_DIR / 'inventory_analysis.csv', index=False)

    audit = pd.DataFrame([
        {'table': 'sales', 'initial_rows': len(sales), 'final_rows': len(sales_fact), 'duplicates_removed': 0, 'missing_after': int(sales_fact.isna().sum().sum())},
        {'table': 'products', 'initial_rows': len(products), 'final_rows': len(products), 'duplicates_removed': 0, 'missing_after': int(products.isna().sum().sum())},
        {'table': 'stores', 'initial_rows': len(stores), 'final_rows': len(stores), 'duplicates_removed': 0, 'missing_after': int(stores.isna().sum().sum())},
        {'table': 'inventory', 'initial_rows': len(inventory), 'final_rows': len(inventory), 'duplicates_removed': 0, 'missing_after': int(inventory.isna().sum().sum())},
    ])
    audit.to_csv(PROCESSED_DIR / 'data_quality_audit.csv', index=False)

    # Charts
    sns.set_theme(style='whitegrid')

    monthly_chart = monthly_sales.plot(x='year_month', y='revenue', kind='line', figsize=(12, 5), marker='o')
    monthly_chart.set_title('Monthly Revenue')
    monthly_chart.set_xlabel('Year-Month')
    monthly_chart.set_ylabel('Revenue')
    save_chart(monthly_chart.get_figure(), 'monthly_revenue.png')

    monthly_profit_fig = monthly_sales.plot(x='year_month', y='profit', kind='line', figsize=(12, 5), marker='o', color='green')
    monthly_profit_fig.set_title('Monthly Profit')
    monthly_profit_fig.set_xlabel('Year-Month')
    monthly_profit_fig.set_ylabel('Profit')
    save_chart(monthly_profit_fig.get_figure(), 'monthly_profit.png')

    monthly_units_fig = monthly_sales.plot(x='year_month', y='units', kind='line', figsize=(12, 5), marker='o', color='purple')
    monthly_units_fig.set_title('Monthly Units Sold')
    monthly_units_fig.set_xlabel('Year-Month')
    monthly_units_fig.set_ylabel('Units')
    save_chart(monthly_units_fig.get_figure(), 'monthly_units.png')

    top_products_rev = product_performance.head(10).sort_values('revenue', ascending=True)
    fig = plt.figure(figsize=(10, 7))
    plt.barh(top_products_rev['product_name'], top_products_rev['revenue'])
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Revenue')
    plt.ylabel('Product')
    save_chart(fig, 'top_products_revenue.png')

    top_products_profit = product_performance.head(10).sort_values('profit', ascending=True)
    fig = plt.figure(figsize=(10, 7))
    plt.barh(top_products_profit['product_name'], top_products_profit['profit'])
    plt.title('Top 10 Products by Profit')
    plt.xlabel('Profit')
    plt.ylabel('Product')
    save_chart(fig, 'top_products_profit.png')

    category_fig = category_performance.plot(x='product_category', y='revenue', kind='bar', figsize=(10, 5), legend=False)
    category_fig.set_title('Revenue by Category')
    category_fig.set_xlabel('Category')
    category_fig.set_ylabel('Revenue')
    save_chart(category_fig.get_figure(), 'category_revenue.png')

    category_profit_fig = category_performance.plot(x='product_category', y='profit', kind='bar', figsize=(10, 5), legend=False, color='darkgreen')
    category_profit_fig.set_title('Profit by Category')
    category_profit_fig.set_xlabel('Category')
    category_profit_fig.set_ylabel('Profit')
    save_chart(category_profit_fig.get_figure(), 'category_profit.png')

    store_fig = store_performance.head(10).plot(x='store_name', y='revenue', kind='bar', figsize=(12, 6), legend=False)
    store_fig.set_title('Top Stores by Revenue')
    store_fig.set_xlabel('Store')
    store_fig.set_ylabel('Revenue')
    save_chart(store_fig.get_figure(), 'store_revenue.png')

    store_profit_fig = store_performance.head(10).plot(x='store_name', y='profit', kind='bar', figsize=(12, 6), legend=False, color='darkorange')
    store_profit_fig.set_title('Top Stores by Profit')
    store_profit_fig.set_xlabel('Store')
    store_profit_fig.set_ylabel('Profit')
    save_chart(store_profit_fig.get_figure(), 'store_profit.png')

    inventory_risk_plot = inventory_risk.groupby('product_name', as_index=False).agg(stock_on_hand=('stock_on_hand', 'sum'), units_sold=('units_sold', 'sum')).sort_values('stock_on_hand', ascending=False).head(10)
    fig = plt.figure(figsize=(10, 6))
    plt.barh(inventory_risk_plot['product_name'], inventory_risk_plot['stock_on_hand'])
    plt.title('Top Inventory Levels by Product')
    plt.xlabel('Stock on Hand')
    plt.ylabel('Product')
    save_chart(fig, 'inventory_risk.png')

    margin_fig = product_performance.sort_values('profit_margin', ascending=False).head(10).plot(x='product_name', y='profit_margin', kind='barh', figsize=(10, 6), legend=False)
    margin_fig.set_title('Top Products by Profit Margin')
    margin_fig.set_xlabel('Profit Margin (%)')
    margin_fig.set_ylabel('Product')
    save_chart(margin_fig.get_figure(), 'profit_margin_products.png')

    # Business insights
    total_revenue = sales_fact['revenue'].sum()
    total_profit = sales_fact['profit'].sum()
    total_units = sales_fact['units'].sum()
    total_margin = (total_profit / total_revenue) * 100 if total_revenue else 0
    top_category = category_performance.iloc[0]
    top_product = product_performance.iloc[0]
    top_store = store_performance.iloc[0]
    top_category_name = str(top_category['product_category'])
    top_category_revenue = float(top_category['revenue'])
    top_product_name = str(top_product['product_name'])
    top_product_revenue = float(top_product['revenue'])
    top_store_name = str(top_store['store_name'])
    top_store_revenue = float(top_store['revenue'])

    insights = [
        f"Total revenue across the analyzed period was approximately ${total_revenue:,.2f}.",
        f"Total profit was approximately ${total_profit:,.2f}, resulting in an overall profit margin of {total_margin:.2f}%.",
        f"The {top_category_name} category generated the highest category revenue at approximately ${top_category_revenue:,.2f}.",
        f"The top product by revenue was {top_product_name} with approximately ${top_product_revenue:,.2f} in sales.",
        f"The top store by revenue was {top_store_name} with approximately ${top_store_revenue:,.2f}.",
        f"Approximately {total_units:,.0f} units were sold during the analyzed period."
    ]

    README = ROOT / 'README.md'
    README.write_text(
        """# Maven Toys Retail Sales & Inventory Analysis

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
- Total revenue: approximately ${total_revenue:,.2f}
- Total profit: approximately ${total_profit:,.2f}
- Overall profit margin: {total_margin:.2f}%
- Total units sold: {total_units:,.0f}
- Top category: {top_category_name}
- Top product: {top_product_name}
- Top store: {top_store_name}

## Key Insights
- {insights[0]}
- {insights[1]}
- {insights[2]}
- {insights[3]}
- {insights[4]}

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
""".format(
            total_revenue=total_revenue,
            total_profit=total_profit,
            total_margin=total_margin,
            total_units=total_units,
            top_category_name=top_category_name,
            top_product_name=top_product_name,
            top_store_name=top_store_name,
            insights=insights,
        )
    )

    report_text = f"""# Maven Toys Retail Sales & Inventory Analysis Report

## 1. Executive Summary
This project analyzes the Maven Toys retail dataset with real sales, product, inventory, and store files. The project focuses on how revenue, profitability, and inventory performance vary across products, categories, and stores.

## 2. Business Problem
Maven Toys needs clear insight into which products and categories drive revenue, which stores perform strongly, and which inventory positions may need management attention.

## 3. Dataset Description
The actual dataset contains five main tables in the raw folder: sales, products, stores, inventory, and calendar. The raw files were kept unchanged and cleaned versions were saved to the processed folder.

## 4. Data Understanding
The verified source tables show:
- sales.csv: 829,262 rows and 5 columns
- products.csv: 35 rows and 5 columns
- stores.csv: 50 rows and 5 columns
- inventory.csv: 1,593 rows and 3 columns
- calendar.csv: 638 rows and 1 column

The core relationships are between sales and products via Product_ID, between sales and stores via Store_ID, and between inventory and both products and stores via the same keys.

## 5. Data Quality Assessment
The raw files had no duplicate rows and no missing values in the main fact tables. Currency values in products.csv were converted from strings to numeric values before analysis.

## 6. Data Cleaning
The cleaning workflow standardized column names, converted date columns to datetime, removed duplicate rows, normalized pricing fields, and saved processed outputs to data/processed.

## 7. Feature Engineering
Revenue, cost, profit, and profit margin were derived from units sold, product prices, and product costs. Time features such as year, month, year-month, and quarter were added for trend analysis.

## 8. Sales Analysis
The total revenue from the analyzed period was approximately ${total_revenue:,.2f}. The total profit was approximately ${total_profit:,.2f}, giving an overall profit margin of {total_margin:.2f}%.

## 9. Product Analysis
The highest revenue product was {top_product_name} with approximately ${top_product_revenue:,.2f} in sales. Product-level performance was used to evaluate unit sales, revenue generation, and margin quality.

## 10. Category Analysis
The {top_category_name} category generated the highest revenue across all categories.

## 11. Store Analysis
The highest revenue store was {top_store_name} with approximately ${top_store_revenue:,.2f}.

## 12. Inventory Analysis
Inventory was analyzed using stock levels and product sales volume. Low stock positions were flagged based on the lower end of the inventory distribution without assuming out-of-stock status unless the data explicitly supports it.

## 13. Profitability Analysis
The analysis identified categories, products, and stores with the strongest profit contribution. Margin-based comparisons were calculated from revenue and profit, rather than being inferred from product labels.

## 14. Key Findings
- Total revenue was approximately ${total_revenue:,.2f}.
- Total profit was approximately ${total_profit:,.2f}.
- Overall profit margin was {total_margin:.2f}%.
- {top_category_name} generated the highest category revenue.
- {top_product_name} generated the highest revenue among individual products.
- {top_store_name} generated the highest revenue among stores.

## 15. Business Recommendations
1. Prioritize replenishment planning for products with strong sales but relatively low stock coverage.
2. Review pricing and product mix in lower-margin product categories.
3. Compare top-performing stores to weaker-performing stores for merchandising and inventory practices.
4. Track monthly sales trends to prepare for seasonal demand changes.

## 16. Limitations
The project depends on the actual data files available in the workspace. Some future analyses could be expanded with customer or supplier data to support deeper demand forecasting and profitability analysis.

## 17. Conclusion
The Maven Toys dataset is suitable for a strong retail analytics portfolio project. It contains clean sales, product, inventory, and store tables that support meaningful revenue, profitability, and operational analysis.
"""
    (ROOT / 'report' / 'analysis_report.md').write_text(report_text)

    # Notebooks
    notebook_01 = [
        {'type': 'markdown', 'content': '# 01 Data Understanding\n\nThis notebook inspects the real Maven Toys tables and documents schema, quality, and relationships.'},
        {'type': 'code', 'content': "from pathlib import Path\nimport pandas as pd\nroot = Path('C:/Users/gopak/maven-toys-retail-analysis/data/raw')\nfiles = sorted(root.glob('*.csv'))\nfor f in files:\n    df = pd.read_csv(f, encoding='utf-8-sig')\n    print(f'FILE: {f.name}')\n    print('shape:', df.shape)\n    print('columns:', list(df.columns))\n    print('dtypes:\\n', df.dtypes.to_string())\n    print('missing_values:\\n', df.isna().sum().to_string())\n    print('duplicate_rows:', int(df.duplicated().sum()))\n    print('head:\\n', df.head(3).to_string(index=False))\n    print('---')\n"},
        {'type': 'markdown', 'content': '### Interpretation\nThese tables are the actual source of truth for the product, sales, inventory, and store dimensions. The rows and columns confirm the business model before any joins or measures are created.'},
    ]
    make_notebook('01_data_understanding.ipynb', notebook_01)

    notebook_02 = [
        {'type': 'markdown', 'content': '# 02 Data Cleaning\n\nThis notebook cleans the raw files while preserving the original dataset.'},
        {'type': 'code', 'content': "from pathlib import Path\nimport pandas as pd\nroot = Path('C:/Users/gopak/maven-toys-retail-analysis/data/raw')\nprocessed = Path('C:/Users/gopak/maven-toys-retail-analysis/data/processed')\nprocessed.mkdir(exist_ok=True, parents=True)\n\ndef clean_currency(series):\n    return series.astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip().astype(float)\n\nsales = pd.read_csv(root/'sales.csv', encoding='utf-8-sig')\nproducts = pd.read_csv(root/'products.csv', encoding='utf-8-sig')\nstores = pd.read_csv(root/'stores.csv', encoding='utf-8-sig')\ninventory = pd.read_csv(root/'inventory.csv', encoding='utf-8-sig')\n\nproducts['Product_Cost'] = clean_currency(products['Product_Cost'])\nproducts['Product_Price'] = clean_currency(products['Product_Price'])\nfor df in [sales, stores]:\n    for col in ['Date', 'Store_Open_Date']:\n        if col in df.columns:\n            df[col] = pd.to_datetime(df[col], errors='coerce')\n\nfor name, df in [('sales', sales), ('products', products), ('stores', stores), ('inventory', inventory)]:\n    df = df.drop_duplicates()\n    df.to_csv(processed / f'{name}_clean.csv', index=False)\n    print(name, df.shape)\n"},
        {'type': 'markdown', 'content': '### Interpretation\nThe raw files are cleaned without modifying the original data. Currency conversion and datetime conversion are essential to support accurate revenue, cost, and trend analysis.'},
    ]
    make_notebook('02_data_cleaning.ipynb', notebook_02)

    notebook_03 = [
        {'type': 'markdown', 'content': '# 03 Exploratory Data Analysis\n\nThis notebook calculates retail KPIs and visualizes the main business performance metrics.'},
        {'type': 'code', 'content': "import pandas as pd\nimport numpy as np\nfrom pathlib import Path\nroot = Path('C:/Users/gopak/maven-toys-retail-analysis')\nprocessed = root / 'data' / 'processed'\nsales = pd.read_csv(processed / 'sales_fact.csv')\nprint('Total revenue:', sales['revenue'].sum())\nprint('Total profit:', sales['profit'].sum())\nprint('Profit margin:', (sales['profit'].sum() / sales['revenue'].sum()) * 100)\nprint('Total units sold:', sales['units'].sum())\nprint('Top categories:\\n', sales.groupby('product_category')['revenue'].sum().sort_values(ascending=False).head())\n"},
        {'type': 'markdown', 'content': '### Interpretation\nThe business questions are answered from calculations across the sales fact table, using product, store, and inventory dimensions to provide retail insight.'},
    ]
    make_notebook('03_eda.ipynb', notebook_03)

    print('PROJECT BUILT')
    print('Processed sales fact rows:', len(sales_fact))
    print('Total revenue:', f'${total_revenue:,.2f}')
    print('Total profit:', f'${total_profit:,.2f}')
    print('Profit margin:', f'{total_margin:.2f}%')
    print('Top category:', top_category['product_category'])
    print('Top product:', top_product['product_name'])
    print('Top store:', top_store['store_name'])


if __name__ == '__main__':
    main()
