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
                html.Blockquote(
                    "Download the example CSV, populate it, then upload to work out the ROI"
                ),
                html.Div(
                    [
                        html.Button("Download Example CSV", id="btn_csv"),
                        dcc.Download(id="download-dataframe-csv"),
                    ],
                    style={"marginBottom": "12px"},
                ),

                # ROI assumption inputs
                html.Div([
                    html.Div([
                        html.Label("Tester monthly salary (ZAR)"),
                        dcc.Input(id="inp_salary_month", type="number", value=20000, step=500, style={"width":"100%"})
                    ], className="three columns"),
                    html.Div([
                        html.Label("Tester hours per month"),
                        dcc.Input(id="inp_hours_month", type="number", value=160, step=1, style={"width":"100%"})
                    ], className="three columns"),
                    html.Div([
                        html.Label("Releases per year"),
                        dcc.Input(id="inp_releases_year", type="number", value=12, step=1, style={"width":"100%"})
                    ], className="three columns"),
                    html.Div([
                        html.Label("Releases to plot"),
                        dcc.Input(id="inp_releases_to_plot", type="number", value=12, step=1, style={"width":"100%"})
                    ], className="three columns"),
                ], className="row", style={"margin":"10px 0"}),

                html.Div([
                    html.Div([
                        html.Label("Global runs per release (fallback)"),
                        dcc.Input(id="inp_runs_per_release_global", type="number", value=1, step=1, style={"width":"100%"})
                    ], className="three columns"),
                ], className="row", style={"margin":"10px 0"}),

                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    style={
                        "width":"100%","height":"60px","lineHeight":"60px","borderWidth":"1px",
                        "borderStyle":"dashed","borderRadius":"5px","textAlign":"center","margin":"10px"
                    },
                    multiple=False,
                ),

                # Store active data (uploaded or example)
                dcc.Store(id="active-df-store"),

                # Upload preview
                html.Div(id="output-data-upload"),

                html.Hr(),

                html.H3("Cumulative Cost Over Releases (Manual vs Automation)"),
                dcc.Graph(id="roi-graph"),

                html.Div(id="roi-metrics", style={"marginTop": "8px", "fontWeight": "bold"}),
            ]
        )
