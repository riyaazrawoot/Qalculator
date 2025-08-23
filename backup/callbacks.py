from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import datetime
import plotly.graph_objects as go

from services.graph_registry import make_roi_figure, make_cost_comparison_figure
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
        return dcc.send_data_frame(example_df.to_csv, "example.csv", index=False)

    # Step 1: Show checklist after button clicked
    @app.callback(
        Output("graph-options", "children"),
        Input("btn-generate", "n_clicks"),
        prevent_initial_call=True
    )
    def show_checklist(n_clicks):
        if not n_clicks:
            return None

        return dcc.Checklist(
            id="graph-checklist",
            options=[
                {"label": "ROI Over Time", "value": "ROI"},
                {"label": "Manual vs Automation Cost", "value": "Cost"},
                {"label": "Execution Time Savings", "value": "Time"},
            ],
            value=[]
        )

    # Step 2: Turn checklist into tabs
    @app.callback(
        Output("tabs-container", "children"),
        Input("graph-checklist", "value"),
        prevent_initial_call=True
    )
    def show_tabs(selected_graphs):
        if not selected_graphs:
            return html.Div("No graphs selected yet.")

        tabs = dcc.Tabs(
            id="tabs-example",
            value=selected_graphs[0],  # default tab = first one
            children=[
                dcc.Tab(label=graph, value=graph) for graph in selected_graphs
            ]
        )
        return tabs

    @app.callback(
        Output("graphs-container", "children", allow_duplicate=True),
        Input("graph-tabs", "value"),
        prevent_initial_call=True
    )
    def render_graph(tab_value):
        if tab_value == "Roi":
            return dcc.Graph(figure=make_roi_figure(example_df))
        elif tab_value == "Cost":
            return dcc.Graph(figure=make_cost_comparison_figure(example_df))

    # # 3) ROI graph + headline metrics
    # @app.callback(
    #     Output("roi-graph", "figure"),
    #     Output("roi-metrics", "children"),
    #     Input("active-df-store", "data"),
    #     Input("inp_salary_month", "value"),
    #     Input("inp_hours_month", "value"),
    #     Input("inp_releases_year", "value"),
    #     Input("inp_releases_to_plot", "value"),
    #     Input("inp_runs_per_release_global", "value"),
    # )
    # def update_roi(df_records, salary_month, hours_month, releases_per_year, releases_to_plot, runs_per_release_global):
    #     df = pd.DataFrame(df_records) if df_records else ExampleData.dataframe()
    #
    #     hourly_rate = salary_to_hourly(float(salary_month or 0), float(hours_month or 1))
    #     releases_to_plot = max(1, int(releases_to_plot or 1))
    #     releases_per_year = max(1.0, float(releases_per_year or 12))
    #     runs_per_release_global = max(1, int(runs_per_release_global or 1))
    #
    #     manual_per_release, auto_initial, auto_run_per_release, maint_pct, total_runs_this_release = \
    #         compute_cost_components(df, hourly_rate, runs_per_release_global)
    #
    #     x, manual_cum, auto_cum, be = cumulative_series(
    #         releases_to_plot, releases_per_year,
    #         manual_per_release, auto_initial, auto_run_per_release, maint_pct
    #     )
    #
    #     fig = go.Figure()
    #     fig.add_trace(go.Scatter(x=x, y=manual_cum, mode="lines+markers", name="Manual cumulative cost"))
    #     fig.add_trace(go.Scatter(x=x, y=auto_cum, mode="lines+markers", name="Automation cumulative cost"))
    #
    #     if be is not None:
    #         fig.add_trace(go.Scatter(
    #             x=[be], y=[auto_cum[be-1]],
    #             mode="markers+text", name="Break-even",
    #             text=["Break-even"], textposition="top center",
    #             marker=dict(size=12, symbol="x")
    #         ))
    #
    #     fig.update_layout(
    #         xaxis_title="Releases",
    #         yaxis_title="Cumulative Cost (ZAR)",
    #         legend_title="Scenario",
    #         height=520,
    #         margin=dict(l=40, r=20, t=40, b=40),
    #     )
    #
    #     metrics = [
    #         f"Manual cost per release: R{manual_per_release:,.0f}",
    #         f"Automation initial (dev) cost: R{auto_initial:,.0f}",
    #         f"Automation run cost per release: R{auto_run_per_release:,.0f}",
    #         f"Maintenance % / month (weighted): {maint_pct*100:.1f}%",
    #         f"Total runs this release (summed overrides or global): {total_runs_this_release}",
    #         f"Break-even release: {'Not reached' if be is None else be}",
    #     ]
    #     return fig, html.Ul([html.Li(m) for m in metrics])
