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
