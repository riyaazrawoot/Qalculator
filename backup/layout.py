from dash import html, dcc
import pandas as pd


class LayoutFactory:
    def __init__(self, title: str, example_df: pd.DataFrame):
        self.title = title
        self.example_df = example_df

    def build(self):
        return html.Div(
            [
                html.H1(self.title),
                html.H6([
                    "Download the sample CSV below and fill it with your test cases.",
                ],

                ),
                # Upload preview
                html.Div(id="output-data-upload"),

                html.Div(
                    [
                        html.Button("Download Example CSV", id="btn_csv"),
                        dcc.Download(id="download-dataframe-csv"),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "height": "10vh"
                    },
                ),

                html.Div([
                    html.H6([
                        "After uploading, the app will generate ROI calculations and graphs to help you compare manual vs automated testing."
                    ]),
                ]),

                dcc.Upload(
                    id="upload-data",
                    children=html.Button(html.A("Select Files")),
                    multiple=False,
                ),

                # Store active data (uploaded or example)
                dcc.Store(id="active-df-store"),

                html.Div([
                    dcc.Checklist(id="graph-checklist", options=[], value=[], style={"display": "none"}),

                    html.Button("Generate Graphs", id="btn-generate", n_clicks=0),
                    html.Div(id="graph-options"),
                    html.Div(id="tabs-container"),
                ], style={

                    "padding": "30px"

                }),

                # ROI assumption inputs
                # html.Div([
                #     html.Div([
                #         html.Label("Tester monthly salary (ZAR)"),
                #         dcc.Input(id="inp_salary_month", type="number", value=20000, step=500, style={"width":"100%"})
                #     ], className="three columns"),
                #     html.Div([
                #         html.Label("Tester hours per month"),
                #         dcc.Input(id="inp_hours_month", type="number", value=160, step=1, style={"width":"100%"})
                #     ], className="three columns"),
                #     html.Div([
                #         html.Label("Releases per year"),
                #         dcc.Input(id="inp_releases_year", type="number", value=12, step=1, style={"width":"100%"})
                #     ], className="three columns"),
                #     html.Div([
                #         html.Label("Releases to plot"),
                #         dcc.Input(id="inp_releases_to_plot", type="number", value=12, step=1, style={"width":"100%"})
                #     ], className="three columns"),
                # ], className="row", style={"margin":"10px 0"}),
                #
                # html.Div([
                #     html.Div([
                #         html.Label("Global runs per release (fallback)"),
                #         dcc.Input(id="inp_runs_per_release_global", type="number", value=1, step=1, style={"width":"100%"})
                #     ], className="three columns"),
                # ], className="row", style={"margin":"10px 0"}),

                # html.Hr(),

                # html.H3("Cumulative Cost Over Releases (Manual vs Automation)"),
                # dcc.Graph(id="roi-graph"),
                #
                # html.Div(id="roi-metrics", style={"marginTop": "8px", "fontWeight": "bold"}),
                #
                # dcc.Checklist(
                #     id="visible-tabs",
                #     options=[
                #         {"label": "Cumulative Cost", "value": "cum_cost"},
                #         {"label": "Per-run Cost", "value": "per_run_cost"},
                #         {"label": "Risk Distribution", "value": "risk_mix"},
                #         {"label": "Time Saved", "value": "time_saved"},
                #     ],
                #     value=["cum_cost", "per_run_cost"]  # sensible defaults
                # ),
                # dcc.Tabs(id="tabs", value="cum_cost"),  # active tab
                # html.Div(id="tabs-content")
            ],
            style={
                "textAlign": "center",
                "marginBottom": "20px",
                "padding": "20px"
            }
        )
