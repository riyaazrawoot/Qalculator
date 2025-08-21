from dash import Dash, dcc, dash_table, html, Input, Output, callback,State
import base64
import datetime
import io
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    [
        html.H1('QAlculator'),
        html.Blockquote('The below csv must be downloaded and populated with your details to work out the ROI'),
        html.Button("Download Example CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
    ]
)

df = pd.DataFrame({
    "test_id": [
        "TC-001", "TC-002", "TC-003", "TC-004", "TC-005", "TC-006"
    ],
    "title": [
        "Login - valid creds",
        "Login - invalid creds",
        "Password reset flow",
        "Profile update",
        "Footer links",
        "Search - basic"
    ],
    "risk": [
        "High", "Medium", "High", "Medium", "Low", "Low"
    ],
    "manual_time_min": [
        5, 4, 7, 5, 2, 3
    ],
    "candidate_for_automation": [
        "Yes", "Yes", "Yes", "Auto", "No", "Auto"
    ],
    "dev_time_hours": [
        2.0, 1.5, 3.0, 2.0, 0.0, 1.0
    ],
    "exec_time_sec": [
        8, 8, 12, 10, 0, 6
    ],
    "maintenance_pct_per_month": [
        5, 4, 6, 4, 0, 3
    ],
    "runs_per_release_override": [
        "", "", "", "", "", 2
    ]
})

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "mydf.csv")


if __name__ == "__main__":
    app.run(debug=True)
