# src/simulation_model.py

import json
import numpy as np
from scipy import stats
from scipy.stats import invgamma # Required for student_t if implemented
import pandas as pd

class SupplyChainSimulator:
    def __init__(self, params_filepath):
        """
        Initializes the simulator with distribution parameters loaded from a JSON file.
        """
        self.params = self._load_parameters(params_filepath)
        self.rng = np.random.default_rng() # For reproducible random numbers

    def _load_parameters(self, filepath):
        """Loads distribution and copula parameters from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Parameters file not found at: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from: {filepath}")

    def _get_dist_func(self, dist_name):
        """Returns the scipy.stats distribution function."""
        # Mapping distribution names to scipy.stats objects
        dist_map = {
            "expon": stats.expon,
            "weibull_min": stats.weibull_min,
            "lognorm": stats.lognorm,
            "pareto": stats.pareto,
            "norm": stats.norm # Added for potential future use or if a normal fit is desired
        }
        if dist_name not in dist_map:
            raise ValueError(f"Unsupported distribution: {dist_name}")
        return dist_map[dist_name]

    def _generate_marginal_samples(self, variable_name, num_samples):
        """
        Generates random samples for a given variable based on its fitted distribution.
        """
        var_params = self.params.get(variable_name)
        if not var_params:
            raise ValueError(f"Parameters for '{variable_name}' not found in JSON.")

        dist_name = var_params['distribution']
        params = var_params['parameters']
        dist_func = self._get_dist_func(dist_name)

        # Generate samples using the rvs method
        samples = dist_func.rvs(*params, size=num_samples, random_state=self.rng)

        # Ensure non-negativity for time and profit (as per fitting)
        if variable_name in ['inter_arrival_time', 'shipping_delay_days']:
            samples[samples < 0] = 0 # Replace negative times with 0

        # For 'order_profit_per_order', if the original data had negatives,
        # but the fitted distribution (e.g., Weibull) only covers positives,
        # the simulation will only generate positive values.
        # A more complex model might handle negative profits separately or with a different distribution.

        return samples

    def _generate_dependent_samples_gaussian(self, num_samples):
        """
        Generates dependent samples using a Gaussian copula.
        Assumes variables in copula section of JSON are normally distributed.
        """
        copula_info = self.params.get('copula')
        if not copula_info or copula_info['type'] != 'gaussian':
            return None # Or raise an error if copula is mandatory

        variables = copula_info['variables']
        corr_matrix = np.array(copula_info['parameters']['correlation_matrix'])

        # Generate correlated standard normal variates
        mean = np.zeros(len(variables))
        correlated_normals = self.rng.multivariate_normal(mean, corr_matrix, size=num_samples)

        dependent_samples = {}
        for i, var_name in enumerate(variables):
            # Transform standard normal variates to uniform [0,1] pseudo-observations
            pseudo_obs = stats.norm.cdf(correlated_normals[:, i])

            # Transform pseudo-observations back to original marginal distribution scale
            var_params = self.params.get(var_name)
            if not var_params:
                raise ValueError(f"Marginal parameters for '{var_name}' not found for copula.")
            dist_func = self._get_dist_func(var_params['distribution'])
            params = var_params['parameters']

            # Use inverse CDF (PPF) to transform uniform samples to original scale
            dependent_samples[var_name] = dist_func.ppf(pseudo_obs, *params)

            # Ensure non-negativity if applicable (e.g., shipping_delay_days, profit)
            if var_name in ['shipping_delay_days', 'order_profit_per_order']:
                dependent_samples[var_name][dependent_samples[var_name] < 0] = 0


        return pd.DataFrame(dependent_samples)

    # Placeholder for Student-t copula if you implement it after analysis
    # def _generate_dependent_samples_student_t(self, num_samples):
    #     copula_info = self.params.get('copula')
    #     if not copula_info or copula_info['type'] != 'student_t':
    #         return None
    #
    #     variables = copula_info['variables']
    #     corr_matrix = np.array(copula_info['parameters']['correlation_matrix'])
    #     df = copula_info['parameters']['df'] # Degrees of freedom
    #
    #     # Generate correlated t-distributed variates
    #     # This requires more complex sampling or a dedicated copula library
    #     # For manual implementation, you'd typically use inverse_gamma for mixing variable
    #     # or a specialized algorithm.
    #     # Example (simplified conceptual approach, not directly implementable with scipy out-of-box for multivariate t):
    #     # w = invgamma.rvs(df/2, scale=df/2, size=num_samples) # Mixing variable
    #     # Z = self.rng.multivariate_normal(np.zeros(len(variables)), corr_matrix, size=num_samples)
    #     # correlated_ts = Z / np.sqrt(w[:, np.newaxis])
    #
    #     # Transform t-variates to uniform [0,1] pseudo-observations using t-CDF
    #     # pseudo_obs = stats.t.cdf(correlated_ts, df=df)
    #
    #     # Then transform back to marginals using PPF as in Gaussian case
    #     # This part will be similar to the Gaussian case.
    #     print("Student-t copula simulation not fully implemented in this prototype.")
    #     return None


    def run_simulation(self, num_simulations, simulation_period_days=365):
        """
        Runs the Monte Carlo simulation for supply chain disruptions.

        Args:
            num_simulations (int): Number of simulation runs.
            simulation_period_days (int): The total duration of one simulation run in days (e.g., 365 for a year).

        Returns:
            dict: Simulation results including total cost, SCRI, and other metrics.
        """
        all_simulated_total_costs = []
        all_simulated_num_disruptions = []
        all_simulated_average_delay = []

        # If a copula is defined, we'll generate dependent variables together
        copula_defined = 'copula' in self.params and self.params['copula']['type'] in ['gaussian', 'student_t']

        for _ in range(num_simulations):
            # 1. Simulate Inter-Arrival Times to get number of events in the period
            inter_arrival_times = self._generate_marginal_samples('inter_arrival_time', num_simulations * 2) # Generate more than needed
            cumulative_times = np.cumsum(inter_arrival_times)
            num_disruptions_in_period = np.sum(cumulative_times < simulation_period_days)

            if num_disruptions_in_period == 0:
                # If no disruptions simulated in this period, assign 0 cost and delay
                all_simulated_total_costs.append(0)
                all_simulated_num_disruptions.append(0)
                all_simulated_average_delay.append(0)
                continue

            simulated_profit_per_order = []
            simulated_shipping_delay_days = []

            if copula_defined:
                dependent_samples_df = self._generate_dependent_samples_gaussian(num_disruptions_in_period) # Use the chosen copula
                if dependent_samples_df is not None:
                    # Filter for cases where profit_per_order might be negative based on model (if model handled it)
                    # For simplicity, if Weibull/Lognormal are used for profit, it will be positive anyway.
                    simulated_profit_per_order = dependent_samples_df['order_profit_per_order'].values
                    simulated_shipping_delay_days = dependent_samples_df['shipping_delay_days'].values
                else:
                    # Fallback to independent if copula generation fails or not implemented
                    simulated_profit_per_order = self._generate_marginal_samples('order_profit_per_order', num_disruptions_in_period)
                    simulated_shipping_delay_days = self._generate_marginal_samples('shipping_delay_days', num_disruptions_in_period)
            else:
                # 2. Simulate other independent variables for each disruption
                simulated_profit_per_order = self._generate_marginal_samples('order_profit_per_order', num_disruptions_in_period)
                simulated_shipping_delay_days = self._generate_marginal_samples('shipping_delay_days', num_disruptions_in_period)

            # Convert simulated profit to cost (loss) for risk calculation
            # Assuming negative profit is a cost, positive profit is revenue
            # For risk, we focus on the "cost of disruption" which is usually a loss.
            # If profit is positive, we count 0 cost of disruption. If profit is negative, it's a direct cost.
            # A more refined model might consider opportunity cost or other cost factors.
            simulated_costs = np.where(simulated_profit_per_order < 0, -simulated_profit_per_order, 0)

            total_simulated_cost = np.sum(simulated_costs)
            average_simulated_delay = np.mean(simulated_shipping_delay_days) if num_disruptions_in_period > 0 else 0

            all_simulated_total_costs.append(total_simulated_cost)
            all_simulated_num_disruptions.append(num_disruptions_in_period)
            all_simulated_average_delay.append(average_simulated_delay)

        # Calculate overall simulation metrics
        avg_total_cost = np.mean(all_simulated_total_costs)
        avg_num_disruptions = np.mean(all_simulated_num_disruptions)
        avg_average_delay = np.mean(all_simulated_average_delay)

        # Define a simple Supply Chain Risk Index (SCRI)
        # This is a placeholder formula. You should define what SCRI means for your project.
        # Example: Weighted sum of average cost and average delay
        # Higher cost and higher delay lead to higher risk
        # Normalization might be needed if values are on very different scales
        # For simplicity, let's say: (Avg Cost / 1000) + (Avg Delay * 10) + (Avg Num Disruptions * 5)
        # Adjust weights based on business impact and scale of values
        scri = (avg_total_cost / 1000) + (avg_average_delay * 10) + (avg_num_disruptions * 5)

        return {
            'avg_total_cost_per_period': avg_total_cost,
            'avg_num_disruptions_per_period': avg_num_disruptions,
            'avg_average_delay_per_disruption': avg_average_delay,
            'simulated_total_costs': all_simulated_total_costs, # For plotting distribution of total costs
            'supply_chain_risk_index': scri
        }

if __name__ == '__main__':
    # Example usage:
    # Ensure you have a 'fitted_parameters.json' in the 'data/' directory
    # or specify its correct path.
    try:
        simulator = SupplyChainSimulator('/Users/manishkumarkumawat/Desktop/Supply chain management/code/fitted_parameters.json') # Adjust path as needed for local testing
        num_sims = 10000
        sim_results = simulator.run_simulation(num_sims)

        print("\n--- Simulation Results ---")
        print(f"Average Total Cost per Period: {sim_results['avg_total_cost_per_period']:.2f}")
        print(f"Average Number of Disruptions per Period: {sim_results['avg_num_disruptions_per_period']:.2f}")
        print(f"Average Delay per Disruption: {sim_results['avg_average_delay_per_disruption']:.2f} days")
        print(f"Calculated Supply Chain Risk Index (SCRI): {sim_results['supply_chain_risk_index']:.2f}")

        # You can plot the distribution of simulated total costs
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(10, 6))
        sns.histplot(sim_results['simulated_total_costs'], bins=50, kde=True)
        plt.title('Distribution of Simulated Total Disruption Costs per Period')
        plt.xlabel('Total Disruption Cost ($)')
        plt.ylabel('Frequency')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()

    except Exception as e:
        print(f"An error occurred during simulation: {e}")
