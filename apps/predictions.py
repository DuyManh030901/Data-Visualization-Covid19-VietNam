import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import json
from dash.dependencies import Input, Output, State
from app import app
from Model import model_graphs
# import time

try:
    layout = html.Div([
        html.Div([
            html.H4(' Dự Đoán Số Người Nhiễm Bệnh & Tử Vong', style={'text-align': 'center', 'background-color': '#99CCFF',
                                                         'border': '1px solid black',
                                                         'padding': '5px',
                                                         'margin': '5px',
                                                         'border-radius': '10px',
                                                         'box-shadow': '0 0 10px',
                                                         'color': 'black'})
        ], className='row'),
        html.P('Vui Lòng chờ 10-15s.....', style={'text-align': 'right',
                                                    'marginRight':"3%",
                                                                        'color': 'Red'}),
        html.Div([
            dcc.Dropdown(id='Cases-and-Deaths', options=[{'label': 'Ca Nhiễm', 'value': 'dailyconfirmed'},
                                                         {'label': 'Tử Vong', 'value': 'dailydeceased'}],
                         value='dailyconfirmed', style={'width': '320px','background-color': '#EEEEEE',
                                                        # 'border': '1px solid black',
                                                        # 'padding': '1px',
                                                        # 'margin': '1px',
                                                        # 'border-radius': '5px',
                                                        # 'box-shadow': '0 0 5px'
                                                        }),
            dcc.Loading(children=[dcc.Graph(id='figure1')], color="#119DFF", type="bar", fullscreen=False)

        ], className='row', style={'text-align': 'center','background-color': 'white',
                                    # 'width': '320px','right''marginLeft':"10%"
                                   # 'border': '1px solid black',
                                   # 'padding': '5px',
                                   # 'margin': '5px',
                                   # 'border-radius': '10px',
                                   # 'box-shadow': '0 0 10px'
                                   }),
        html.Div([
            html.Div([
                html.H6('Tóm Tắt Mô Hình', style={'text-align': 'center','background-color': '#EEEEEE',
                                                'width': '320px','marginLeft':"17%",
                                                'border': '0.5px solid black',
                                                # 'padding': '5px',
                                                # 'margin': '5px',
                                                # 'border-radius': '10px',
                                                # 'box-shadow': '0 0 10px',
                                                'color': 'black'}, className='six columns')
            ], className='row'),
            html.Div([
                dcc.Loading(children=[html.Div(id='table1')], color="#119DFF", type="bar", fullscreen=False),
                # dcc.Loading(children=[html.Div(id='table2')], color="#119DFF", type="bar", fullscreen=False)

            ], className='six columns', style={'background-color': 'white', 'width': '730px',
                                               # 'height': '100px',
                                               # 'border': '1px solid black',
                                               # 'padding': '5px',
                                               # 'margin': '5px',
                                               # 'border-radius': '10px',
                                               # 'box-shadow': '0 0 10px'
                                               })

        ], className='row'),
        html.Div([
            html.P("*Dự đoán có thể không chính xác....", style={
                'color': 'red', 'text-align': 'center'
            })
        ])
    ])


    @app.callback([Output('figure1', 'figure'),
                   Output('table1', 'children')],
                  [Input('Store-Data', 'children'), Input('Cases-and-Deaths', 'value')],
                  [State('Cases-and-Deaths', 'value')])
    def model_data(jsonified_cleaned_data, value, val):
        # begin = time.time()
        datasets = json.loads(jsonified_cleaned_data)
        data = pd.read_json(datasets['Country'], orient='split')
        data['dateymd'] = pd.to_datetime(data['dateymd'], format="%Y-%m-%d")

        fig, table_1 = model_graphs(data, value)
        # end = time.time()
        # print('Total time taken', end-begin)
        return fig, table_1

except:

    layout = html.Div([
        html.P("Đã xảy ra lỗi.......", style={
            'color': 'red', 'text-align': 'center'
        })
    ])
