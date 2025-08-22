from dash import Dash
from domain import ExampleData, CsvSchema
from layout import LayoutFactory
from io_upload import UploadParser
from callbacks import register_callbacks

EXTERNAL_STYLES = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

def create_app() -> Dash:
    app = Dash(__name__, external_stylesheets=EXTERNAL_STYLES)

    example_df = ExampleData.dataframe()
    app.title = "QAlculator"
    app.layout = LayoutFactory("QAlculator", example_df).build()

    parser = UploadParser(CsvSchema())
    register_callbacks(app, example_df, parser)
    return app

if __name__ == "__main__":
    create_app().run(debug=True)
