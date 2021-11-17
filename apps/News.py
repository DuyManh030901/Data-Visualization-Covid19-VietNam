from GoogleNews import GoogleNews
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from datetime import date, timedelta

from app import app 

layout = html.Div([
    html.Div([
        html.H4('Tin Tức', style={'text-align': 'center', 'background-color': '#99CCFF',
                               'border': '1px solid black',
                               'padding': '5px',
                               'margin': '5px',
                               'border-radius': '10px',
                               'box-shadow': '0 0 10px',
                               'color': 'black'})
    ], className='row'),
    html.Div([
        dcc.Loading(children=[html.Div(id="News")], color="#119DFF", type="bar", fullscreen=False)
    ], className='row', style={'background-color': 'white',
                               'border': '1px solid black',
                               'padding': '5px',
                               'margin': '5px',
                               'border-radius': '10px',
                               'box-shadow': '0 0 10px',
                               'min-height': '200px'
                               }),

    dcc.Dropdown(id="Hidden", style={'display': 'none'})
])


@app.callback(Output("News", 'children'),
              [Input("Hidden", 'value'), Input('intervals1', 'n_intervals')])
def news_data(value, n):
    #tìm kiếm bài viết thế giới
    try:
        googlenews = GoogleNews(lang='en')
        googlenews.set_time_range(start=date.today() - timedelta(days=1), end=date.today())
        googlenews.get_news('Covid Viet Nam')
        data = pd.json_normalize(googlenews.results()[:5])
    except:  # For Country news if the above one fails
        googlenews = GoogleNews(lang='en')
        googlenews.set_time_range(start=date.today() - timedelta(days=1), end=date.today())
        googlenews.get_news('Covid 19 Việt Nam')
        data = pd.json_normalize(googlenews.results()[:5])
    #bài viết việt nam
    try: 
        googlenews = GoogleNews(lang='vi')
        googlenews.set_time_range(start=date.today() - timedelta(days=1), end=date.today())
        googlenews.get_news('Việt Nam Covid-19')
        data1 = pd.json_normalize(googlenews.results()[:5])
    except:  # For Country news if the above one fails
        googlenews = GoogleNews(lang='vi')
        googlenews.set_time_range(start=date.today() - timedelta(days=1), end=date.today())
        googlenews.get_news('Việt Nam với Covid19')
        data1 = pd.json_normalize(googlenews.results()[:5])


    return html.Div([
        html.Div([
            html.H3(data['title'][0], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data['date'][0], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data['link'][0], style={'float': 'right','color':'#0033CC'}, target="_blank"),

        ], className='twelve columns', style={'background-color': '#FFFFCC',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data1['title'][0], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data1['date'][0], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data1['link'][0], style={'float': 'right','color':'#0033CC'}, target="_blank"),

        ], className='twelve columns', style={'background-color': '#CCFFFF',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data['title'][1], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data['date'][1], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data['link'][1], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#FFFFCC',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data1['title'][1], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data1['date'][1], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data1['link'][1], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#CCFFFF',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data['title'][2], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data['date'][2], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data['link'][2], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#FFFFCC',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data1['title'][2], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data1['date'][2], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data1['link'][2], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#CCFFFF',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data['title'][3], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data['date'][3], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data['link'][3], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#FFFFCC',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data1['title'][3], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data1['date'][3], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data1['link'][3], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#CCFFFF',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px'
                                              }),
        html.Div([
            html.H3(data1['title'][4], style={'text-align': 'center', 'font-family': 'sans-serif', 'font-weight': 'bold'}),
            html.P(data1['date'][4], style={'float': 'left'}),
            html.A("Link to News ", href="https://"+data1['link'][4], style={'float': 'right','color':'#0033CC'}, target="_blank")
        ], className='twelve columns', style={'background-color': '#FFFFCC',
                                              'border': '1px solid black',
                                              'padding': '5px',
                                              'margin': '5px',
                                              'border-radius': '10px',
                                              'box-shadow': '0 0 10px',
                                              'Align': 'center'
                                              })

    ], className='row')
