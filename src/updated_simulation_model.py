# src/simulation_model.py => updated_simulation_model.py

import json
import numpy as np
from scipy import stats
from scipy.stats import invgamma # Required for student_t if implemented
import pandas as pd
import sys
import os

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
        dist_map = {
            "expon": stats.expon,
            "weibull_min": stats.weibull_min,
            "lognorm": stats.lognorm,
            "pareto": stats.pareto,
            "norm": stats.norm
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

        samples = dist_func.rvs(*params, size=num_samples, random_state=self.rng)

        if variable_name in ['inter_arrival_time', 'shipping_delay_days']:
            samples[samples < 0] = 0

        return samples

    def _generate_dependent_samples_gaussian(self, num_samples):
        """
        Generates dependent samples using a Gaussian copula.
        Assumes variables in copula section of JSON are normally distributed.
        """
        copula_info = self.params.get('copula')
        if not copula_info or copula_info['type'] != 'gaussian':
            return None

        variables = copula_info['variables']
        corr_matrix = np.array(copula_info['parameters']['correlation_matrix'])
        mean = np.zeros(len(variables))
        correlated_normals = self.rng.multivariate_normal(mean, corr_matrix, size=num_samples)
        dependent_samples = {}

        for i, var_name in enumerate(variables):
            pseudo_obs = stats.norm.cdf(correlated_normals[:, i])
            var_params = self.params.get(var_name)
            if not var_params:
                raise ValueError(f"Marginal parameters for '{var_name}' not found for copula.")
            dist_func = self._get_dist_func(var_params['distribution'])
            params = var_params['parameters']
            dependent_samples[var_name] = dist_func.ppf(pseudo_obs, *params)
            if var_name in ['shipping_delay_days', 'order_profit_per_order']:
                dependent_samples[var_name][dependent_samples[var_name] < 0] = 0

        return pd.DataFrame(dependent_samples)
    
    def _generate_dependent_samples_student_t(self, num_samples):
        """
        Generates dependent samples using a Student-t copula.
        """
        copula_info = self.params.get('copula')
        if not copula_info or copula_info['type'] != 'student_t':
            return None

        variables = copula_info['variables']
        corr_matrix = np.array(copula_info['parameters']['correlation_matrix'])
        df = copula_info['parameters']['degrees_of_freedom']

        # Generate correlated t-distributed variates
        # This requires a more complex method than scipy's basic tools.
        # For a simplified, illustrative implementation:
        try:
            from rpy2.robjects.packages import importr
            from rpy2.robjects import pandas2ri
            pandas2ri.activate()
            copula = importr('copula')
            t_cop = copula.tCopula(param=pandas2ri.py2rpy(pd.DataFrame(corr_matrix)), dim=len(variables), df=df)
            pseudo_obs = np.array(copula.rCopula(num_samples, t_cop))
        except ImportError:
            print("Warning: rpy2 is not installed. Student-t copula simulation will be skipped.")
            print("Falling back to independent sampling for this prototype.")
            return None

        dependent_samples = {}
        for i, var_name in enumerate(variables):
            var_params = self.params.get(var_name)
            if not var_params:
                raise ValueError(f"Marginal parameters for '{var_name}' not found for copula.")
            dist_func = self._get_dist_func(var_params['distribution'])
            params = var_params['parameters']
            dependent_samples[var_name] = dist_func.ppf(pseudo_obs[:, i], *params)
            if var_name in ['shipping_delay_days', 'order_profit_per_order']:
                dependent_samples[var_name][dependent_samples[var_name] < 0] = 0
                
        return pd.DataFrame(dependent_samples)

    def run_simulation(self, num_simulations, simulation_period_days=365):
        """
        Runs the Monte Carlo simulation for supply chain disruptions.
        """
        all_simulated_total_costs = []
        all_simulated_num_disruptions = []
        all_simulated_average_delay = []

        copula_defined = 'copula' in self.params and self.params['copula']['type'] in ['gaussian', 'student_t']

        for _ in range(num_simulations):
            inter_arrival_times = self._generate_marginal_samples('inter_arrival_time', num_simulations * 2)
            cumulative_times = np.cumsum(inter_arrival_times)
            num_disruptions_in_period = np.sum(cumulative_times < simulation_period_days)

            if num_disruptions_in_period == 0:
                all_simulated_total_costs.append(0)
                all_simulated_num_disruptions.append(0)
                all_simulated_average_delay.append(0)
                continue

            simulated_profit_per_order = []
            simulated_shipping_delay_days = []

            if copula_defined:
                copula_type = self.params['copula']['type']
                if copula_type == 'gaussian':
                    dependent_samples_df = self._generate_dependent_samples_gaussian(num_disruptions_in_period)
                elif copula_type == 'student_t':
                    dependent_samples_df = self._generate_dependent_samples_student_t(num_disruptions_in_period)
                
                if dependent_samples_df is not None:
                    simulated_profit_per_order = dependent_samples_df['order_profit_per_order'].values
                    simulated_shipping_delay_days = dependent_samples_df['shipping_delay_days'].values
                else:
                    simulated_profit_per_order = self._generate_marginal_samples('order_profit_per_order', num_disruptions_in_period)
                    simulated_shipping_delay_days = self._generate_marginal_samples('shipping_delay_days', num_disruptions_in_period)
            else:
                simulated_profit_per_order = self._generate_marginal_samples('order_profit_per_order', num_disruptions_in_period)
                simulated_shipping_delay_days = self._generate_marginal_samples('shipping_delay_days', num_disruptions_in_period)

            simulated_costs = np.where(simulated_profit_per_order < 0, -simulated_profit_per_order, 0)
            total_simulated_cost = np.sum(simulated_costs)
            average_simulated_delay = np.mean(simulated_shipping_delay_days) if num_disruptions_in_period > 0 else 0

            all_simulated_total_costs.append(total_simulated_cost)
            all_simulated_num_disruptions.append(num_disruptions_in_period)
            all_simulated_average_delay.append(average_simulated_delay)

        avg_total_cost = np.mean(all_simulated_total_costs)
        avg_num_disruptions = np.mean(all_simulated_num_disruptions)
        avg_average_delay = np.mean(all_simulated_average_delay)

        scri = (avg_total_cost / 1000) + (avg_average_delay * 10) + (avg_num_disruptions * 5)

        return {
            'avg_total_cost_per_period': avg_total_cost,
            'avg_num_disruptions_per_period': avg_num_disruptions,
            'avg_average_delay_per_disruption': avg_average_delay,
            'simulated_total_costs': all_simulated_total_costs,
            'supply_chain_risk_index': scri
        }

# =============================================================================
# New Code for Inventory Policies and Experimentation
# =============================================================================
class InventorySimulator:
    def __init__(self, demand_dist, lead_time_dist, holding_cost=1.0, shortage_cost=10.0, order_cost=50.0):
        self.demand_dist = demand_dist
        self.lead_time_dist = lead_time_dist
        self.holding_cost = holding_cost
        self.shortage_cost = shortage_cost
        self.order_cost = order_cost
        self.rng = np.random.default_rng()

    def _run_single_simulation(self, policy, policy_params, sim_period_days, initial_inventory=100):
        """
        Runs a single inventory simulation run for a given policy and parameters.
        """
        inventory_level = initial_inventory
        inventory_position = initial_inventory
        total_holding_cost = 0
        total_shortage_cost = 0
        total_ordering_cost = 0
        
        # Track pending orders
        pending_orders = {}

        for day in range(sim_period_days):
            # 1. Process incoming orders
            if day in pending_orders:
                inventory_level += pending_orders[day]
                del pending_orders[day]

            # 2. Update inventory costs
            if inventory_level > 0:
                total_holding_cost += inventory_level * self.holding_cost
            else:
                total_shortage_cost += abs(inventory_level) * self.shortage_cost

            # 3. Simulate demand
            daily_demand = max(0, int(self.demand_dist.rvs())) # Ensure non-negative and integer demand
            
            # 4. Fulfill demand
            inventory_level -= daily_demand
            inventory_position = inventory_level + sum(pending_orders.values())

            # 5. Make a decision based on the policy
            order_qty = 0
            if policy == 'sS':
                s, S = policy_params['s'], policy_params['S']
                if inventory_position <= s:
                    order_qty = S - inventory_position
            elif policy == 'myopic':
                # Myopic: order up to average demand of a period (e.g., 30 days)
                # This is a simplified model. A more complex one would track historical demand.
                # For this prototype, we'll assume a fixed average demand target.
                avg_daily_demand = self.demand_dist.mean()
                if inventory_position < avg_daily_demand:
                    order_qty = avg_daily_demand * 30 # Order up to 30 days of average demand
            
            if order_qty > 0:
                total_ordering_cost += self.order_cost
                # Simulate lead time using the distribution
                lead_time = max(1, int(self.lead_time_dist.rvs()))
                arrival_day = day + lead_time
                pending_orders[arrival_day] = pending_orders.get(arrival_day, 0) + order_qty
        
        total_cost = total_holding_cost + total_shortage_cost + total_ordering_cost
        return total_cost, total_holding_cost, total_shortage_cost, total_ordering_cost

    def run_experiment(self, policy_name, parameter_grid, num_simulations, sim_period_days=365):
        """
        Runs a series of simulations across a parameter grid for a given policy.
        """
        results = []
        for params in parameter_grid:
            costs = []
            for _ in range(num_sims):
                cost, _, _, _ = self._run_single_simulation(policy_name, params, sim_period_days)
                costs.append(cost)
            
            avg_cost = np.mean(costs)
            std_dev = np.std(costs)
            results.append({
                'policy': policy_name,
                'parameters': params,
                'avg_total_cost': avg_cost,
                'std_dev_cost': std_dev
            })
        
        return pd.DataFrame(results)

# =============================================================================
# Example Usage: Connecting the two simulators
# =============================================================================
if __name__ == '__main__':
    # we've already done the distribution fitting and saved the parameters.
    # update the path to **updated_fitted_parameters.json** JSON file.
    params_path = "/kaggle/input/fitted-parameter/fitted_parameters_updated.json"
    
    # 1. Initialize the Supply Chain Simulator to get fitted distributions
    supply_chain_sim = SupplyChainSimulator(params_path)

    # 2. Get the fitted distributions for demand and lead time (from your analysis)
    # For this prototype, we use the `shipping_delay_days` as lead time.
    # We will assume a demand distribution for this example. A full project would fit it from data.
    # Let's say demand is normally distributed with a mean of 5 and std dev of 2.
    demand_dist = stats.norm(loc=5, scale=2)
    
    # Get the fitted distribution for lead time from the JSON
    lead_time_params = supply_chain_sim.params.get('shipping_delay_days', {})
    if lead_time_params:
        lead_time_dist = supply_chain_sim._get_dist_func(lead_time_params['distribution'])(*lead_time_params['parameters'])
    else:
        lead_time_dist = stats.norm(loc=3, scale=1) # Fallback if not in JSON

    # 3. Initialize the Inventory Simulator
    inv_sim = InventorySimulator(demand_dist, lead_time_dist)
    
    # 4. Define parameter grids for experimentation
    sS_parameter_grid = [
        {'s': 10, 'S': 50},
        {'s': 20, 'S': 70},
        {'s': 30, 'S': 100},
    ]

    myopic_parameter_grid = [
        {'target_days': 10},
        {'target_days': 20},
        {'target_days': 30},
    ]

    num_sims = 1000
    sim_period = 365

    # 5. Run the experiments
    print("\n--- Running (s,S) Policy Experiments ---")
    sS_results = inv_sim.run_experiment('sS', sS_parameter_grid, num_sims, sim_period)
    print(sS_results)

    print("\n--- Running Myopic Heuristic Experiments ---")
    myopic_results = inv_sim.run_experiment('myopic', myopic_parameter_grid, num_sims, sim_period)
    print(myopic_results)
    
    # Note: The myopic policy in this prototype is simplified. A full implementation need to be more sophisticated to show its true performance.
