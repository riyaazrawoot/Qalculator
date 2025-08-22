from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import datetime
import plotly.graph_objects as go

from services.roi_service import (
    salary_to_hourly,
    compute_cost_components,
    cumulative_series,
)
from domain import ExampleData
from io_upload import UploadParser

def register_callbacks(app, example_df: pd.DataFrame, parser: UploadParser):

    # 1) Preview table + store active data (uploaded or example)
    @app.callback(
        Output("output-data-upload", "children"),
        Output("active-df-store", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
        prevent_initial_call=False,
    )
    def on_upload(contents, filename, last_modified):
        if contents is None:
            df = example_df.copy()
            table = dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=6,
            )
            return [html.H5("Using example data"), table], df.to_dict("records")

        try:
            preview, df = parser.parse_contents(contents, filename, last_modified)
            return [preview], df.to_dict("records")
        except Exception as e:
            err = html.Div(f"Error processing file: {e}", style={"color": "crimson"})
            return [err], example_df.to_dict("records")

    # 2) Download example CSV
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_download(_):
        return dcc.send_data_frame(example_df.to_csv, "qa_roi_example.csv", index=False)

    # 3) ROI graph + headline metrics
    @app.callback(
        Output("roi-graph", "figure"),
        Output("roi-metrics", "children"),
        Input("active-df-store", "data"),
        Input("inp_salary_month", "value"),
        Input("inp_hours_month", "value"),
        Input("inp_releases_year", "value"),
        Input("inp_releases_to_plot", "value"),
        Input("inp_runs_per_release_global", "value"),
    )
    def update_roi(df_records, salary_month, hours_month, releases_per_year, releases_to_plot, runs_per_release_global):
        df = pd.DataFrame(df_records) if df_records else ExampleData.dataframe()

        hourly_rate = salary_to_hourly(float(salary_month or 0), float(hours_month or 1))
        releases_to_plot = max(1, int(releases_to_plot or 1))
        releases_per_year = max(1.0, float(releases_per_year or 12))
        runs_per_release_global = max(1, int(runs_per_release_global or 1))

        manual_per_release, auto_initial, auto_run_per_release, maint_pct, total_runs_this_release = \
            compute_cost_components(df, hourly_rate, runs_per_release_global)

        x, manual_cum, auto_cum, be = cumulative_series(
            releases_to_plot, releases_per_year,
            manual_per_release, auto_initial, auto_run_per_release, maint_pct
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=manual_cum, mode="lines+markers", name="Manual cumulative cost"))
        fig.add_trace(go.Scatter(x=x, y=auto_cum, mode="lines+markers", name="Automation cumulative cost"))

        if be is not None:
            fig.add_trace(go.Scatter(
                x=[be], y=[auto_cum[be-1]],
                mode="markers+text", name="Break-even",
                text=["Break-even"], textposition="top center",
                marker=dict(size=12, symbol="x")
            ))

        fig.update_layout(
            xaxis_title="Releases",
            yaxis_title="Cumulative Cost (ZAR)",
            legend_title="Scenario",
            height=520,
            margin=dict(l=40, r=20, t=40, b=40),
        )

        metrics = [
            f"Manual cost per release: R{manual_per_release:,.0f}",
            f"Automation initial (dev) cost: R{auto_initial:,.0f}",
            f"Automation run cost per release: R{auto_run_per_release:,.0f}",
            f"Maintenance % / month (weighted): {maint_pct*100:.1f}%",
            f"Total runs this release (summed overrides or global): {total_runs_this_release}",
            f"Break-even release: {'Not reached' if be is None else be}",
        ]
        return fig, html.Ul([html.Li(m) for m in metrics])
