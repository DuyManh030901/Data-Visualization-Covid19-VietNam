import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output, State
import plotly.validator_cache
import plotly.express as px
import json
import time
import numpy as np
import datetime 
from plotly.subplots import make_subplots
import requests
from app import app
import unidecode

#làm sạch dữ liệu về vaccine
def load_data_vaccine():
    #loads data về sôs liệu theo tỉnh
    x=pd.read_csv("https://vnexpress.net/microservice/sheet/type/vaccine_data_vietnam_city")
    df1=pd.DataFrame(x,
    columns=['fK','Số người đã tiêm','Số người tiêm liều 1','Số người tiêm liều 2 ','Tổng số dân','Tổng số dân trên 18 tuổi',
            'Số liều Vaccine dự kiến phân bổ','Số liều Vaccine thực tế phân bổ'])
    df1['ratio']=round((df1['Số người đã tiêm']/df1['Tổng số dân'])*100,2)
    df1['ratio118']=round((df1['Số người tiêm liều 1']/df1['Tổng số dân trên 18 tuổi'])*100,2)
    df1['ratio218']=round((df1['Số người tiêm liều 2 ']/df1['Tổng số dân trên 18 tuổi'])*100,2)
    Countryvaccine=df1
    Countryvaccine.columns=['state','Total','Mui1','Mui2','Population','Population_18','expected_vaccine','reality_vaccine',
            'ratio','ratio_1_18','ratio_2_18']

    #số liệu data theo ngày
    y=pd.read_csv("https://vnexpress.net/microservice/sheet/type/vaccine_data_vietnam")
    df2=pd.DataFrame(y,
                        columns=['Ngày','Số người tiêm chưa đủ mũi theo ngày',
                                 'Tổng số người đã tiêm theo ngày'])
    #mã hoá ngày vì file định dạng sai
    c=[]
    d=[]
    m=''
    for i in df2['Ngày']:
        m=''
        m=str(i)+"/2021"
        c.append(m)
    date_format =  "%d/%m/%Y"
    for time in c:
           d.append(datetime.datetime.strptime(time,date_format).strftime("%Y-%m-%d")) #mã hoá theo định dạng đúng
    df2["Ngày"]=d
    date1 = pd.to_datetime(datetime.date.today())
    df2['Ngày'] = pd.to_datetime(df2['Ngày'])   #chuyển định dạng đúng
    df2=df2[~df2.isin([np.nan, np.inf, -np.inf]).any(1)] #bỏ đi các hàng NaN
    vaccine=df2
    vaccine.columns=['date','Mui1','Dailytotal']
    mui1s=[]
    for i in vaccine['Mui1']:
         if i<0:
            mui1s.append(-i)
         else:
             mui1s.append(i)
    vaccine['Mui1']=mui1s
    vaccine['Mui2']=vaccine['Dailytotal']-vaccine['Mui1']
    vaccine[['Mui1','Dailytotal','Mui2']]=vaccine[['Mui1',
                                                       'Dailytotal','Mui2']].apply(pd.to_numeric)

    #các loại vaccine
    z1=pd.read_csv("https://vnexpress.net/microservice/sheet/type/vaccine_to_vietnam")
    df3=pd.DataFrame(z1,
                    columns=['AstraZeneca','Pfilzer','Moderna','Sinopharm','Nanocovax','Sinovac'])
    df3=df3.fillna('0')
    df3['AstraZeneca'] = df3['AstraZeneca'].str.replace(r'[^\w\s]+', '')
    df3['Pfilzer'] = df3['Pfilzer'].str.replace(r'[^\w\s]+', '')
    df3['Moderna'] = df3['Moderna'].str.replace(r'[^\w\s]+', '')
    df3['Sinopharm'] = df3['Sinopharm'].str.replace(r'[^\w\s]+', '')
    df3['Nanocovax'] = df3['Nanocovax'].str.replace(r'[^\w\s]+', '')
    df3['Sinovac'] = df3['Sinovac'].str.replace(r'[^\w\s]+', '')
    df3=df3.fillna(0)
    df3[['AstraZeneca','Pfilzer','Moderna','Sinopharm','Nanocovax','Sinovac']]=df3[
            ['AstraZeneca','Pfilzer','Moderna','Sinopharm','Nanocovax','Sinovac']].apply(np.int64)
    
    return Countryvaccine,vaccine,df3

layout = html.Div([
    html.Div([
        html.H4('Thống Kê COVID-19', style={'text-align': 'center', 'background-color': '#99CCFF',
                                            'border': '1px solid black',
                                            'padding': '5px',
                                            'margin': '5px',
                                            'border-radius': '10px',
                                            'box-shadow': '0 0 10px',
                                            'color': 'black'})
    ], className='row'),
    html.P('Số liệu có thể không chính xác...........',style={
            'color':'red',
            'text-align': 'right',
            'marginRight':"3%",
            }),
    html.Div([
        html.H1(children='',
        style={
            'background-color': 'white',
            'height': '20px'
        })
        ]),
    html.Div([
        html.Div([
            html.Div([
                html.H1(children='',
                style={
                    'background-color': 'white',
                    # 'fontSize':'15',
                    'height': '17px'
                })
            ]),
            html.Div([
                html.P('Số Liệu Vaccine',style={
                    'fontSize':'20',
                    'text-align': 'center',
                    'fontWeight': 'bold',
                    }),
            ]),
            html.Div([
                html.P('',style={
                    'height':'40px'
                    }),
            ]),
            html.Div([
                html.P('Tổng số liều đã tiêm',style={
                    'text-align': 'center',
                    # 'background-color':'#00BB00',
                    # 'color':'#004400'
                    }),
                html.H4(id='total_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    'fontWeight': 'bold',
                    }),
                html.P(id='tong_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    # 'fontWeight': 'bold',
                    }),
            ],className='three columns'),
            html.Div([
                html.P('Tiêm chưa đủ mũi',style={
                    'text-align': 'center',
                    # 'background-color':'#00BB00',
                    # 'color':'#004400'
                    }),
                html.H4(id='mui1_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    'fontWeight': 'bold',
                    }),
                html.P(id='mui1%_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    # 'fontWeight': 'bold',
                    }),
            ],className='four columns'),
            html.Div([
                html.P('Tiêm đủ mũi',style={
                    'text-align': 'center',
                    # 'background-color':'#004400',
                    # 'color':'white'
                    }),
                html.H4(id='mui2_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    'fontWeight': 'bold',
                    }),
                html.P(id='mui2%_vaccine',style={
                    'color':'#007700',
                    'text-align': 'center',
                    # 'fontWeight': 'bold',
                    }),
            ],className='three columns'),
        ], className='six columns'),
        html.Div([
            dcc.Loading(children=[
                dcc.Graph(id='Indicator', style={'background-color': 'white', 'width': '720px',
                                                # 'height':'px',
                                                 # 'border': '1px solid black',
                                                 # 'padding': '5px',
                                                 # 'margin': '5px',
                                                 # 'border-radius': '10px',
                                                 # 'box-shadow': '0 0 10px'
                                                 })
            ], color="#119DFF", type="bar", fullscreen=False),
        ], className='six columns')
    ], className='row'),
    html.Div([
        html.H1(children='',
        style={
            'background-color': 'white',
            'height': '20px'
        })
        ]),
    html.Div([
        html.Div([
            dcc.Dropdown(id='vaccine1', options=[{'label': 'Vaccine Theo Ngày', 'value': 'daily_vaccine'},
                                                    {'label': 'Các Loại Vaccine', 'value': 'type_Vaccine'}],
                        value='daily_vaccine', style={'width': '320px','background-color': '#EEEEEE',
                                               # 'border': '1px solid black',
                                               # 'padding': '1px',
                                               # 'margin': '1px',
                                               # 'border-radius': '5px',
                                               # 'box-shadow': '0 0 5px'
                                               }),
            html.Div([
                html.H1(children='',
                style={
                    'background-color': 'white',
                    'height': '25px'
                })
            ]),
            dcc.Loading(children=[dcc.Graph(id="chart", style={'background-color': 'white', 'width': '720px',
                                                                    # 'border': '1px solid black',
                                                                    # 'padding': '5px',
                                                                    # 'margin': '5px',
                                                                    # 'border-radius': '10px',
                                                                    # 'box-shadow': '0 0 10px'
                                                                    })], color="#119DFF", type="bar", fullscreen=False)
        ], className='six columns'),
            html.Div([
            dcc.Dropdown(id='DailyCases', options=[{'label': 'Chi Tiết Covid-19 Theo Ngày', 'value': 'daily'},
                                                   {'label': 'Chi Tiết Covid-19 Tích Luỹ', 'value': 'cumulative'}],
                         value='daily', style={'width': '320px',
                                                'background-color': '#EEEEEE',
                                               # 'border': '1px solid black',
                                               # 'padding': '1px',
                                               # 'margin': '1px',
                                               # 'border-radius': '5px',
                                               # 'box-shadow': '0 0 5px'
                                               }),
            html.Div([
                html.H1(children='',
                style={
                    'background-color': 'white',
                    'height': '25px'
                })
            ]),
            dcc.Loading(children=[dcc.Graph(id="line-chart", style={'background-color': 'white', 'width': '720px',
                                                                    # 'border': '1px solid black',
                                                                    # 'padding': '5px',
                                                                    # 'margin': '5px',
                                                                    # 'border-radius': '10px',
                                                                    # 'box-shadow': '0 0 10px'
                                                                    })], color="#119DFF", type="bar", fullscreen=False),
        ], className='six columns')
    ], className='row'),
    html.Div([
                html.H1(children='',
                style={
                    'background-color': 'white',
                    'height': '20px'
                })
            ]),
    html.Div([
        html.Div([
            html.Div([
                html.H1(children='Số Liệu Vaccine Theo Tỉnh thành',
                style={
                    'background-color': 'white',
                    'height': '15px',
                    'fontWeight': 'bold',
                    'text-align': 'center',
                    'fontSize': 15,

                })
            ]),
            dcc.Loading([html.Div(id='table_vaccine')], color="#119DFF", type="bar", fullscreen=False)
        ], className='six columns', style={'background-color': 'white',
                                           'width': '710px',
                                           'hmineight': '200px',
                                           # 'border': '1px solid black',
                                           # 'padding': '5px',
                                           # 'margin': '5px',
                                           # 'border-radius': '10px',
                                           # 'box-shadow': '0 0 10px'
                                           }),

        html.Div([
                html.Div([
                    html.H1(children='Số Liệu Covid-19 Theo Tỉnh Thành',
                    style={
                        'background-color': 'white',
                        'height': '15px',
                        'fontWeight': 'bold',
                        'text-align': 'center',
                        'fontSize': 15,
                    })
                ]),
                dcc.Loading(id='content',style={'background-color': 'white',
                                           'width': '710px',
                                           'hmineight': '200px',
                                           # 'border': '1px solid black',
                                           # 'padding': '5px',
                                           # 'margin': '5px',
                                           # 'border-radius': '10px',
                                           # 'box-shadow': '0 0 10px'
                                           }),
        ], className='six columns')
    ], className='row'),
    html.Div([
        html.H1(children='',
        style={
            'background-color': 'white',
            'height': '30px'
        })
    ])
])
#bảng các tỉnh thành ca nhiem
def generate_table(df):
    new = df[['state', 'confirmed','recovered', 'deaths','dailyconfirmed']]
    new.columns=['Tỉnh Thành', 'Ca Nhiễm', 'Hồi Phục','Tử Vong','Nhiễm Hôm Nay']
    return html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in new.columns],
            data=new.to_dict('records'),
            sort_action='native',
            style_cell_conditional=[
                {'if': {'column_id': 'Tỉnh Thành'},
                 'width': '250px',
                 'textAlign': 'left'}],
            style_data_conditional=[{
                'if': {'column_id': 'Hồi Phục'},
                'backgroundColor': 'rgb(152, 215, 187)',
                'color': 'black'
            },
                {
                    'if': {'column_id': 'Tử Vong'},
                    'backgroundColor': 'rgb(224, 123, 123)',
                    'color': 'black'
                },
                {
                    'if': {'column_id': 'Ca Nhiễm'},
                    'backgroundColor': 'rgb(161, 185, 215)',
                    'color': 'black'
                },
                {
                    'if': {'column_id': 'Nhiễm Hôm Nay'},
                    'backgroundColor': '#EEEEEE',
                    'color': 'black'
                }
            ],
            fixed_columns={'headers': True, 'data': 1},
            page_action='none',
            style_table={'height': '750px', 'overflowY': 'auto', 'overflowX': 'auto',
                         'minWidth': '100%'},
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'fontSize': 15, 'font-family': 'sans-serif',
                'minWidth': '80px', 'width': '150px', 'maxWidth': '120px'
            },

            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ]

    )
#bảng vaccine
def vaccine_table(df):
    new = df[['state', 'Total','Mui1', 'Mui2','ratio','ratio_2_18']]
    new.columns=['Tỉnh Thành(Vaccine)', 'Số người đã tiêm', 'Số Người tiêm mũi 1','Số người tiêm đủ 2 mũi',
    'Tỉ lệ đã tiêm ít nhẩt 1 mũi(%)','Tỉ lệ tiêm đủ trên 18 tuổi(%)']
    return html.Div([
        dash_table.DataTable(
            id='table2',
            columns=[{"name": i, "id": i} for i in new.columns],
            data=new.to_dict('records'),
            sort_action='native',
            style_cell_conditional=[
                {'if': {'column_id': 'Tỉnh Thành(Vaccine)'},
                 'width': '250px',
                 'textAlign': 'left'}],
            style_data_conditional=[{
                'if': {'column_id': 'Số người đã tiêm'},
                'backgroundColor': '#EEEEEE',
                'color': 'black'
            },
                {
                    'if': {'column_id': 'Số Người tiêm mũi 1'},
                    'backgroundColor': '#66FF99',
                    'color': 'black'
                },
                {
                    'if': {'column_id': 'Số người tiêm đủ 2 mũi'},
                    'backgroundColor': '#00AA00',
                    'color': 'black'
                },
                {
                    'if': {'column_id': 'Tỉ lệ đã tiêm ít nhẩt 1 mũi(%)'},
                    'backgroundColor': '#66FF99',
                    'color': 'black'
                },
                {
                    'if': {'column_id': 'Tỉ lệ tiêm đủ trên 18 tuổi(%)'},
                    'backgroundColor': '#00AA00',
                    'color': 'black'
                }
            ],
            # style_data={
            #     'whiteSpace': 'normal',
            #     'height': 'auto',
            # },
            fixed_columns={'headers': True, 'data': 1},
            # page_action='none',
            style_table={'height': '750px', 'overflowY': 'auto', 'overflowX': 'auto',
                         'minWidth': '100%'},
            # style_cell={
            #     'overflow': 'hidden',
            #     'textOverflow': 'ellipsis',
            #     # 'word-break': 'break-all',
            #     'fontSize': 15, 'font-family': 'sans-serif',
            #     'minWidth': '80px', 'width': '150px', 'maxWidth': '120px'
            # },
            style_cell={
                # all three widths are needed
                'minWidth': '80px', 'width': '150px', 'maxWidth': '120px',
                'fontSize': 15,
                 'font-family': 'sans-serif',
                # 'textAlign': 'left',
                'whiteSpace': 'normal',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ]

)

#biểu đồ đường tích luỹ Covid19
def cumulative(Country): 
    fig = go.Figure(
        go.Scatter(x=Country['dateymd'], y=Country['totalconfirmed'],
                   line=dict(color='Blue'), name="Nhiễm", mode='lines+markers', marker=dict(size=5))
    )
    fig.add_trace(go.Scatter(x=Country['dateymd'], y=Country['totaldeceased'],
                             line=dict(color='red'), name="Tử Vong", mode='lines+markers',
                             marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=Country['dateymd'], y=Country['totalrecovered'],
                             line=dict(color='green'), name="Hồi Phục", mode='lines+markers',
                             marker=dict(size=5)))
    fig.update_layout(
        autosize=False,
        width=700,
        height=480,
        margin=dict(
            l=1,
            r=1,
            b=1,
            t=1,
            pad=1
        ),
        paper_bgcolor="white",
        plot_bgcolor='#DDE9F5',

        xaxis=dict(showline=False, showgrid=False),
        yaxis=dict(showline=False, showgrid=False)
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                # dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig

#biểu đồ đường về số ca nhiễm theo ngày
def daily(Country):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=Country['dateymd'], y=Country['dailyconfirmed'],
        hoverinfo='x+y',
        mode='lines',
        name="Ca Nhiễm Theo Ngày",
        line=dict(color='blue'),
        fill="tozeroy",
        fillcolor='rgb(161, 185, 215)'
        # stackgroup='one'  # define stack group
    ))
    fig.add_trace(go.Scatter(
        x=Country['dateymd'], y=Country['dailyrecovered'],
        hoverinfo='x+y',
        mode='lines',
        name="Hồi Phục Theo Ngày",
        line=dict(color='green'),
        fill="tozeroy",
        fillcolor='rgb(152, 215, 187)'
        # stackgroup='one'
    ))
    fig.add_trace(go.Scatter(
        x=Country['dateymd'], y=Country['dailydeceased'],
        hoverinfo='x+y',
        mode='lines',
        name="Tử Vong Theo Ngày",
        line=dict(color='red'),
        fill="tozeroy",
        fillcolor='rgb(224, 123, 123)'
        # stackgroup='one'
    ))
    fig.update_layout(
        autosize=True,
        width=700,
        height=480,
        margin=dict(
            l=1,
            r=1,
            b=1,
            t=1,
            pad=1
        ),
        paper_bgcolor="white",
        plot_bgcolor='#DDE9F5',

        xaxis=dict(showline=False, showgrid=False),
        yaxis=dict(showline=False, showgrid=False)
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                # dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig

#vaccine số mũi theo ngày theo biểu đồ đường theo ngày
def daily_vaccine(df):
    fig = go.Figure(
        go.Scatter(x=df['date'], y=df['Mui1'],
                line=dict(color='#3399CC'), 
                # fill="tozeroy",
                # fillcolor='#99CCCC',
                stackgroup='one',
                name="Mũi 1", mode='lines', 
                marker=dict(size=5)
                )
    )
    fig.add_trace(go.Scatter(x=df['date'], y=df['Mui2'],
                             line=dict(color='#008800'), name="Mũi 2", mode='lines',
                            #  fill="tozeroy",
                            # fillcolor='#CCFFCC',
                            stackgroup='one',
                             marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=df['date'], y=df['Dailytotal'],
                            # fill="none",
                            # fillcolor='#CCFFFF',
                            stackgroup='one',
                             line=dict(color='#0000FF'), name="Tổng Số Mũi Đã Tiêm", mode='lines',
                             marker=dict(size=5)))
    fig.update_layout(
        autosize=False,
        width=700,
        height=480,
        margin=dict(
            l=1,
            r=1,
            b=1,
            t=1,
            pad=1
        ),
        paper_bgcolor="white",
        plot_bgcolor='#DDDDDD',

        xaxis=dict(showline=False, showgrid=False),
        yaxis=dict(showline=False, showgrid=False)
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                # dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig
#biêu đồ tròn vaccine
def type_Vaccine(df):
    labels = ['AstraZeneca','Pfilzer','Moderna','Sinopharm','Nanocovax','Sinovac']
    values=[]
    for i in labels:
        values.append(df[i][0:-1].sum())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                 insidetextorientation='radial'
                                )])
    fig.update_layout(
        autosize=False,
        width=620,
        height=380,
        margin=dict(
            l=1,
            r=1,
            b=1,
            t=1,
            pad=1
        )
        # paper_bgcolor="white",
        # plot_bgcolor='#DDE9F5',
        # xaxis=dict(showline=False, showgrid=False),
        # yaxis=dict(showline=False, showgrid=False)
    )
    return fig

#gọi ra đồ thị về số liệu vaccine
@app.callback(Output('chart', 'figure'),
            [Input('vaccine1', 'value')], [State('vaccine1', 'value')])   
def vaccine_panel(value,val):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        if value == 'daily_vaccine':
            fig = daily_vaccine(vaccine)
        else:
            fig = type_Vaccine(type_vaccine)
        return fig
    except:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        if value == 'daily_vaccine':
            fig = daily_vaccine(vaccine)
        else:
            fig = type_Vaccine(type_vaccine)
        return fig

#goi ra bang vaccine
@app.callback(Output('table_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])   
def vaccine_panel(self):  # building the left panel of the dashboard
    try:
        
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        Table=vaccine_table(Countryvaccine)
        return Table
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        Table=vaccine_table(Countryvaccine)
        return Table

#gọi bảng và đồ thị thống kê covid19
@app.callback([Output('line-chart', 'figure'),
               Output('content', 'children')],
              [Input('Store-Data', 'children'),
               Input('DailyCases', 'value')], [State('DailyCases', 'value')])
def covid_panel(jsonified_cleaned_data, value, val):  # building the left panel of the dashboard
    try:
        datasets = json.loads(jsonified_cleaned_data) # loi o day phai khong
        Country = pd.read_json(datasets['Country'], orient='split')
        state_wise = pd.read_json(datasets['state_wise'], orient='split')
        if value == 'cumulative':
                fig = cumulative(Country)
        else:
                fig = daily(Country)

        Table = generate_table(state_wise)
        return fig, Table
    except:
        time.sleep(5)
        datasets = json.loads(jsonified_cleaned_data)
        Country = pd.read_json(datasets['Country'], orient='split')
        state_wise = pd.read_json(datasets['state_wise'], orient='split')
        if value == 'cumulative':
            fig = cumulative(Country)
        else:
            fig = daily(Country)
        Table = generate_table(state_wise)
        return fig, Table

#màu bản đồ
color_scale = {'confirmed': 'Blues', 'recovered': 'greens', 'deaths': 'Reds'}

#bản đồ
def map(state_wise, value): 
    fig = go.Figure(data=go.Choropleth(
        locations=state_wise['state_EN'][0:-1],  #tỉnh
        z=state_wise[value][0:-1],  # Dữ liệu để hiển thị màu

        geojson=vietnam_geojson,
        featureidkey='properties.Name_EN',
        colorscale=color_scale[value],
    ))

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title_text=f"COVID-19 {value} in VIETNAM by State",
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    )
    fig.update_traces(showscale=True, colorbar=dict(len=0.5))
    return fig

#gọi ra bảng tăng giảm
@app.callback(Output('Indicator', 'figure'),
              Input('Store-Data', 'children'))
def covid_panel(jsonified_cleaned_data):
    datasets = json.loads(jsonified_cleaned_data)
    Country = pd.read_json(datasets['Country'], orient='split')
    state_wise = pd.read_json(datasets['state_wise'], orient='split')
    LastUpdatedTime = state_wise['lastupdatedtime'][0]
    fig = make_subplots(rows=1, cols=3,
                        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]])
    fig.add_trace(
        go.Indicator(
            value=Country['dailyconfirmed'].sum(),
            mode="number+delta",
            delta={"reference": int(Country['dailyconfirmed'][0:-1].sum()), "valueformat": ".0f"},
            title={'text': "Tổng Ca Nhiễm"},
            delta_increasing_color='red',
            number_font_color='blue',
            number_valueformat="string"), row=1, col=1
    )
    fig.add_trace(go.Indicator(
        value=Country['dailyrecovered'].sum(),
        mode="number+delta",
        delta={"reference": int(Country['dailyrecovered'][0:-1].sum()), "valueformat": ".0f"},
        title={'text': "Tổng ca Khỏi Bệnh"},
        number_font_color='green'), row=1, col=2)
    fig.add_trace(go.Indicator(
        value=Country['dailydeceased'].sum(),
        mode="number+delta",
        delta={"reference": int(Country['dailydeceased'][0:-1].sum()),"valueformat": ".0f"},
        title={'text': "Tổng ca Tử Vong"},
        delta_increasing_color='black',
        number_font_color='red',
        number_valueformat="string"), row=1, col=3)
    fig.update_traces(number_font_size=30, title_font_size=15)
    fig.update_layout(height=350, width=700, title=f'Thời Gian Cập Nhập: {str(LastUpdatedTime)}')
    return fig
m=1000000
@app.callback(Output('total_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Dailytotal'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Dailytotal'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans
@app.callback(Output('mui1_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Mui1'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Mui1'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans

@app.callback(Output('mui2_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Mui2'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=np.sum(vaccine['Mui2'])
        k=round(k/m,1)
        ans=str(k)+'M'
        return ans
@app.callback(Output('tong_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Dailytotal']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Dailytotal']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans

@app.callback(Output('mui1%_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Mui1']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Mui1']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans
@app.callback(Output('mui2%_vaccine', 'children'),
            [Input('intervals1', 'n_intervals')])
def vaccine_up(self):
    try:
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Mui2']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans
    except:
        time.sleep(5)
        Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
        k=int(np.sum(vaccine['Mui2']))
        p=np.sum(Countryvaccine['Population'])
        x=round((k/p)*100,2)
        ans=str(x)+'%'+' dân số'
        return ans

















