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
    ├── Figures                             # All outout figures
    ├── Output/
    │   ├──fitted_parameters.json
    │   └──fitted_parameters_updated.json
    ├── docs
    │   └──copula_choice.md
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
        
        * The distribution is highly skewed to the right, with a long tail. This indicates that most orders experience little to no delay, but a smaller number of orders experience significant delays.
        
        * The highest frequency (mode) is at or very close to zero, meaning a large majority of shipments are either on time or have minimal delays.
        
        * The delays extend to a considerable number of days, indicating that while rare, some shipments can be severely delayed.
        
        * This distribution highlights that while most of the supply chain operates efficiently in terms of shipping time, there are critical instances of substantial delays that could lead to significant disruptions, customer dissatisfaction, and potentially increased costs. Understanding the characteristics of this tail is crucial for identifying and mitigating high-impact disruption risks.

    
    * order_profit_per_order_distribution.png: Histogram showing the distribution of profit per order, indicating financial impact.
      
      <img width="1000" height="600" alt="order_profit_per_order_distribution" src="https://github.com/user-attachments/assets/fdcfe3a6-7c2a-4c4b-80dc-c11682a2df2b" />

        * The distribution appears to be multimodal or at least highly irregular, with significant density both around positive values and a notable presence of negative values. This indicates that the profit per order can vary widely, including instances of losses.
        
        * Crucially, the histogram clearly shows bars to the left of zero, representing orders where a loss was incurred. This is a key characteristic that many standard positive-only distributions (like Exponential, Weibull, Lognormal, Pareto) cannot directly model.
        
        * There seems to be a concentration of profits around certain positive values, and another concentration around zero or slightly negative, likely indicating typical profit margins versus breakeven or loss-making orders.
        
        * The profit/loss extends over a wide range, from significant losses to substantial profits.
        
        * This variable is a direct measure of the financial impact of each order, and thus, implicitly, the financial severity of any disruption associated with that order. The presence of negative values means that a simple single-distribution fit for the entire range is challenging. For robust modeling, it might require:
        
            * Modeling positive profits and negative losses separately.
            
            * Using distributions that can handle both positive and negative values (e.g., normal, logistic, or a mixture of distributions).
            
            * Applying transformations to make the data amenable to positive-only distributions, but then interpreting results back in the original scale.
                
    * inter_arrival_time_distribution.png: Histogram showing the distribution of inter-arrival times between orders.
      
      <img width="1000" height="600" alt="inter_arrival_time_distribution" src="https://github.com/user-attachments/assets/086dc9bd-d9bf-456c-894b-26cd33d1e33f" />
      
        * The distribution is highly skewed to the right, with a long tail. There's a high frequency of short inter-arrival times (many orders occurring relatively close to each other) and a decreasing frequency as inter-arrival time increases. This is a common pattern for arrival processes.

        * The highest frequency (mode) is very close to zero or at zero, indicating that a significant number of orders follow very quickly after the previous one for the same customer. (Note: Our fitting process for distributions like Pareto and Lognormal excluded 0 values as they are not defined for 0, and 0 in this context represented the first order for a customer rather than an actual interval).
        
        * While most inter-arrival times are short, there are instances of very long intervals between orders, forming the long tail.
        
        * This variable is crucial for understanding the frequency of events within the supply chain, which can be directly linked to the frequency of potential disruptions or the rate at which the supply chain is 'stressed'.

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
      From the distribution fitting comparison table, the Exponential distribution for 'Order Profit Per Order' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_order_profit_per_order_exponential" src="https://github.com/user-attachments/assets/bec1e8ef-e731-4ef2-804a-69dc4b6d4810" />

        * Parameters: loc = 0.08, scale = 53.853
        Similar to the inter-arrival time, loc represents a shift, and scale is related to the average value. A loc of approximately 0.08 indicates the distribution starts slightly above zero. The scale of 53.853 suggests an average profit per order of around this value, given that the fit was performed only on the positive profit values. As a reminder, Exponential distributions are defined for non-negative values. My fitting process considered only the positive values of 'Order Profit Per Order' for this distribution due to its mathematical definition.
        
        * KS p-value: 0
        An extremely low (effectively zero) p-value indicates a strong rejection of the null hypothesis that the data comes from an Exponential distribution. This suggests that the Exponential distribution does not provide a statistically good fit for the 'Order Profit Per Order' data, particularly when considering the entire range of profit (including negative values that were excluded for fitting this specific distribution).
        
        * AIC (Akaike Information Criterion): 1,451,586 and BIC (Bayesian Information Criterion): 1,451,606
        These values are quite high. When compared to the Weibull distribution (AIC: 1,443,710, BIC: 1,443,740) and Lognormal distribution (AIC: 1,449,940, BIC: 1,449,970) for 'Order Profit Per Order', the Exponential distribution has higher AIC and BIC values, indicating that it is a poorer fit compared to Weibull and Lognormal distributions for this variable (even when considering only the positive portion of the data for Lognormal and Pareto).
        
        * Looking at the "Order Profit Per Order - Exponential Fit" plot, you would likely observe that the fitted Exponential PDF (red line) does not closely align with the shape of the empirical data histogram (grey bars), especially given that the original 'Order Profit Per Order' data includes negative values (losses) that the Exponential distribution cannot directly model. The fit is only for positive profits.
        
        * Based on all metrics (extremely low KS p-value, and significantly higher AIC/BIC compared to better-fitting distributions like Weibull and Lognormal for positive profits), the Exponential distribution is not a suitable fit for modeling 'Order Profit Per Order', particularly considering the full range of profit/loss values. Its fit is statistically poor even for the positive subset of the data, and other distributions perform much better. For a comprehensive model of profit, a distribution or method that can account for both positive and negative values would be more appropriate.
            
    * Order Profit Per Order - Weibull Fit:
      From the distribution fitting comparison table, the Weibull distribution for 'Order Profit Per Order' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_order_profit_per_order_weibull" src="https://github.com/user-attachments/assets/45da32e8-37ba-4df0-9d66-14af95a0b883" />

        * Parameters: shape = 1.206, loc = 0.080, scale = 57.394
        The shape parameter (k) of 1.206 indicates that the rate of "failure" (or in this context, the probability density of a certain profit value) is slightly increasing over the range of profit values.
        
        * The loc parameter of 0.080 suggests a slight shift, indicating that the distribution effectively starts just above zero.
        The scale parameter (lambda) of 57.394 is related to the characteristic life, meaning that about 63.2% of the positive profit values fall below this point.
        As with other distributions that require non-negative inputs, this fit was performed only on the positive profit values from 'Order Profit Per Order'.
        
        * KS p-value: 1.399×10^−10
        While extremely low, this p-value is still a strong indication that the Weibull distribution statistically does not perfectly fit the 'Order Profit Per Order' data (considering only positive profits) according to the Kolmogorov-Smirnov test. The null hypothesis that the data comes from a Weibull distribution is rejected.
        
        * AIC (Akaike Information Criterion): 1,443,710 and BIC (Bayesian Information Criterion): 1,443,740
        These are the lowest AIC and BIC values among all the distributions fitted for 'Order Profit Per Order'. Lower AIC and BIC values suggest a better model fit. This indicates that, among the distributions tested, the Weibull distribution provides the relatively best fit for the positive values of 'Order Profit Per Order' according to these information criteria.
        
        * Looking at the "Order Profit Per Order - Weibull Fit" plot, you can visually assess how well the red line (fitted Weibull PDF) aligns with the grey bars (empirical data histogram for positive profits). You would likely observe that the Weibull curve provides a reasonable representation of the positive profit distribution, better than the Exponential.
        
        * The Weibull distribution provides the best fit for the positive values of 'Order Profit Per Order' among the distributions tested, as indicated by its lowest AIC and BIC values. However, it's crucial to remember that the fit was performed only on the positive subset of the data because the Weibull distribution, like Exponential and Pareto, is inherently defined for non-negative values. The extremely low KS p-value still suggests a statistically significant difference between the empirical data and the fitted distribution, which is common with large datasets where even minor deviations can lead to rejection. For a complete model of 'Order Profit Per Order' that includes negative values (losses), a different modeling approach or a more complex distribution capable of handling both positive and negative values would be required.
            
    * Order Profit Per Order - Lognormal Fit:
      From the distribution fitting comparison table, the Lognormal distribution for 'Order Profit Per Order' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_order_profit_per_order_lognormal" src="https://github.com/user-attachments/assets/1804a61d-6bbe-4407-b741-1e386a6c12fd" />

        * Parameters: shape = 0.739, loc = -7.734, scale = 47.688
        The shape parameter of 0.739 indicates a right-skewed distribution, which is characteristic of the Lognormal distribution.
        
        * The loc parameter, which represents a shift, is a negative value (-7.734). While the Lognormal distribution is defined for positive values, the scipy.stats implementation allows for a shift parameter. This negative loc means the distribution effectively starts before zero, even though the data used for fitting was filtered to include only positive profit values. This can sometimes occur when the fitted distribution is attempting to model a distribution that starts very close to zero or has a high density near the origin.
        The scale parameter of 47.688 is related to the median of the underlying normal distribution.
        As with other distributions that require non-negative inputs, this fit was performed only on the positive profit values from 'Order Profit Per Order'.
        
        * KS p-value: 1.338×10^−155
        This is an extremely low (effectively zero) p-value. This indicates a very strong rejection of the null hypothesis that the data comes from a Lognormal distribution. This suggests that the Lognormal distribution does not provide a statistically good fit for the 'Order Profit Per Order' data, even when considering only the positive portion.
        
        * AIC (Akaike Information Criterion): 1,449,940 and BIC (Bayesian Information Criterion): 1,449,970
        These values are lower than those for the Exponential and Pareto distributions, but higher than the Weibull distribution (AIC: 1,443,710, BIC: 1,443,740). This suggests that while Lognormal is better than Exponential and Pareto for positive profits, the Weibull distribution still provides a comparatively better fit according to these information criteria.
        
        * Looking at the "Order Profit Per Order - Lognormal Fit" plot, you would likely observe that the fitted Lognormal PDF (red line) might not perfectly capture the shape of the empirical data histogram (grey bars) for positive profits. While it may follow the general trend, discrepancies might be visible, particularly in the tails or peak of the distribution.
        
        * Based on the extremely low KS p-value, the Lognormal distribution does not provide a statistically good fit for the positive values of 'Order Profit Per Order'. While its AIC/BIC values are better than Exponential and Pareto, the Weibull distribution still outperformed it for this variable. It is important to remember that this analysis is based solely on the positive profit values, as the Lognormal distribution does not natively handle negative values. For a complete understanding of 'Order Profit Per Order' that includes both profits and losses, a different modeling approach would be necessary.
            
    * Order Profit Per Order - Pareto Fit:
      From the distribution fitting comparison table, the Pareto distribution for 'Order Profit Per Order' has the following characteristics:
      <img width="1000" height="600" alt="fit_plot_order_profit_per_order_pareto" src="https://github.com/user-attachments/assets/9a928e4f-0f30-46af-9b3b-aec0f0db7388" />


        * Parameters: shape = 39876410.26, loc = -2147483647.92, scale = 2147483648.0
        Similar to the Pareto fit for 'Inter-Arrival Time (Days)', the shape parameter (alpha) is extremely large (almost 40 million). This indicates an extremely steep decay, implying that values much larger than the minimum are highly unlikely.
        
        * The loc parameter is a very large negative value, and the scale parameter is an equally large positive value. These are indicative of a degenerate or poor fit, where the optimization algorithm struggled to find meaningful parameters that describe the data. It suggests that the fit is attempting to model a distribution that is almost a point mass, which is often observed when the actual data does not possess the long-tail characteristics that a Pareto distribution is designed to model.
        
        * As with other distributions that require non-negative inputs, this fit was performed only on the positive profit values from 'Order Profit Per Order'.
        
        * KS p-value: 0
        An extremely low (effectively zero) p-value indicates a very strong rejection of the null hypothesis that the data comes from a Pareto distribution. This suggests that the Pareto distribution does not provide a statistically good fit for the 'Order Profit Per Order' data, even when considering only the positive portion.
        
        * AIC (Akaike Information Criterion): 1,451,588 and BIC (Bayesian Information Criterion): 1,451,618
        These values are the highest among all the distributions fitted for 'Order Profit Per Order'. Higher AIC and BIC values indicate a poorer model fit. This confirms that the Pareto distribution is the worst fit among the tested distributions for the positive values of 'Order Profit Per Order'.
        
        * Looking at the "Order Profit Per Order - Pareto Fit" plot, you would likely observe that the fitted Pareto PDF (red line) would be a very steep, rapidly decaying curve that does not effectively capture the distribution of your empirical data (grey bars), especially given the extremely large shape parameter.
        
        * Based on all metrics (extremely low KS p-value, highly unusual and large parameter values, and the highest AIC/BIC), the Pareto distribution is the least suitable fit for modeling the 'Order Profit Per Order' data, even when considering only the positive values. Its fit is statistically very poor, and the estimated parameters are implausible for a typical long-tail phenomenon. For modeling 'Order Profit Per Order', especially considering both profits and losses, a more robust and appropriate distribution or modeling approach would be necessary.

* These plots help in visually assessing the goodness of fit.

## 4. Alternative Copula Check
Compare a Student-t copula with a Gaussian copula for modeling dependency between disruption variables.

copula_alt.ipynb and a "margin of fit" table (likely meaning a comparison of fit metrics for the marginal distributions and the copulas).

Copulas are used to model the dependence structure between random variables independently of their marginal distributions. This is crucial for multivariate risk modeling.

## 5.Risk-Dashboard Prototype                    

* CLICK ON IT :: http://localhost:8501/
* UPLOAD :: fitted_parameters.json

## 6. Copula selection on full dataset

### 1. Marginal Distribution Analysis for Lead Time
First, we need to find the best-fitting marginal distribution for the shipping_delay_days variable, as copula modeling requires calibrated marginals. shipping_delay_days can be negative (for early shipments), so distributions like Exponential and Weibull will be fitted to the positive values only, while a Normal distribution can handle the entire range.
<img width="795" height="152" alt="Screenshot 2025-08-27 at 3 14 51 PM" src="https://github.com/user-attachments/assets/c4b315fc-2a00-4488-a910-c90bf16c7c64" />
Based on the lowest AIC and BIC, the Normal distribution provides the best fit for shipping_delay_days. While the KS p-value is still very low (common with large datasets), the information criteria strongly favor the Normal distribution over the others.

### 2. Data Preparation for Copula Fitting
The three variables for our copula analysis are:

1. Severity: order_profit_per_order

2. Frequency: inter_arrival_time

3. Lead Time: shipping_delay_days

For copula modeling, which works with continuous distributions, we must transform these variables into pseudo-observations using their respective marginal CDFs. This transformation maps the data to the unit hypercube (values between 0 and 1) while preserving the dependence structure.

The logic of data preparation:
* inter_arrival_time and shipping_delay_days are used as-is for their respective marginal CDFs.

* order_profit_per_order contains negative values. A Weibull distribution was chosen as the best fit for the positive portion. For copula modeling, we need to handle the full distribution. A robust approach would use a mixture model, but for this task, a simplified approach involves using a single, best-fit distribution that can accommodate the data's range. The Weibull fit on the positive values is the best available, and we will use its CDF for transformation.

### 3. Copula Fitting & Diagnostic Analysis
We will fit both Gaussian and Student-t copulas to the pseudo-observations and evaluate their performance using the requested metrics.

* Rosenblatt/PIT Diagnostics
  
    The Probability Integral Transform (PIT) is a core diagnostic for checking the marginal fit. If the marginal distribution is a good fit, the transformed data (pseudo-observations) will be uniformly distributed between 0 and 1. A Q-Q plot against a theoretical uniform distribution reveals how well this holds. As seen in the generated Q-Q plot , the pseudo-observations from our chosen marginals show a reasonably linear relationship with the uniform distribution, indicating that the marginal fits are sufficient for copula modeling.

* Copula Comparison
  
    <img width="939" height="126" alt="Screenshot 2025-08-27 at 3 21 15 PM" src="https://github.com/user-attachments/assets/7e34dd0f-a44e-4861-b085-abc4c97c57eb" />


    * Tail Exceedance Rates (**lambda**): Tail dependence is a crucial metric for supply chain risk. It measures the probability of extreme events occurring simultaneously.

    * Empirical Tail Exceedance: By calculating the proportion of simultaneous extreme events in our data, we find an empirical tail dependence **lambda_emp** approx **0.28**.

    * Gaussian Copula: By definition, a Gaussian copula assumes no tail dependence, so its theoretical **lambda=0**. This is a poor match for our data.

    * Student-t Copula: The fitted Student-t copula has a theoretical tail dependence of **lambda_t** approx **0.31**.

This result (**lambda_t** approx **0.31**) is within **10%** of our empirical observation (**lambda_emp** approx **0.28**), satisfying a key project requirement.

### 4. Final Choice and Deliverables
Based on the analysis, the Student-t copula is the clearl good one. It provides a better statistical fit (lower AIC/BIC and higher out-of-sample log-likelihood) and, most importantly, accurately captures the tail dependence observed in the data. This is critical for a supply chain risk model, as it means the model can correctly simulate scenarios where severe disruptions are more likely to coincide with long lead times.

The final deliverables are:

1. fitted_parameters.json update:check (/outputs/fitted_parameters_updated.json)

The simulation configuration file will be updated to use the Student-t copula. The new entry will look like this:

```

{
  "copula": {
    "type": "student_t",
    "variables": ["order_profit_per_order", "shipping_delay_days", "inter_arrival_time"],
    "parameters": {
      "degrees_of_freedom": 5.4,
      "correlation_matrix": [
        [1.0, -0.41, -0.05],
        [-0.41, 1.0, 0.08],
        [-0.05, 0.08, 1.0]
      ]
    }
  }
}

```

Note: The degrees_of_freedom (df) value is a key parameter that determines the extent of tail dependence. A lower value indicates stronger dependence.

2. copula_choice.md document: check /docs/ directory.

3. Dashboard Note:
A toggle note can be added to the simulation dashboard interface: model: t-copula. This ensures that users are aware of the underlying dependency structure driving the simulation results.

## 7. Baseline Policies and Experiment Design

Here our goal is to set up a framework for evaluating simple inventory control policies before moving on to more complex, simulation-based strategies.
Baseline Policies and Experiment Design
Here is a design for your baseline policies and the structure for an experiment sheet. The goal is to set up a framework for evaluating simple inventory control policies before moving on to more complex, simulation-based strategies.

### 1. Baseline Inventory Policies
#### (a). (s, S) Policy:
* The (s,S) inventory policy is a classic and widely used control strategy. It's a simple, robust that is well-suited as a baseline for comparison.

* This is a continuous-review inventory policy where **s** is the reorder point and **S** is the order-up-to level.

* When the inventory position (on-hand inventory + on-order inventory) drops to **s** or below, an order is placed.

* The size of the order is such that the inventory position returns to **S**. The quantity is calculated as **S** - inventory_position.

* Why It's a Good Baseline?
  The (s,S) policy is simple to implement and understand. Its performance depends on only two parameters, making it easy to test and calibrate. It provides a solid benchmark against which more sophisticated, data-driven policies can be measured.

#### (b). Myopic Heuristics
* A "myopic heuristics policy" refers to decision-making rules (heuristics) that prioritize immediate or short-term costs and benefits over longer-term consequences
* It is a rule-based policy that makes decisions based only on immediate, short-term information, without considering future impacts. They are useful for their simplicity and as a lower bound for performance.

Example: "Order up to average demand"

At a fixed review period (e.g., every 30 days), calculate the average demand over the last X days. Place an order to bring your inventory up to that level.

* Myopic heuristics are computationally cheap and serve as a "what if we just used a simple rule" benchmark. They highlight the value of more sophisticated inventory models.

* REFERENCE : https://link.springer.com/article/10.1007/s10479-021-04441-1

### 2. Experiment Sheet Design
To systematically evaluate the (s,S) policy, we need a structured experiment sheet. This sheet will serve as a single source of truth for all simulation runs, ensuring reproducibility and clear tracking of results.

| Experiment ID | Policy | Parameter Grid | Metrics | Observations |
|---|---|---|---|---|
| B-001 | (s,S) | s: [10, 20, 30] S: [50, 75, 100]|Total Cost, Service Level, Fill Rate| Initial run to find a basic working range |
| B-002 | (s,S) | s: [50, 70, 90] S: [100, 150, 200]| Total Cost, Service Level, Fill Rate | Total Cost	Testing a higher demand scenario |
| B-003 | Myopic Heuristic | (Based on a simple rule) | Total Cost, Service Level, Fill Rate | Compare a rule-based policy to (s,S) |

#### Parameter Grids
The parameter grid defines the specific values to be tested for each policy. A systematic grid search is a standard way to find a good range for **s** and **S**.

**s (Reorder Point)**: This parameter is typically related to the lead time demand. A simple approach is to set **s** equal to the **average lead time demand plus a safety stock**. we can start with a grid around our average lead time demand and then expand it.

**S (Order-up-to Level)**: This is often a function of **s** and the reorder quantity. A common practice is to set **S = s + Q**, where **Q** is your lot size. Alternatively, we can test a range of **S** values independently.
* **simulation_model.py** updated to **updated_simulation_model.py** include these policies and a loop to iterate through the parameter grid.

### 3. Experiments:
  
#### (s,S) Policy Experiments

| Exp No. | Policy | Parameters          | Avg Total Cost | Std Dev Cost |
|---------|--------|---------------------|----------------|--------------|
| 0       | sS     | {'s': 10, 'S': 50} | 11754.372      | 245.295119   |
| 1       | sS     | {'s': 20, 'S': 70} | 16433.131      | 316.431322   |
| 2       | sS     | {'s': 30, 'S': 100} | 23060.791      | 375.186345   |



#### Myopic Heuristic Experiments

| Exp No. | policy | parameters | avg_total_cost | std_dev_cost |
|---------|--------|---------------------|----------------|--------------|
| 0 | myopic | {'target_days': 10} | 27303.048 | 548.657193 |
| 1 | myopic | {'target_days': 20} | 27307.310 | 547.859916 |
| 2 | myopic | {'target_days': 30} | 27311.991 | 534.231750 |

#### Based on the simulation outputs:

* The (s,S) policy shows a clear and significant performance difference across the tested parameters.
* The {'s': 10, 'S': 50} configuration yielded the lowest average total cost at $11,754.37, with the lowest standard deviation, indicating a more stable cost outcome. (Best Performance)
* As the reorder point (s) and order-up-to level (S) increase, the total cost of the policy also rises significantly. For example, the cost for s=30, S=100 is $23,060.79, nearly double the cost of the best-performing policy. This suggests that the higher holding costs associated with larger inventory levels outweigh the benefits of reduced shortages in these scenarios.
* The results confirm that the (s,S) policy is sensitive to its parameter settings and a well-tuned policy can be very effective.
* Whereas the myopic heuristic performed consistently and poorly across all tested parameters.
* The average total costs for all three configurations were consistently high, ranging from $27,303.05 to $27,311.99. There is very little variation in cost among the different targets.(High and Stable Costs)
* The myopic policy's average costs are more than double the cost of the best-performing (s,S) policy. This is because a simple, rule-based policy that doesn't strategically account for demand variability, lead time, or safety stock leads to frequent stockouts or excessive inventory, resulting in high shortage or holding costs.(Poor Performance) 

#### Conclusion: 
* The results clearly demonstrate that the (s,S) policy is a far more effective baseline for inventory control than the myopic heuristic.
* The best (s,S) policy achieved an average total cost of $11,754.37, which is less than half the cost of the best myopic policy ($27,303.05).
* This significant difference highlights the value of a continuous-review policy that intelligently manages reorder points and inventory levels, as opposed to a simple, short-sighted heuristic.
* The (s,S) policy serves as a strong and sensible benchmark for future policy comparisons.
