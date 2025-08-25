import pandas as pd
import plotly

from services.calculations import execution_time_savings, manual_automation_comparison


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


