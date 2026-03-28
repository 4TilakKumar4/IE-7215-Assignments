"""
PROBLEM 5
APPROACH:
    - The data contains daily call counts for 8 one-hour intervals (8AM-4PM).
    - MLE for a Poisson rate over each interval: λ̂_k = mean count across days.
    - Arrivals within each interval are generated as Poisson(λ̂_k).
    - Simulation runs multiple replications and reports arrivals per interval.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def estimate_rates(filepath):
    df = pd.read_csv(filepath)
    return df.mean(), df.columns.tolist()


def simulate_arrivals(rates, replications=1000):
    results = np.zeros((replications, len(rates)))
    for r in range(replications):
        for k, lam in enumerate(rates):
            results[r, k] = np.random.poisson(lam)
    return results


def print_results(rates, intervals, sim_results):
    print(f"\n\nEstimated arrival rates (calls/hour):\n")
    print(f"{'Interval':<14} {'λ̂_k (Estimated)':>18} {'Sim Mean':>10} {'Sim Std':>10}")
    for k, (interval, rate) in enumerate(zip(intervals, rates)):
        sim_mean = sim_results[:, k].mean()
        sim_std  = sim_results[:, k].std()
        print(f"{interval:<14} {rate:>18.2f} {sim_mean:>10.2f} {sim_std:>10.2f}")

    print(f"\nTotal expected arrivals per day : {rates.sum():.1f}")
    print(f"Simulated mean total per day    : {sim_results.sum(axis=1).mean():.1f}")
    print(f"Simulated std total per day     : {sim_results.sum(axis=1).std():.1f}")
    print("\n")


if __name__ == "__main__":
    np.random.seed(42)
 
    data_path = Path(__file__).parent / "Sources" / "CallCounts.csv"
    rates, intervals = estimate_rates(data_path)
    sim_results = simulate_arrivals(rates, replications=1000)
    print_results(rates, intervals, sim_results)