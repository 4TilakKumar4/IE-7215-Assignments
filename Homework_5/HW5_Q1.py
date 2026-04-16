import numpy as np
from scipy import stats
from pathlib import Path

# SAN: Y = max(X1+X4, X1+X3+X5, X2+X5)
# Each scenario reduces one activity mean; all others remain at mean=1
# Scenario means: rows = scenarios, cols = (mu1, mu2, mu3, mu4, mu5)
scenarios = {
    "x1": (0.5, 1.0, 1.0, 0.3, 1.0),
    "x2": (1.0, 0.5, 1.0, 1.0, 1.0),
    "x3": (1.0, 1.0, 0.5, 1.0, 1.0),
    "x4": (1.0, 1.0, 1.0, 0.4, 1.0),
    "x5": (1.0, 1.0, 1.0, 1.0, 0.5),
}


def simulate_san(means, n_reps, seed):
    """Simulate the SAN for n_reps replications; return array of completion times."""
    rng = np.random.default_rng(seed)
    mu = np.array(means)
    # Generate all activity times at once: shape (n_reps, 5)
    X = rng.exponential(scale=mu, size=(n_reps, 5))
    X1, X2, X3, X4, X5 = X[:, 0], X[:, 1], X[:, 2], X[:, 3], X[:, 4]
    Y = np.maximum.reduce([X1 + X4, X1 + X3 + X5, X2 + X5])
    return Y


def subset_selection(obs_dict, alpha=0.05):
    """
    Apply subset selection (Boesel et al. 2003) without CRN.
    obs_dict: {name: array of observations}
    Returns list of scenario names in the selected subset I.
    """
    names = list(obs_dict.keys())
    K = len(names)
    n = {k: len(v) for k, v in obs_dict.items()}
    means = {k: np.mean(v) for k, v in obs_dict.items()}
    variances = {k: np.var(v, ddof=1) for k, v in obs_dict.items()}

    # t_i = quantile of t-distribution at level (1-alpha)^(1/(K-1)), df = n_i - 1
    level = (1 - alpha) ** (1 / (K - 1))
    t2 = {k: stats.t.ppf(level, df=n[k] - 1) ** 2 for k in names}

    # Include x_i if mean(x_i) <= mean(x_h) + W_ih for all h != i
    subset = []
    for i in names:
        keep = True
        for h in names:
            if h == i:
                continue
            W_ih = np.sqrt(t2[i] * variances[i] / n[i] + t2[h] * variances[h] / n[h])
            if means[i] > means[h] + W_ih:
                keep = False
                break
        if keep:
            subset.append(i)
    return subset, means, variances, t2


def run_experiment(n_reps, base_seed=42):
    print(f"\n")
    print(f"  n = {n_reps} replications per scenario")
    print(f"{'_'*60}")

    obs = {}
    for i, (name, means) in enumerate(scenarios.items()):
        obs[name] = simulate_san(means, n_reps, seed=base_seed + i)

    subset, means, variances, t2 = subset_selection(obs, alpha=0.05)

    print(f"\n{'Scenario':<10} {'Mean':>12} {'Variance':>12} {'t^2':>8}")
    print("-" * 46)
    for name in scenarios:
        print(f"{name:<10} {means[name]:>12.6f} {variances[name]:>12.6f} {t2[name]:>8.4f}")

    print(f"\nSelected subset I = {subset}")
    print(f"Eliminated: {[s for s in scenarios if s not in subset]}")

    # Show W_ih matrix for transparency
    print(f"\nW_ih thresholds (row i vs col h):")
    names = list(scenarios.keys())
    header = f"{'':>6}" + "".join(f"{h:>10}" for h in names)
    print(header)
    for i in names:
        row = f"{i:>6}"
        for h in names:
            if h == i:
                row += f"{'---':>10}"
            else:
                W = np.sqrt(t2[i] * variances[i] / len(obs[i]) +
                            t2[h] * variances[h] / len(obs[h]))
                row += f"{W:>10.4f}"
        print(row)

    return subset


if __name__ == "__main__":
    subset_100 = run_experiment(n_reps=100)
    subset_200 = run_experiment(n_reps=200)

    print(f"\n{'-'*60}")
    print("  Summary")
    print(f"{'-'*60}")
    print(f"n=100  selected subset: {subset_100}")
    print(f"n=200  selected subset: {subset_200}")
    print("\n")