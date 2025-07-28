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


## 3. Distribution Fitting 
I have implemented a prototype for fitting common probability distributions to key variables (inter_arrival_time and order_profit_per_order).

* Key Variables Analyzed:

    * Inter-Arrival Time (Days)
    
    * Order Profit Per Order (Note: For this variable, Lognormal and Pareto distributions were fitted only to positive values, as these distributions are defined for positive inputs. This limitation should be considered for variables with both positive and negative values like profit/loss.)

* Distributions Fitted: Exponential, Weibull, Lognormal, and Pareto.

* Parameter Estimates + Goodness-of-Fit Metrics:
The following table summarizes the fitted parameters, Kolmogorov-Smirnov (KS) p-value, Akaike Information Criterion (AIC), and Bayesian Information Criterion (BIC) for each distribution. Lower AIC/BIC values generally indicate a better fit, while a higher KS p-value suggests that the data distribution is similar to the fitted distribution.

    <img width="864" height="191" alt="Screenshot 2025-07-27 at 7 28 26 PM" src="https://github.com/user-attachments/assets/8cae5e6d-9d84-4f5a-acde-362065e12ebc" />

* You can find the full comparison table in the file distribution_fitting_comparison_table.csv.

* For each variable and distribution, a plot visualizing the fitted probability density function (PDF) against the empirical data histogram has been generated:
     *  Inter-Arrival Time (Days) - Exponential Fit:
       From the distribution fitting comparison table, the Exponential distribution for 'Inter-Arrival Time (Days)' has the following characteristics:
        <img width="1000" height="600" alt="fit_plot_inter-arrival_time_(days)_exponential" src="https://github.com/user-attachments/assets/35553b26-a5a0-4ac8-88db-0d007c8a2c57" />
    
        * Parameters: loc = 1.0, scale = 160.952:
        In the context of the Exponential distribution, loc typically represents the minimum value or a shift parameter, and scale is the inverse of the rate parameter (λ). So, a scale of approximately 160.952 implies an average inter-arrival time of about 160.952 days.
        
        * KS p-value: 2.88×10^{-10} :
         A very low p-value (much less than 0.05) indicates that the null hypothesis (that the data comes from an Exponential distribution) is rejected. This suggests that the Exponential distribution does not provide a statistically good fit for the 'Inter-Arrival Time (Days)' data according to the Kolmogorov-Smirnov test.
        
        * AIC (Akaike Information Criterion): 545577, BIC (Bayesian Information Criterion): 545594 
        AIC and BIC are used for model comparison, where lower values generally indicate a better fit. When compared to the Weibull distribution (AIC: 545553, BIC: 545580) for 'Inter-Arrival Time (Days)', the Exponential distribution has slightly higher AIC and BIC values, suggesting that the Weibull distribution provides a marginally better fit according to these criteria.
        
        * Looking at the "Inter-Arrival Time (Days) - Exponential Fit" plot, we can visually assess how well the red line (fitted Exponential PDF) aligns with the grey bars (empirical data histogram). While the Exponential distribution captures the overall decaying shape, it might not perfectly represent the nuances of the data's distribution, especially if there are initial peaks or different decay rates not captured by a single exponential.
        
        * While the Exponential distribution is a common choice for modeling inter-arrival times (especially in Poisson processes), the low KS p-value suggests it might not be the most appropriate fit for your specific 'Inter-Arrival Time (Days)' data from a statistical standpoint. The Weibull distribution appears to offer a slightly better fit based on the AIC and BIC values.
          
     *  Inter-Arrival Time (Days) - Weibull Fit: From the distribution fitting comparison table, the Weibull distribution for 'Inter-Arrival Time (Days)' has the following characteristics:
       <img width="1000" height="600" alt="fit_plot_inter-arrival_time_(days)_weibull" src="https://github.com/user-attachments/assets/e2f7140c-680b-4c3b-8285-29b9829a8aa7" />
   
        * Parameters: shape = 1.024, loc = 0.974, scale = 162.487 
        In the context of the Weibull distribution:shape (also known as the 'k' parameter) describes the shape of the distribution. A value close to 1 (like 1.024) indicates a distribution that is very similar to an Exponential distribution. If it were significantly less than 1, it would imply a decreasing failure rate (e.g., infant mortality), and if significantly greater than 1, an increasing failure rate (e.g., wear-out failures).
    
        * loc (location parameter) shifts the distribution along the x-axis. A value of approximately 0.974 means the distribution effectively starts slightly after 0.
        scale (also known as the 'lambda' parameter) is a characteristic life parameter, similar to the mean in an exponential distribution. A value of 162.487 suggests that 63.2% of events occur by this time.
    
        * KS p-value: 7.36×10^−7
         Similar to the Exponential fit, a very low p-value (much less than 0.05) indicates that the null hypothesis (that the data comes from a Weibull distribution) is rejected. This suggests that even the Weibull distribution does not provide a statistically good fit for the 'Inter-Arrival Time (Days)' data according to the Kolmogorov-Smirnov test.
    
        * AIC (Akaike Information Criterion): 545553
        BIC (Bayesian Information Criterion): 545580
        Comparing these to the Exponential fit (AIC: 545577, BIC: 545594), the Weibull distribution has slightly lower AIC and BIC values. This indicates that, according to these information criteria, the Weibull distribution is a marginally better model for this data compared to the Exponential distribution, despite both having low KS p-values.

        * Looking at the "Inter-Arrival Time (Days) - Weibull Fit" plot, you can visually assess how well the red line (fitted Weibull PDF) aligns with the grey bars (empirical data histogram). Given that the shape parameter is close to 1, the Weibull curve will closely resemble the Exponential curve, reflecting similar characteristics in terms of decreasing probability density over time.
    
        * While the Weibull distribution (especially with a shape parameter close to 1) is a strong candidate for modeling inter-arrival times, the low KS p-value still suggests that it might not be a perfect statistical fit for your 'Inter-Arrival Time (Days)' data. However, based on the AIC and BIC, it is a better fit than the Exponential distribution among the distributions tested. The visual fit should also be considered, as slight deviations might not always be captured by goodness-of-fit tests alone, especially with large datasets. The very small p-values for both Exponential and Weibull might indicate that the empirical distribution has characteristics that are not fully captured by these simple parametric forms, or that with a large dataset, even small deviations from the theoretical distribution lead to statistical rejection.
           
    * Inter-Arrival Time (Days) - Lognormal Fit:
      From the distribution fitting comparison table, the Lognormal distribution for 'Inter-Arrival Time (Days)' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_inter-arrival_time_(days)_lognormal" src="https://github.com/user-attachments/assets/42209b0e-2ea9-48da-b0d9-eaadc90d379f" />
      
        * Parameters: shape = 0.906, loc = -14.743, scale = 122.389
        The shape parameter (often denoted as 's' or 'sigma') determines the skewness of the distribution. A value of 0.906 indicates a right-skewed distribution, which is typical for Lognormal distributions.
        
        * The loc parameter (location) shifts the distribution. A negative loc of -14.743 is unusual as inter-arrival times are non-negative. This might indicate that the fitting algorithm is using a general form of the Lognormal distribution that allows for a negative shift, even if the actual data is strictly positive. However, since we filtered for data_series > 0, the fitted loc might be trying to account for the left tail's behavior.
        
        * The scale parameter (often denoted as 'exp(mu)') is related to the median of the distribution. A value of 122.389 suggests a central tendency around this value after transformation.
        
        * KS p-value: 8.13×10^−65
        This is an extremely low p-value, even lower than those for the Exponential and Weibull distributions. This strongly indicates that the Lognormal distribution does not provide a good statistical fit for the 'Inter-Arrival Time (Days)' data according to the Kolmogorov-Smirnov test. The null hypothesis that the data comes from a Lognormal distribution is unequivocally rejected.
        
        * AIC (Akaike Information Criterion): 549754, BIC (Bayesian Information Criterion): 549780
        These values are significantly higher than those for the Exponential (AIC: 545577, BIC: 545594) and Weibull (AIC: 545553, BIC: 545580) distributions. This further confirms that the Lognormal distribution is a worse fit compared to the other two for 'Inter-Arrival Time (Days)', based on information criteria.
        
        *Looking at the "Inter-Arrival Time (Days) - Lognormal Fit" plot, you would likely observe that the fitted Lognormal PDF (red line) does not closely follow the shape of the empirical data histogram (grey bars). The pronounced right skewness inherent in the Lognormal might not align well with the actual distribution of your inter-arrival times, especially if your data is more indicative of a constant rate (exponential-like) or has a more complex shape.
        
        * Based on all metrics (extremely low KS p-value, and significantly higher AIC/BIC compared to other fits), the Lognormal distribution is the least suitable among the tested distributions for modeling the 'Inter-Arrival Time (Days)' data. Its fit is statistically poor, and information criteria also disfavor it. You should prioritize other distributions (like Weibull or Exponential) for this variable, even though their KS p-values were also low, their AIC/BIC values were much better.
            
    * Inter-Arrival Time (Days) - Pareto Fit:
      From the distribution fitting comparison table, the Pareto distribution for 'Inter-Arrival Time (Days)' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_inter-arrival_time_(days)_pareto" src="https://github.com/user-attachments/assets/142ee898-71e7-4911-89e9-f5d008212281" />
        
        * Parameters: shape = 106738994.35, loc = -17179869183.0, scale = 17179869183.999998
        The shape parameter (often denoted as 'alpha') is extremely large (over 100 million). A very large shape parameter in a Pareto distribution implies a very steep decay, meaning that the probability of observing values much larger than the minimum is extremely low. This unusually large value might indicate issues with the fit or that the data does not exhibit the long-tail behavior typically associated with Pareto distributions.
        
        * The loc parameter (location) is a large negative value, and the scale parameter is a large positive value. For a standard Pareto distribution (Type I), loc would represent the minimum value, and it must be positive. The scipy.stats.pareto implementation is a shifted Pareto distribution where loc can represent a shift. However, these extremely large and offsetting loc and scale values (scale being loc + min_x for a standard Pareto) are often indicative of a poor or degenerate fit, where the optimization algorithm struggled to find sensible parameters that accurately describe the data. It suggests that the data points are very concentrated, and the fitting is trying to find a distribution that effectively models a point mass.
        
        
        * KS p-value: 2.88×10−10
         This extremely low p-value (much less than 0.05) indicates that the null hypothesis (that the data comes from a Pareto distribution) is rejected. This strongly suggests that the Pareto distribution does not provide a statistically good fit for the 'Inter-Arrival Time (Days)' data according to the Kolmogorov-Smirnov test.
        
        * AIC (Akaike Information Criterion): 545579 and BIC (Bayesian Information Criterion): 545605
        These values are higher than those for the Weibull distribution (AIC: 545553, BIC: 545580) and very similar to the Exponential distribution (AIC: 545577, BIC: 545594). Compared to Lognormal, Pareto is better, but among the Exponential, Weibull, and Pareto, Weibull remains the best based on AIC/BIC. The very high magnitude of the parameters, combined with the low p-value and relatively higher AIC/BIC, strongly suggests that the Pareto distribution is not a suitable model for this dataset.

        *  Looking at the "Inter-Arrival Time (Days) - Pareto Fit" plot, you would likely see that the fitted Pareto PDF (red line) would be a very steep, rapidly decaying curve that does not effectively capture the distribution of your empirical data (grey bars), especially given the extremely large shape parameter.
        
        * Based on all metrics (extremely low KS p-value, unusual and large parameter values, and higher AIC/BIC compared to Weibull), the Pareto distribution is not a suitable fit for modeling the 'Inter-Arrival Time (Days)' data. Its fit is statistically poor and the estimated parameters are highly implausible for a typical long-tail phenomenon. Among the distributions tested, the Weibull distribution provided the relatively best fit for 'Inter-Arrival Time (Days)', although its KS p-value was also low, suggesting that none of the tested simple parametric distributions perfectly describe the data.
            
    * Order Profit Per Order - Exponential Fit:
    
    * Order Profit Per Order - Weibull Fit:
    
    * Order Profit Per Order - Lognormal Fit:
    
    * Order Profit Per Order - Pareto Fit:

* These plots help in visually assessing the goodness of fit.
