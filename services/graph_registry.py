import pandas as pd
import plotly


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

    # Bar chart
    figure = plotly.express.bar(
        counts, x = "Category", y = "Count", text = "Count",
        title = "Manual vs Automation Comparison"
    )

    figure.update_traces(textposition="outside")
    figure.update_layout(xaxis_title="", yaxis_title="Number of test cases",
                         margin = dict(t=60))
    return figure




