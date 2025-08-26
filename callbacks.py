from dash import dcc, Input, Output, dash_table, html, State
import pandas as pd

from services.graph_registry import (
    execution_savings_time_graph,
    manual_automation_comparison_graph,
    roi_over_time_graph,
)
from upload_parser import UploadParser


def register_callbacks(app, example_df: pd.DataFrame, tester_example_df: pd.DataFrame, parser: UploadParser, tester_parser: UploadParser):

    # 1) Download example.csv
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_download(_):
        # Called after the first click
        return dcc.send_data_frame(example_df.to_csv, "qa_example.csv", index=False)

    # 2) Preview table + store active data (uploaded or example)
    @app.callback(
        Output("output-data-upload", "children"),
        Output("active-df-store", "data"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
        prevent_initial_call=False,
    )
    def on_upload(contents: str, filename: str, last_modified: int):
        if contents is None:
            data_frame = example_df.copy()
            table = dash_table.DataTable(
                data=data_frame.to_dict("records"),
                columns=[{"name": i, "id": i} for i in data_frame.columns],
                page_size=6,
            )
            return [html.H5("Using example data"), table], data_frame.to_dict("records")

        try:
            preview, df = parser.parse_contents(contents, filename, last_modified)
            return [preview], df.to_dict("records")
        except Exception as e:
            err = html.Div(f"Error processing file: {e}", style={"color": "crimson"})
            return [err], example_df.to_dict("records")


    # 3) Show checklist after button clicked
    @app.callback(
        Output("graph-options","children"),
        Input("btn-generate", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_checklist(n_clicks):
        if not n_clicks:
            return None
        
        return dcc.Checklist(
            id="graph-checklist",
            options=[
                {"label": "ROI Over Time", "value": "ROI"},
                {"label": "Manual vs Automation Testcases", "value": "Manual vs Automation Testcases"},
                {"label": "Execution Time Savings", "value": "Time"},
            ],
            value=["ROI"],
            labelStyle={"display": "flex", "padding": "10px 12px", "border": "1px solid #e5e7eb",
                        "borderRadius": "8px", "margin": "6px 0", "cursor": "pointer"},
            inputStyle={"marginRight": "10px"},
            style={"maxWidth": "100%", "margin": "0 auto"}
        )

    # 4) Turn checklist into tabs
    @app.callback(
        Output("tabs-container", "children"),
        Input("graph-checklist", "value"),
        prevent_initial_call=False
    )
    def show_tabs(selected_graphs):
        if not selected_graphs:
            return "No graphs selected yet."

            # build one tab per selected graph
        tabs = [
            dcc.Tab(label=val, value=val) for val in selected_graphs
        ]
        return dcc.Tabs(id="graph-tabs", value=selected_graphs[0], children=tabs)

    # 5) Statement to show graphs per tab
    @app.callback(
        Output("tab-content", "children"),
        Input("graph-tabs", "value"),
        State("active-df-store", "data"),
        State("active-tester-df-store", "data"),
        prevent_initial_call=True
    )
    def render_graph(tab_value, records, tester_records):
        data_frame = pd.DataFrame(records) if records else example_df
        tester_df = pd.DataFrame(tester_records) if tester_records else tester_example_df

        if tab_value in ("Manual vs Automation Testcases", "Cost", "COST"):
            figure = manual_automation_comparison_graph(data_frame)
            description = (
                "Displays the number of test cases that are good candidates for automation"
                " versus those that remain manual."
            )
            return html.Div([dcc.Graph(figure=figure), html.P(description)])
        elif tab_value == "Time":
            figure = execution_savings_time_graph(data_frame, runs_per_release=1, releases=12)
            description = (
                "Compares total execution hours for manual and automated runs,"
                " highlighting time saved through automation."
            )
            return html.Div([dcc.Graph(figure=figure), html.P(description)])
        elif tab_value == "ROI":
            figure = roi_over_time_graph(
                data_frame,
                tester_df,
                runs_per_release=1,
                releases=12,
                releases_per_year=12.0,
            )
            description = (
                "Shows cumulative manual testing and automation costs per release and"
                " marks the release where automation breaks even."
            )
            return html.Div([dcc.Graph(figure=figure), html.P(description)])
        return html.H3(f"You clicked the {tab_value} tab")


    # 6) Download tester data
    @app.callback(
        Output("download-tester-dataframe-csv", "data"),
        Input("btn_tester_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_download_tester_data(_):
        # Called after the first click
        return dcc.send_data_frame(tester_example_df.to_csv, "qa_tester_example.csv", index=False)

    # 7) Preview table + store testdata data (uploaded or example)
    @app.callback(
        Output("output-testdata-upload", "children"),
        Output("active-tester-df-store", "data"),
        Input("upload-tester-data", "contents"),
        State("upload-tester-data", "filename"),
        State("upload-tester-data", "last_modified"),
        prevent_initial_call=False,
    )
    def on__tester_details_upload(contents: str, filename: str, last_modified: int):
        if contents is None:
            tester_data_frame = tester_example_df.copy()
            table = dash_table.DataTable(
                data=tester_data_frame.to_dict("records"),
                columns=[{"name": i, "id": i} for i in tester_data_frame.columns],
                page_size=6,
            )
            return [html.H5("Using example data"), table], tester_data_frame.to_dict("records")

        try:
            preview, df = tester_parser.parse_contents(contents, filename, last_modified)
            return [preview], df.to_dict("records")
        except Exception as e:
            err = html.Div(f"Error processing file: {e}", style={"color": "crimson"})
            return [err], tester_example_df.to_dict("records")