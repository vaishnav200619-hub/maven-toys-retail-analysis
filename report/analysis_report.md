# Maven Toys Retail Sales & Inventory Analysis Report

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
The total revenue from the analyzed period was approximately $14,444,572.35. The total profit was approximately $4,014,029.00, giving an overall profit margin of 27.79%.

## 9. Product Analysis
The highest revenue product was Lego Bricks with approximately $2,388,882.63 in sales. Product-level performance was used to evaluate unit sales, revenue generation, and margin quality.

## 10. Category Analysis
The Toys category generated the highest revenue across all categories.

## 11. Store Analysis
The highest revenue store was Maven Toys Ciudad de Mexico 2 with approximately $554,553.43.

## 12. Inventory Analysis
Inventory was analyzed using stock levels and product sales volume. Low stock positions were flagged based on the lower end of the inventory distribution without assuming out-of-stock status unless the data explicitly supports it.

## 13. Profitability Analysis
The analysis identified categories, products, and stores with the strongest profit contribution. Margin-based comparisons were calculated from revenue and profit, rather than being inferred from product labels.

## 14. Key Findings
- Total revenue was approximately $14,444,572.35.
- Total profit was approximately $4,014,029.00.
- Overall profit margin was 27.79%.
- Toys generated the highest category revenue.
- Lego Bricks generated the highest revenue among individual products.
- Maven Toys Ciudad de Mexico 2 generated the highest revenue among stores.

## 15. Business Recommendations
1. Prioritize replenishment planning for products with strong sales but relatively low stock coverage.
2. Review pricing and product mix in lower-margin product categories.
3. Compare top-performing stores to weaker-performing stores for merchandising and inventory practices.
4. Track monthly sales trends to prepare for seasonal demand changes.

## 16. Limitations
The project depends on the actual data files available in the workspace. Some future analyses could be expanded with customer or supplier data to support deeper demand forecasting and profitability analysis.

## 17. Conclusion
The Maven Toys dataset is suitable for a strong retail analytics portfolio project. It contains clean sales, product, inventory, and store tables that support meaningful revenue, profitability, and operational analysis.
