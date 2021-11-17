import dash
import plotly.validator_cache
import json

external_stylesheets = ['assets/bWLwgP.css', 'assets/styles.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}],
                )

server = app.server

# try:
#     vietnam_geojson = "https://data.opendevelopmentmekong.net/dataset/55bdad36-c476-4be9-a52d-aa839534200a/resource/b8f60493-7564-4707-aa72-a0172ba795d8/download/vn_iso_province.geojson"
# except:
#     vietnam_geojson = json.load(open("vn_iso_province.geojson", "r"))



