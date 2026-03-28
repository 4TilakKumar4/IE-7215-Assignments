"""
PROBLEM 4.c: Coverage Simulation for Confidence Intervals
APPROACH:
    (a) Asymptotic CI: The MLE for Poisson is λ̂ = X̄. By asymptotic normality
        of the MLE and Fisher Information I(λ) = 1/λ, the CI is:
            λ̂ ± z_{α/2} * sqrt(λ̂ / n)
    (b) Parametric Bootstrap CI: Using λ̂ = X̄ as the assumed true parameter,
        generate B bootstrap samples from Poisson(λ̂), compute the bootstrap
        MLE for each, and take empirical (α/2) and (1 - α/2) percentiles.
    (c) Coverage Simulation: For n ∈ {5, 10, 100, 1000}, run 1000 replications.
        In each, generate data from Poisson(λ_c = 1), construct both CIs, and
        check containment. Coverage = fraction of CIs containing λ_c.
"""

import numpy as np
from scipy import stats


def compute_asymptotic_ci(x_bar, n, z_crit):
    se = np.sqrt(x_bar / n)
    return x_bar - z_crit * se, x_bar + z_crit * se


def compute_bootstrap_ci(x_bar, n, alpha, B):
    if x_bar == 0:
        return 0.0, 0.0
    boot_means = np.random.poisson(x_bar, size=(B, n)).mean(axis=1)
    return np.percentile(boot_means, [alpha / 2 * 100, (1 - alpha / 2) * 100])


def run_coverage_simulation(n_values, lambda_true=1.0, alpha=0.05, replications=1000, B=1000):
    z_crit = stats.norm.ppf(1 - alpha / 2)
    results = {}

    for n in n_values:
        asy_hits, boot_hits = 0, 0

        for _ in range(replications):
            data = np.random.poisson(lambda_true, size=n)
            x_bar = data.mean()

            lower_asy, upper_asy = compute_asymptotic_ci(x_bar, n, z_crit)
            if lower_asy <= lambda_true <= upper_asy:
                asy_hits += 1

            lower_boot, upper_boot = compute_bootstrap_ci(x_bar, n, alpha, B)
            if lower_boot <= lambda_true <= upper_boot:
                boot_hits += 1

        results[n] = {
            "asymptotic": asy_hits / replications,
            "bootstrap": boot_hits / replications,
        }

    return results


def print_results(results, alpha):
    nominal = (1 - alpha) * 100
    print(f"\n\nNominal coverage: {nominal:.0f}%\n")
    print(f"{'n':<8} {'Asymptotic':>12} {'Bootstrap':>12}")
    for n, res in results.items():
        print(f"{n:<8} {res['asymptotic']:>11.1%} {res['bootstrap']:>11.1%}")
    print("\nAsymptotic CI may under-cover for small n due to skewness, while Bootstrap CI should be more accurate.\n")


if __name__ == "__main__":
    np.random.seed(42)

    results = run_coverage_simulation(n_values=[5, 10, 100, 1000])
    print_results(results, alpha=0.05)