from typing import Tuple

import pandas as pd

from data import ExampleTesters

def manual_automation_comparison(data_frame: pd.DataFrame):
    df = data_frame.copy()
    column_name = "candidate_for_automation"
    col = df[column_name].astype(str).str.strip().str.lower()

    counts = pd.DataFrame({
        "Category": ["Automation Candidates", "Manual Only"],
        "Count": [
            (col.isin(["yes", "auto"])).sum(),
            (col == "no").sum()
        ]
    })


    return counts

def average_hourly_rate(testers_df):
    def avg_rate(role):
        pool = testers_df[testers_df["role"] == role].copy()
        if pool.empty:
            return 0.0
        pool["hourly_rate"] = pool["monthly_salary"] / pool["hours_per_month"].clip(lower=1)
        return pool["hourly_rate"].mean()

    return {
        "manual_rate": avg_rate("manual"),
        "automation_rate": avg_rate("automation")
    }

rates = average_hourly_rate(ExampleTesters.tester_data_frame())
print(rates)

def execution_time_savings(data_frame: pd.DataFrame, runs_per_release = 1, releases = 12):
    df = data_frame.copy()

    manual_total_hours = (df["manual_time_min"].fillna(0).sum() / 60) \
    * runs_per_release * releases

    automation_total_hours = (df["exec_time_sec"].fillna(0).sum() / 3600) \
    * runs_per_release * releases

    savings_hours = manual_total_hours - automation_total_hours
    savings_percentage = (savings_hours / manual_total_hours * 100) if manual_total_hours > 0 else 0

    return {
        "manual_hours": manual_total_hours,
        "automation_hours": automation_total_hours,
        "savings_hours": savings_hours,
        "savings_percentage": round(savings_percentage, 2),
    }


def make_roi_figure(releases: int, releases_per_year: float) -> float:
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