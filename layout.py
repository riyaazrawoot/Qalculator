import pandas as pd
from dash import html, dcc


class Layout:
    def __init__(self, title: str, example_data_frame: pd.DataFrame, example_tester_data: pd.DataFrame):
        self.title = title
        self.example_data_frame = example_data_frame


    def build(self):
        return html.Div([
            html.H1(self.title),
            html.H5(["Find the example.csv below.",
                     html.Br(),
                     "If you don’t download and upload your own file, the app will use the built-in sample data instead.",
                     html.Br(),
                     "This lets you explore the calculations and graphs right away, but with example numbers rather than your own."]),

            html.Div(
                [
                    html.Button("Download Example CSV", id="btn_csv"),
                    dcc.Download(id="download-dataframe-csv"),
                ],
                id="btn_div"
            ),

            html.Div(
                [
                    html.Button("Download Example Tester Details CSV", id="btn_tester_csv"),
                    dcc.Download(id="download-tester-dataframe-csv"),
                ],
                id="btn_tester_div"
            ),

            html.H5(["Upload your own data below."]),

            html.Div([
                dcc.Upload(
                    id="upload-data",
                    children=html.Button("Select Data File"),
                    multiple=False,
                ),
                dcc.Upload(
                    id="upload-tester-data",
                    children=html.Button("Select Tester File"),
                    multiple=False,
                ),
            ], style={"display": "flex", "justifyContent": "center", "gap": "20px"}),

            html.Div([
                html.Label("Releases"),
                dcc.Input(id="input-releases", type="number", value=12, min=1, style={"marginRight": "20px"}),
                html.Label("Runs per Release"),
                dcc.Input(id="input-runs", type="number", value=1, min=1),
            ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "gap": "10px",
                      "margin": "20px 0"}),

            # Store active data (uploaded or example)
            dcc.Store(id="active-df-store"),
            dcc.Store(id="active-tester-df-store"),

            # Upload preview
            html.Div(id="output-data-upload"),
            html.Div(id="output-testdata-upload"),

            # Check list only shown once generate button is clicked
            html.Div([
                dcc.Checklist(id="graph-checklist", options=[], value=[], style={"display": "none"}),

                html.Button("Generate Graphs", id="btn-generate", n_clicks=0),
                html.Div(id="graph-options"),
                html.Div(id="tabs-container"),
                html.Div(id="tab-content")
            ], style={

                "padding": "30px"

            }),

        ], "app")


