import pandas as pd
import plotly
import plotly.graph_objects as go

from services.calculations import (
    execution_time_savings,
    manual_automation_comparison,
    average_hourly_rate,
    roi_over_time,
)

def manual_automation_comparison_graph(data_frame: pd.DataFrame):

    counts = manual_automation_comparison(data_frame)

    # Bar chart
    figure = plotly.express.bar(
        counts, x = "Category", y = "Count", text = "Count",
        title = "Manual vs Automation Comparison"
    )

    figure.update_traces(textposition="outside")
    figure.update_layout(xaxis_title="", yaxis_title="Number of test cases",
                         margin = dict(t=60))
    return figure


def execution_savings_time_graph(data_frame: pd.DataFrame, runs_per_release: int = 1, releases: int = 12):
    # compute totals
    stats = execution_time_savings(data_frame, runs_per_release=runs_per_release, releases=releases)

    # small plotting frame
    plot_df = pd.DataFrame([
        {"Category": "Manual", "Hours": stats["manual_hours"]},
        {"Category": "Automation", "Hours": stats["automation_hours"]},
    ])

    # bar chart comparing total execution hours
    fig = plotly.express.bar(
        plot_df,
        x="Category",
        y="Hours",
        text="Hours",
        title=f"Execution Time: Manual vs Automation (over {releases} releases × {runs_per_release} run(s)/release)",
        labels={"Hours": "Execution Time (hours)", "Category": ""},
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        yaxis_title="Execution Time (hours)",
        xaxis_title="",
        margin=dict(t=70, r=30, b=40, l=50),
    )

    # optional annotation showing savings
    fig.add_annotation(
        x=0.5, y=max(stats["manual_hours"], stats["automation_hours"]) * 1.05,
        text=f"Time saved: {stats['savings_hours']:.2f} h ({stats['savings_percentage']}%)",
        showarrow=False, yref="y", xref="paper", xanchor="center"
    )

    return fig


def roi_over_time_graph(
    data_frame: pd.DataFrame,
    testers_df: pd.DataFrame,
    runs_per_release: int = 1,
    releases: int = 12,
    releases_per_year: float = 12.0,
):
    rates = average_hourly_rate(testers_df)
    roi_df, break_even_release, break_even_cost = roi_over_time(
        data_frame, rates, runs_per_release, releases, releases_per_year
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=roi_df["release"],
            y=roi_df["manual_cost"],
            mode="lines+markers",
            name="Manual",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=roi_df["release"],
            y=roi_df["automation_cost"],
            mode="lines+markers",
            name="Automation",
        )
    )

    if break_even_release is not None and break_even_cost is not None:
        fig.add_trace(
            go.Scatter(
                x=[break_even_release],
                y=[break_even_cost],
                mode="markers",
                marker=dict(symbol="x", size=12, color="red"),
                name="Break-even",
            )
        )
        fig.add_annotation(
            x=break_even_release,
            y=break_even_cost,
            text=f"Break-even: Release {break_even_release:.2f}",
            showarrow=True,
            arrowhead=2,
        )

    fig.update_layout(
        title="ROI Over Time",
        xaxis_title="Release",
        yaxis_title="Cumulative Cost",
        margin=dict(t=60),
    )
    return fig



