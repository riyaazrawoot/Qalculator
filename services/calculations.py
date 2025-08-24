import pandas as pd

from data import ExampleTesters


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