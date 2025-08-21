from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd

app = Dash()
app.layout = html.Div(
    [
        html.H1('QAlculator'),
        html.Blockquote('The below csv must be downloaded and populated with your details to work out the ROI'),
        html.Button("Download Example CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
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


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "mydf.csv")


if __name__ == "__main__":
    app.run(debug=True)
