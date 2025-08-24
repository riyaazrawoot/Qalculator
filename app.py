import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc

from callbacks import register_callbacks
from data import ExampleData, CsvSchema, ExampleTesters
from layout import Layout
from upload_parser import UploadParser


# -> Dash is the return of the method
def create_app(
        title: str = "QAlculator"
) -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)

    data_frame = ExampleData.data_frame()
    tester_data_frame = ExampleTesters.tester_data_frame()

    app.title = title

    app.layout = Layout(title, data_frame, tester_data_frame).build()

    parser = UploadParser(CsvSchema())
    register_callbacks(app, data_frame, tester_data_frame, parser)

    return app



if __name__ == "__main__":
    create_app().run(debug=True)
