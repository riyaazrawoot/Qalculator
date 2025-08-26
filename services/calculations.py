import array
from typing import Tuple, Dict
import pandas as pd
import numpy as np

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
    average_hourly_rate: Dict[str, float],
    runs_per_release_global: int,
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
    manual_cost_per_run = total_manual_hours * average_hourly_rate['manual_rate']

    runs_overrides = pd.to_numeric(
        df["runs_per_release_override"], errors="coerce"
    ).fillna(runs_per_release_global)
    runs_overrides = runs_overrides.where(
        runs_overrides > 0, runs_per_release_global
    )
    total_runs_this_release = max(1, int(runs_overrides.sum()))
    manual_cost_per_release = manual_cost_per_run * total_runs_this_release

    # Candidates for automation
    candidates = ~df["candidate_for_automation"].astype(str).str.strip().str.lower().eq("no")

    # Dev (initial) cost
    dev_hours = df.loc[candidates, "dev_time_hours"].fillna(0).sum()
    automation_initial_cost = dev_hours * average_hourly_rate["automation_rate"]

    # Execution cost per release
    exec_seconds_per_run = df.loc[candidates, "exec_time_sec"].fillna(0).sum()
    exec_hours_per_run = exec_seconds_per_run / 3600.0
    automation_run_cost_per_release = exec_hours_per_run * average_hourly_rate["automation_rate"] * total_runs_this_release

    # Maintenance (weighted mean of %/month)
    maintenance_pct_weighted = df.loc[candidates, "maintenance_pct_per_month"].fillna(0).mean() / 100.0

    return (
        manual_cost_per_release,
        automation_initial_cost,
        automation_run_cost_per_release,
        maintenance_pct_weighted,
        total_runs_this_release,
    )

def roi_over_time(
    df: pd.DataFrame,
    average_hourly_rate: Dict[str, float],
    runs_per_release_global: int,
    releases: int,
    releases_per_year: float,
):
    (
        manual_cost_per_release,
        automation_initial_cost,
        automation_run_cost_per_release,
        maintenance_pct,
        _,
    ) = compute_cost_components(df, average_hourly_rate, runs_per_release_global)

    months_per_release = 12.0 / max(releases_per_year, 1.0)
    maintenance_cost_per_release = (
            automation_initial_cost * maintenance_pct * months_per_release
    )

    releases_arr = np.arange(1, releases + 1)
    manual_cumulative = releases_arr * manual_cost_per_release
    automation_cumulative = (
        automation_initial_cost
        + releases_arr * (automation_run_cost_per_release + maintenance_cost_per_release)
    )
    roi = manual_cumulative - automation_cumulative

    roi_df = pd.DataFrame(
        {
            "release": releases_arr,
            "manual_cost": manual_cumulative,
            "automation_cost": automation_cumulative,
            "roi": roi,
        }
    )

    releases_ext = np.insert(releases_arr, 0, 0)
    roi_ext = np.insert(roi, 0, -automation_initial_cost)

    break_even_release = None
    break_even_cost = None
    for i in range(1, len(releases_ext)):
        r_prev, r_curr = releases_ext[i - 1], releases_ext[i]
        roi_prev, roi_curr = roi_ext[i - 1], roi_ext[i]

        if roi_curr == 0:
            break_even_release = float(r_curr)
        elif roi_prev == 0:
            break_even_release = float(r_prev)
        elif roi_prev * roi_curr < 0:
            # linear interpolation between r_prev and r_curr where roi crosses zero
            ratio = -roi_prev / (roi_curr - roi_prev)
            break_even_release = float(r_prev + (r_curr - r_prev) * ratio)

        if break_even_release is not None:
            break_even_cost = float(manual_cost_per_release * break_even_release)
            break

    return roi_df, break_even_release, break_even_cost




def manual_testing_cost(data_frame: pd.DataFrame, testers_df: pd.DataFrame, runs_per_release = 1, releases = 12):
    df = data_frame.copy()

    manual_hours = (df["manual_time_min"].fillna(0).sum() / 60) \
    * runs_per_release * releases

    return manual_hours * average_hourly_rate(testers_df)["manual_rate"]

def automation_exec_hours(data_frame: pd.DataFrame, testers_df: pd.DataFrame, runs_per_release = 1, releases = 12):
    df = data_frame.copy()

    return ((df["exec_time_sec"].fillna(0).sum() / 3600) 
    * runs_per_release * releases) * average_automation_hourly_rate(testers_df)

def average_automation_hourly_rate(testers_df: pd.DataFrame):
    return average_hourly_rate(testers_df)["automation_rate"]

def initial_development_cost(data_frame: pd.DataFrame, testers_df: pd.DataFrame):
    return data_frame["dev_time_hours"].fillna(0).sum() * average_automation_hourly_rate(testers_df)

def average_maintenance_pct_per_month(data_frame: pd.DataFrame):
    candidates = ~data_frame["candidate_for_automation"].astype(str).str.strip().str.lower().eq("no")
    return data_frame.loc[candidates, "maintenance_pct_per_month"].fillna(0).mean() / 100
