"""
PROBLEM 6
APPROACH:
    1. Pool all arrival times from both days and sort them.
    2. Estimate Λ̂(t) empirically: Λ̂(t) = (cumulative arrivals up to t) / num_days.
       This gives the average cumulative arrival count as a function of time.
    3. Build a linear interpolant of Λ̂(t) and its inverse Λ̂⁻¹(u).
    4. Generate arrivals using the inversion method:
         - Draw E_i ~ Exp(1), set u_i = u_{i-1} + E_i
         - Arrival time t_i = Λ̂⁻¹(u_i)
         - Stop when u_i > Λ̂(T) where T = 40 hours
"""

import numpy as np
import pathlib
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def load_arrival_times(filepath):
    namespace = {}
    exec(pathlib.Path(filepath).read_text(), namespace)
    return np.array(namespace["Times"])


def estimate_lambda_hat(times, num_days, T=40.0):
    """
    Build empirical Λ̂(t) as a piecewise-linear interpolant.
    Collapses simultaneous arrivals (same t across days) into a single
    point to avoid zero-length intervals and distorted rates.
    """
    sorted_times = np.sort(times)
    unique_times, counts = np.unique(sorted_times, return_counts=True)
    cumulative = np.cumsum(counts) / num_days
 
    t_points = np.concatenate([[0.0], unique_times, [T]])
    lambda_points = np.concatenate([[0.0], cumulative, [cumulative[-1]]])
 
    lambda_hat = interp1d(t_points, lambda_points, kind="linear", bounds_error=False,
                          fill_value=(0.0, cumulative[-1]))
    return lambda_hat, t_points, lambda_points


def build_inverse(t_points, lambda_points):
    """Build the inverse function Λ̂⁻¹(u) via interpolation."""
    _, unique_idx = np.unique(lambda_points, return_index=True)
    return interp1d(lambda_points[unique_idx], t_points[unique_idx],
                    kind="linear", bounds_error=False,
                    fill_value=(0.0, t_points[unique_idx[-1]]))


def generate_arrivals(lambda_hat, lambda_inv, T=40.0):
    """
    Generate one day of arrivals using the inversion method.
    Draw Exp(1) increments in the Λ domain, map back to time via Λ̂⁻¹.
    """
    total_lambda = lambda_hat(T)
    arrivals = []
    u = 0.0
 
    while True:
        u += np.random.exponential(1.0)
        if u > total_lambda:
            break
        arrivals.append(float(lambda_inv(u)))
 
    return np.array(arrivals)


def plot_results(times, arrivals, t_points, lambda_points, T=40.0):
    global seed
    t_fine = np.linspace(0, T, 500)
    lambda_hat_vals = interp1d(t_points, lambda_points, kind="linear",
                               bounds_error=False, fill_value=(0.0, lambda_points[-1]))(t_fine)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("HW4 Problem 6 — Nonstationary Poisson Process", fontsize=13)

    ax = axes[0]
    ax.plot(t_fine, lambda_hat_vals, color="steelblue", lw=2, label=r"$\hat{\Lambda}(t)$ (fitted)")
    ax.step(np.sort(times), np.arange(1, len(times) + 1) / 2,
            color="gray", lw=1, alpha=0.6, label="Observed (empirical)")
    ax.step(np.sort(arrivals), np.arange(1, len(arrivals) + 1),
            color="tomato", lw=1.5, linestyle="--", label="Generated arrivals")
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel(r"Cumulative arrivals $\Lambda(t)$")
    ax.set_title(r"Fitted $\hat{\Lambda}(t)$ vs. Generated")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    bins = np.arange(0, T + 1, 1)
    ax.hist(arrivals, bins=bins, color="steelblue", edgecolor="white", alpha=0.8, label="Generated")
    ax.hist(times / 2, bins=bins, color="gray", edgecolor="white", alpha=0.5, label="Observed avg/day")
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Arrivals per hour")
    ax.set_title("Hourly Arrival Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out_path = pathlib.Path(__file__).parent / "Results" / "HW4_Problem6_plot_rs_42.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nPlot saved to: {out_path}")
    plt.show()


def print_results(arrivals, lambda_hat, T=40.0):
    print(f"\n\nTotal arrivals generated       : {len(arrivals)}")
    print(f"Expected arrivals (Λ̂(T))       : {lambda_hat(T):.1f}")
    print(f"First arrival time (hours)     : {arrivals[0]:.3f}" if len(arrivals) else "No arrivals")
    print(f"Last arrival time (hours)      : {arrivals[-1]:.3f}" if len(arrivals) else "")
    print(f"\nGenerated arrival times : \n{np.round(arrivals[:40], 3)}\n\n")


if __name__ == "__main__":
    np.random.seed(42)

    data_path = pathlib.Path(__file__).parent / "Sources" / "data_problem6.txt"
    times = load_arrival_times(data_path)

    num_days = 2
    T = 40.0

    lambda_hat, t_points, lambda_points = estimate_lambda_hat(times, num_days, T)
    lambda_inv = build_inverse(t_points, lambda_points)

    arrivals = generate_arrivals(lambda_hat, lambda_inv, T)
    print_results(arrivals, lambda_hat, T)
    plot_results(times, arrivals, t_points, lambda_points, T)