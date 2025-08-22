from __future__ import annotations
import pandas as pd
from typing import Tuple, List

def salary_to_hourly(monthly_salary: float, hours_per_month: float) -> float:
    return float(monthly_salary) / max(1.0, float(hours_per_month))

def months_over(releases: int, releases_per_year: float) -> float:
    # If 12 releases/year => ~1 release per month
    return (releases / max(1.0, releases_per_year)) * 12.0

def compute_cost_components(
    df: pd.DataFrame,
    hourly_rate: float,
    runs_per_release_global: int
) -> Tuple[float, float, float, float, int]:
    """
    Returns:
      manual_cost_per_release,
      automation_initial_cost,
      automation_run_cost_per_release,
      maintenance_pct_weighted (0..1),
      total_runs_this_release (int)
    """
    # Manual
    total_manual_hours = df["manual_time_min"].fillna(0).sum() / 60.0
    manual_cost_per_run = total_manual_hours * hourly_rate

    runs_overrides = df["runs_per_release_override"].fillna("")
    runs_per_release = []
    for val in runs_overrides:
        try:
            rp = int(val)
            rp = rp if rp > 0 else runs_per_release_global
        except Exception:
            rp = runs_per_release_global
        runs_per_release.append(rp)
    total_runs_this_release = max(1, sum(runs_per_release))
    manual_cost_per_release = manual_cost_per_run * total_runs_this_release

    # Candidates for automation
    candidates = ~df["candidate_for_automation"].astype(str).str.strip().str.lower().eq("no")

    # Dev (initial) cost
    dev_hours = df.loc[candidates, "dev_time_hours"].fillna(0).sum()
    automation_initial_cost = dev_hours * hourly_rate

    # Execution cost per release
    exec_seconds_per_run = df.loc[candidates, "exec_time_sec"].fillna(0).sum()
    exec_hours_per_run = exec_seconds_per_run / 3600.0
    automation_run_cost_per_release = exec_hours_per_run * hourly_rate * total_runs_this_release

    # Maintenance (weighted mean of %/month)
    maintenance_pct_weighted = df.loc[candidates, "maintenance_pct_per_month"].fillna(0).mean() / 100.0

    return (
        manual_cost_per_release,
        automation_initial_cost,
        automation_run_cost_per_release,
        maintenance_pct_weighted,
        total_runs_this_release,
    )

def cumulative_series(
    releases_to_plot: int,
    releases_per_year: float,
    manual_cost_per_release: float,
    auto_initial: float,
    auto_run_cost_per_release: float,
    maint_pct: float
):
    x = list(range(1, releases_to_plot + 1))
    manual_cum, auto_cum = [], []
    break_even_release = None

    for r in x:
        months_so_far = months_over(r, releases_per_year)
        maintenance_cost_cum = auto_initial * maint_pct * months_so_far

        manual_cum_cost = manual_cost_per_release * r
        auto_cum_cost = auto_initial + (auto_run_cost_per_release * r) + maintenance_cost_cum

        manual_cum.append(manual_cum_cost)
        auto_cum.append(auto_cum_cost)

        if break_even_release is None and auto_cum_cost <= manual_cum_cost:
            break_even_release = r

    return x, manual_cum, auto_cum, break_even_release
