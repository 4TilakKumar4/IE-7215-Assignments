import numpy as np
from scipy.stats import norm

# SAN: Y = max(X1+X4, X1+X3+X5, X2+X5)
# Default scenario: all activity means = 1 (base SAN from Section 4.4)

def simulate_san(n_reps, seed=42):
    rng = np.random.default_rng(seed)
    X = rng.exponential(scale=1.0, size=(n_reps, 5))
    X1, X2, X3, X4, X5 = X[:, 0], X[:, 1], X[:, 2], X[:, 3], X[:, 4]
    return np.maximum.reduce([X1 + X4, X1 + X3 + X5, X2 + X5])

def quantile_ci(Y, q, alpha):
    """
    Point estimate and order-statistic CI for the q-quantile.
    Uses normal approximation to binomial (Eq 7.7 from textbook).
    """
    n = len(Y)
    Y_sorted = np.sort(Y)

    # Point estimate: Y_{ceil(nq)}
    idx = int(np.ceil(n * q)) - 1  # 0-based
    point_est = Y_sorted[idx]

    # CI bounds via normal approx to binomial
    z = norm.ppf(1 - alpha / 2)
    spread = z * np.sqrt(n * q * (1 - q))
    l = int(np.floor(n * q - spread))
    u = int(np.ceil(n * q + spread))

    # Clamp to valid index range
    l = max(l - 1, 0)      # convert to 0-based
    u = min(u - 1, n - 1)

    ci_lower = Y_sorted[l]
    ci_upper = Y_sorted[u]

    return point_est, ci_lower, ci_upper, l + 1, u + 1  # report 1-based order stats

# --- Run with n = 1000 replications ---
n = 1000
q = 0.95
alpha = 0.05   # 95% CI

Y = simulate_san(n_reps=n, seed=42)
point_est, ci_lo, ci_hi, l_idx, u_idx = quantile_ci(Y, q, alpha)


print("\n")
print(f"Estimated 0.95 quantile: {point_est:.4f}")
print(f"SAN Quantile Estimation (base scenario, all means = 1)")
print(f"{'─'*50}")
print(f"Replications (n)     : {n}")
print(f"Quantile level (q)   : {q}")
print(f"Confidence level     : {int((1-alpha)*100)}%")
print(f"")
print(f"Point estimate ϑ̂    : {point_est:.4f}  [order stat Y_({int(np.ceil(n*q))})]")
print(f"95% CI               : [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"CI order stats       : [Y_({l_idx}), Y_({u_idx})]")
print(f"CI half-width        : {(ci_hi - ci_lo)/2:.4f}")
print(f"")
print(f"Interpretation: With 95% confidence, the true 0.95 quantile")
print(f"of project completion time lies in [{ci_lo:.4f}, {ci_hi:.4f}] days.")
print(f"There is a 95% probability the project completes within {point_est:.4f} days.")
print("\n")