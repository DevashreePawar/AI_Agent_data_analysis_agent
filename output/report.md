# Data Analysis Report: sample_sales.csv

## 1. Dataset Overview
The dataset "sample_sales.csv" contains 100 rows and 6 columns. The columns are: date, region, product, units_sold, revenue, and discount. The data types of these columns are not explicitly mentioned in the log, but based on the analysis steps, we can infer that units_sold, revenue, and discount are numeric columns, while date, region, and product are likely categorical or date/time columns.

## 2. Key Statistics
The analysis revealed the following key statistics:

- The mean units sold is 25.55, with a median of 20.50, and a standard deviation of 19.89. The minimum units sold is 3.00, and the maximum is 150.00. The skewness of the units_sold column is 2.83, indicating a right-skewed distribution.
- The mean revenue is 13191.50, with a median of 9675.00, and a standard deviation of 18241.29. The minimum revenue is 2500.00, and the maximum is 180000.00. The skewness of the revenue column is 7.91, indicating a highly right-skewed distribution.

## 3. Correlation Insights
The strongest correlations found are:

- A correlation of 0.605 between units_sold and revenue, suggesting a strong positive relationship between the two columns.
- A correlation of 0.397 between units_sold and discount, indicating a moderate positive relationship.
- A correlation of 0.190 between revenue and discount, suggesting a weak positive relationship.

## 4. Outliers & Anomalies
Two outliers were detected in the units_sold column, with values of 70 and 150. These outliers are likely impacting the sales data and warrant further investigation.

## 5. Category Breakdown
The top products associated with the outliers in the units_sold column are:

- Laptop (33.0%)
- Phone (27.0%)
- Tablet (21.0%)
- Headphones (19.0%)

## 6. Key Takeaways & Recommendations

* The strong positive correlation between units_sold and revenue suggests that increasing units sold can lead to higher revenue.
* The moderate positive correlation between units_sold and discount indicates that discounts may be influencing sales, but the relationship is not as strong as the relationship between units sold and revenue.
* The weak positive correlation between revenue and discount suggests that discounts may not be having a significant impact on revenue.
* The outliers in the units_sold column (70 and 150) may be impacting the sales data and warrant further investigation.
* The top products associated with the outliers in the units_sold column (Laptop, Phone, Tablet, and Headphones) may be worth examining further to understand their sales patterns.