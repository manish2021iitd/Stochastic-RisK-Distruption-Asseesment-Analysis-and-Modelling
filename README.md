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
