# Copula Selection for Supply Chain Risk Modeling
To select the most appropriate copula model for simulating dependencies between key supply chain disruption variables.

Based on a rigorous comparison using statistical metrics and domain relevance, the Student-t copula is selected as the superior model. It outperforms the Gaussian copula by providing a better fit to the data and, critically, by accurately capturing the tail dependence observed in extreme events.

## Analysis & Rationale
### 1. Key Variables and Marginal Distributions
The analysis focused on three crucial disruption variables:

* Severity: order_profit_per_order

* Frequency: inter_arrival_time

* Lead Time: shipping_delay_days

Each variable's marginal distribution was calibrated prior to copula fitting. The best-fitting marginal distributions chosen were Weibull for inter_arrival_time, Weibull for the positive portion of order_profit_per_order, and Normal for shipping_delay_days.

### 2. Gaussian vs. Student-t Copula Comparison
A comparison of the two candidate copula models yielded the following results:

<img width="580" height="149" alt="Screenshot 2025-08-27 at 3 57 04 PM" src="https://github.com/user-attachments/assets/ea74d083-73bc-4e62-87b2-5e8b6e8c665d" />

* Goodness-of-Fit: The Student-t copula demonstrated a significantly better fit, as evidenced by its lower AIC and BIC values and a higher out-of-sample log-likelihood.

* Kendall's Tau: Both models provided a close match to the empirical correlation, indicating they both correctly model the overall monotonic relationship between the variables.

### 3. Capturing Tail Dependence: A Critical Distinction
The key difference between the two models lies in their ability to capture tail dependence, which is the probability of extreme events occurring simultaneously.

* The Gaussian copula assumes no tail dependence (λ=0). This is a poor assumption for supply chain risks, where severe disruptions (e.g., large financial losses) are often correlated with long delays.

* The Student-t copula has a key parameter, the degrees of freedom, which allows it to model tail dependence. The fitted model yielded a tail dependence coefficient of **λ_t≈0.31**.

This theoretical value closely matches the empirically observed tail exceedance rate (**λ_emp≈0.28**), satisfying the project's exit check with a difference of only **10.7%**.

## Conclusion
The Student-t copula is the appropriate choice for this risk simulation model. Its superior fit and, most importantly, its ability to accurately represent the co-occurrence of extreme events ensures that the simulations are more realistic and the calculated risk metrics, such as the Supply Chain Risk Index (SCRI), are more reliable for proactive risk management.
