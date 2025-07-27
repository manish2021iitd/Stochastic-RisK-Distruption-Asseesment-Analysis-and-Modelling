# Stochastic-RisK-Asseesment-Model
### Repo Structure:
    Stochastic-RisK-Asseesment-Mode
    ├── data/
    │   ├── DataCoSupplyChainDataset.csv    # raw dataset
    │   ├── DescriptionDataCoSupplyChain.csv
    │   └── cleaned_supply_chain_data.csv   # Output from cleaning script
    ├── notebook/
    │   ├── data_cleaning.ipynb             # Jupyter notebook for data cleaning
    │   └── distribution_fitting.ipynb      # Jupyter notebook for distribution fitting
    │   └── copula_alt.ipynb                # created for copula analysis
    ├── src/
    │   ├── __init__.py                     # Makes 'src' a Python package
    │   └── simulation_model.py             # (To contain simulation logic for Streamlit)
    ├── .gitignore                          # Specifies files/folders to ignore in Git
    ├── README.md                           # Project overview, setup, and instructions
    └── requirements.txt                    # List of Python dependencies

## 1. Data Mapping and Disruption Variables
Based on the DataCoSupplyChainDataset.csv file, here's a mapping of relevant fields to disruption variables:

* Disruption Frequency / Inter-arrival Time:

    * order date (DateOrders): Used to calculate inter_arrival_time, which directly represents the time between consecutive orders and can serve as a proxy for the frequency of business events, and subsequently, disruption events if tied to orders.
    
    * Late_delivery_risk: A binary indicator (0 or 1) that directly flags an order as having a late delivery risk, indicating a potential disruption.
    
    * Delivery Status: Provides granular information about delivery outcomes, such as 'Late delivery', 'Advance shipping', and 'Shipping on time', clearly indicating disruption status.

* Severity/Cost Impact:

    * order_profit_per_order (formerly Order Profit Per Order): Directly indicates the financial profit or loss associated with each order, serving as a primary measure of cost impact. Negative values indicate losses.
    
    * benefit_per_order (formerly Benefit per order): Similar to profit per order, representing the financial gain or loss.
    
    * order_item_discount, order_item_discount_rate: Can indicate efforts to mitigate customer dissatisfaction due to delays, which might be a hidden cost or a symptom of disruption.
    
    * Supplier-related features: The dataset does not contain explicit supplier features. However, Department Name and Category Name could indirectly represent aspects of the supply chain related to product groups.

* Customer-related features:

    * Customer City, Customer Country, Customer Id, Customer Segment, Customer State, Customer Street, Customer Zipcode: Provide demographic and geographic information about the customers affected by orders, which can be valuable for segmenting disruption impacts.

* Product-related features:

    * Category Name, Product Name, Product Price: Provide details about the products involved, which might influence disruption likelihood or impact (e.g., critical components, high-value items).

* Logistics/Transportation-related features:

    * Days for shipping (real) and Days for shipment (scheduled): Crucial for determining delivery_duration_actual and delivery_duration_scheduled, and subsequently shipping_delay_days, a direct measure of logistics disruption.
    
    * Shipping Mode: Indicates the method of transport (e.g., Standard Class), which can be analyzed for its correlation with delays.
    
    * Order City, Order Country, Order Region, Order State: Geographical information about the order's destination or origin, important for understanding regional disruption patterns.

## 2. Data Cleaning
I have created a reproducible data cleaning script that performs the following:

* Imports the raw dataset: The script loads DataCoSupplyChainDataset.csv.

* Handles missing values:

    * Customer Lname was filled with 'Unknown'.
    
    * Customer Zipcode was filled with the mode.
    
    * Order Zipcode was filled with 0 due to a high percentage of missing values.
    
    * Product Description (which was entirely empty) was dropped.

* Converts dates:

    * order date (DateOrders) and shipping date (DateOrders) were converted to datetime objects.
    
    * New features delivery_duration_actual, delivery_duration_scheduled, shipping_delay_days, and inter_arrival_time (time between consecutive orders for each customer) were engineered.
    
    * Normalises units: Column names related to profit and sales were renamed for consistency (e.g., Order Profit Per Order to order_profit_per_order). No explicit unit conversion was required as the data appeared to be in consistent units.

* Outputs a cleaned CSV: A cleaned dataset named cleaned_supply_chain_data.csv has been saved to your environment.

* Basic EDA charts: The following basic EDA charts have been generated to visualize key distributions:

    * shipping_delay_days_distribution.png: Histogram showing the distribution of shipping delays.
      
      <img width="1000" height="600" alt="shipping_delay_days_distribution" src="https://github.com/user-attachments/assets/1b1466e9-3d49-4854-a2a7-7fbeb633973c" />

    
    * order_profit_per_order_distribution.png: Histogram showing the distribution of profit per order, indicating financial impact.
      
      <img width="1000" height="600" alt="order_profit_per_order_distribution" src="https://github.com/user-attachments/assets/fdcfe3a6-7c2a-4c4b-80dc-c11682a2df2b" />

    
    * inter_arrival_time_distribution.png: Histogram showing the distribution of inter-arrival times between orders.
      
      <img width="1000" height="600" alt="inter_arrival_time_distribution" src="https://github.com/user-attachments/assets/086dc9bd-d9bf-456c-894b-26cd33d1e33f" />

    * delivery_status_count.png: Bar chart showing the counts of different delivery statuses.
      
      <img width="1000" height="600" alt="delivery_status_count" src="https://github.com/user-attachments/assets/a3d491ff-bd25-4de1-941c-24a54227a0f2" />

    
    * late_delivery_risk_count.png: Bar chart showing the counts of orders with and without late delivery risk.
      
      <img width="700" height="500" alt="late_delivery_risk_count" src="https://github.com/user-attachments/assets/cd5d4c91-d076-4ea0-a478-b5d942908689" />


## 3. Distribution Fitting Prototype
I have implemented a prototype for fitting common probability distributions to key variables (inter_arrival_time and order_profit_per_order).

* Key Variables Analyzed:

    * Inter-Arrival Time (Days)
    
    * Order Profit Per Order (Note: For this variable, Lognormal and Pareto distributions were fitted only to positive values, as these distributions are defined for positive inputs. This limitation should be considered for variables with both positive and negative values like profit/loss.)

* Distributions Fitted: Exponential, Weibull, Lognormal, and Pareto.

* Parameter Estimates + Goodness-of-Fit Metrics:
The following table summarizes the fitted parameters, Kolmogorov-Smirnov (KS) p-value, Akaike Information Criterion (AIC), and Bayesian Information Criterion (BIC) for each distribution. Lower AIC/BIC values generally indicate a better fit, while a higher KS p-value suggests that the data distribution is similar to the fitted distribution.
    <img width="864" height="191" alt="Screenshot 2025-07-27 at 7 28 26 PM" src="https://github.com/user-attachments/assets/8cae5e6d-9d84-4f5a-acde-362065e12ebc" />

