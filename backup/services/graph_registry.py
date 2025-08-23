import plotly.express as px
import pandas as pd

def make_roi_figure(df: pd.DataFrame):
    """
    Example ROI graph: show cumulative cost of manual vs automation over test runs
    """
    # pretend ROI calculation
    df["manual_cost"] = df["manual_time_min"] * 5   # tester wage per min
    df["automation_cost"] = (df["dev_time_hours"] * 200) / 10  # amortised
    df["runs"] = range(1, len(df) + 1)

    fig = px.line(
        df,
        x="runs",
        y=["manual_cost", "automation_cost"],
        title="ROI: Manual vs Automation",
        labels={"value": "Cost (ZAR)", "runs": "Test Runs"}
    )
    return fig


def make_cost_comparison_figure(df: pd.DataFrame):
    """
    Example bar chart comparing costs
    """
    avg_costs = {
        "Manual": df["manual_time_min"].sum() * 5,
        "Automation": df["dev_time_hours"].sum() * 200,
    }
    cost_df = pd.DataFrame(list(avg_costs.items()), columns=["Method", "Cost"])

    fig = px.bar(cost_df, x="Method", y="Cost", title="Total Cost Comparison")
    return fig
