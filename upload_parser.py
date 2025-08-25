import base64, io, datetime as dt
from typing import Tuple
import pandas as pd
from dash import html, dash_table
from data import CsvSchema

class UploadParser:
    def __init__(self, columns: Tuple[str, ...]):
        self.columns = columns

    def parse_contents(self, contents: str, filename: str, last_modified: int):
        df = self._to_dataframe(contents, filename)
        self._validate_schema(df)
        return self._render_preview(df, filename, last_modified), df

    def _to_dataframe(self, contents: str, filename: str) -> pd.DataFrame:
        content_type, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)

        fn = filename.lower()
        if fn.endswith(".csv"):
            return pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        if fn.endswith((".xls", ".xlsx")):
            return pd.read_excel(io.BytesIO(decoded))
        raise ValueError("Unsupported file type. Please upload .csv or .xlsx")

    def _validate_schema(self, df: pd.DataFrame) -> None:
        missing = [c for c in self.columns if c not in df.columns]
        if missing:
            raise ValueError(f"Columns does not match the example.csv: {missing}")

    def _render_preview(self, df: pd.DataFrame, filename: str, last_modified: int):
        return html.Div([
            html.H5(filename),
            html.H6(dt.datetime.fromtimestamp(last_modified)),
            dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": c, "id": c} for c in df.columns],
                page_size=10,
                style_table={"overflowX": "auto"},
            ),
            html.Hr(),
        ])
