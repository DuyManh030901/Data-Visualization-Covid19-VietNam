import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.validator_cache
import pandas as pd
import requests
import json
import unidecode

from datetime import datetime
import datetime
import numpy as np
from app import app
from app import server
from apps import dashboard, predictions, News

app.title = 'Covid19 Việt Nam'

#covid19
def load_data():  # Gọi API và làm sạch dữ liệu
	#số ca theo ngày 
	content1=pd.read_csv("https://vnexpress.net/microservice/sheet/type/covid19_2021_by_day")
	df = pd.DataFrame(content1,
						columns=['new_cases', 'new_deaths', 'new_recovered', 'day_full', 'total_cases',
									'total_deaths',
									'total_recovered_12'])
	date_object = pd.to_datetime(datetime.date.today())
	df['day_full'] = pd.to_datetime(df['day_full'])
	Country=df[(df['day_full']<date_object)]
	Country.columns=['dailyconfirmed', 'dailydeceased', 'dailyrecovered','dateymd','totalconfirmed', 'totaldeceased',
		 'totalrecovered']
	Country[['dailyconfirmed', 'dailydeceased', 'dailyrecovered', 'totalconfirmed', 'totaldeceased',
			 'totalrecovered']] = Country[
		['dailyconfirmed', 'dailydeceased', 'dailyrecovered', 'totalconfirmed', 'totaldeceased',
		 'totalrecovered']].apply(np.int64)

	#theo tỉnh
	response = requests.get("https://static.pipezero.com/covid/data.json")
	content2 = json.loads(response.text)
	state_wise = pd.DataFrame(content2['locations'],
							  columns=['cases', 'death', 'casesToday',
									  'name'])
	state_wise['recovered']=(state_wise['cases']-state_wise['death'])*3/5
	state_wise['recovered']=state_wise['recovered'].apply(np.int64)
	state_wise['dateupdaute']=pd.to_datetime(datetime.date.today())
	state_wise=state_wise[['recovered','cases','death','casesToday','dateupdaute','name']]
	state_wise.columns=['recovered','confirmed','deaths','dailyconfirmed','lastupdatedtime','state']
	state_wise[['recovered','confirmed','deaths','dailyconfirmed']]=state_wise[
		['recovered','confirmed','deaths','dailyconfirmed']].apply(np.int64)
	state_wise['lastupdatedtime'] = pd.to_datetime(state_wise['lastupdatedtime'])
	#sửa phù hợp file geojson
	state_wise["state_EN"]=state_wise["state"]
	states = []
	for i in state_wise["state_EN"]:
		if i == 'Thừa Thiên Huế':
			states.append('Thua Thien - Hue')
		elif i == "Khánh Hòa":
			states.append("Khanh Hoa")
		elif i=="Kiên Giang":
			states.append("Kien Giang")
		else:
			states.append(unidecode.unidecode(i))
	state_wise["state_EN"]=states
	state_wise=state_wise.append({'recovered':0,'confirmed':0,'deaths':0,'dailyconfirmed':0,'lastupdatedtime':0,
				   'state':'Hoàng sa','state_EN':'Hoang Sa (Da Nang)'},ignore_index=True)
	state_wise=state_wise.append({'recovered':0,'confirmed':0,'deaths':0,'dailyconfirmed':0,'lastupdatedtime':0,
				   'state':'Trường sa','state_EN':'Truong Sa (Khanh Hoa)'},ignore_index=True)
	return Country, state_wise

# def bottom1():
# 	return html.Div([
# 		html.Div([
# 			html.H6('')
# 		], className='five columns'),
# 		html.Div([
# 			html.A("Facebook", href='https://www.facebook.com/duymanh030901/', target="_blank",
# 				   style={'background-color': '#99CCFF', 'height': '70px',
# 						  'border': '1px solid black',
# 						  'padding': '5px',
# 						  'margin': '5px',
# 						  'border-radius': '2px',
# 						  'box-shadow': '0 0 10px',
# 						  'text-align': 'center',
# 						  'color': 'black'
# 						  }
# 				   )
# 		], className='one column'),
# 		html.Div([
# 			html.A("GitHub", href='https://github.com/DuyManh030901', target="_blank",
# 				   style={'background-color': '#99CCFF', 'height': '70px',
# 						  'border': '1px solid black',
# 						  'padding': '5px',
# 						  'margin': '5px',
# 						  'border-radius': '2px',
# 						  'box-shadow': '0 0 10px',
# 						  'text-align': 'center',
# 						  'color': 'black'
# 						  })
# 		], className='one column'),
# 		html.Div([
# 			html.H6('')
# 		], className='six columns')
# 	], className='row')


# FRONT-END LAYOUT

app.layout = html.Div([
	html.Div([
		html.Img(
			src="../assets/virus.png",
			style={
				'height': '50px',
				'float': 'right',
				'width': '50px',
				'background-color': 'while',
				'border': '1px solid white',
				'border-radius': '50%',
				'display': 'inline',
				'box-shadow': '0 0 5px'
			}
		),
		html.H1(children='Theo Dõi COVID-19 Việt Nam', style={'text-align': 'center',
														  'color': 'black'}),
		html.P("(Việt Nam sẽ chiến thắng COVID-19)", style={'text-align': 'center',
															 'color': 'black'})
	], className='row',style={'text-align': 'center', 'background-color': '#99CCFF',
											'border': '1px solid black',
											'padding': '5px',
											'margin': '5px',
											'border-radius': '10px',
											'box-shadow': '0 0 10px',
							   }),
	# div ẩn lưu trữ các giá trị trung gian 
	dcc.Dropdown(id='data', style={'display': 'none'}),
	html.Div(id='Store-Data', style={'display': 'none'}),
	dcc.Location(id='url', refresh=True),

	html.Div([
		html.Div([
			dcc.Link("Thống Kê", href='/apps/dashboard', style={'text-align': 'center',
																 'fontSize': 20,
																 'font-family': 'sans-serif',
																 'background-color': '#99CCFF',
																 'height': '50px',
																 'width': '510px',
																 'border': '1px solid black',
																 'padding': '5px',
																 'margin': '5px',
																 'border-radius': '5px',
																 'box-shadow': '0 0 10px grey',
																 'color': 'black'
																 }, className='four columns'),
			dcc.Link("Dự Đoán", href='/apps/predictions', style={'text-align': 'center',
																	 'fontSize': 20,
																	 'font-family': 'sans-serif',
																	 'background-color': '#99CCFF',
																	 'height': '50px',
																	 'width': '510px',
																	 'border': '1px solid black',
																	 'padding': '5px',
																	 'margin': '5px',
																	 'border-radius': '5px',
																	 'box-shadow': '0 0 10px grey',
																	 'Align': 'center',
																	 'color': 'black'
																	 }, className='four columns'),
			dcc.Link("Tin Tức", href='/apps/News', style={'text-align': 'center',
																	 'fontSize': 20,
																	 'font-family': 'sans-serif',
																	 'background-color': '#99CCFF',
																	 'height': '50px',
																	 'width': '510px',
																	 'border': '1px solid black',
																	 'padding': '5px',
																	 'margin': '5px',
																	 'border-radius': '5px',
																	 'box-shadow': '0 0 10px grey',
																	 'Align': 'center',
																	 'color': 'black'
																	 }, className='four columns')
		], className='row'),

	]),
	# Nội dung của trang
	html.Div(id='page-content', children=[]),

	html.Div([
		html.Div([
			html.H6('Nguồn Dữ Liệu & Tài Liệu Kham Thảo', style={'text-align': 'center', 'background-color': '#99CCFF',
													   'border': '1px solid black',
													   'padding': '5px',
													   'margin': '5px',
													   'border-radius': '5px',
													   'box-shadow': '0 0 10px',
													   'color': 'black',
													   })
		], className='row'),
		html.Div([
			html.P("https://vnexpress.net/covid-19/covid-19-viet-nam",
				   style={'text-align': 'center'}),
			html.P("https://dantri.com.vn/suc-khoe/dai-dich-covid-19.htm",
				   style={'text-align': 'center'}),
			html.P("Dash :  https://dash.plotly.com/",
				   style={'text-align': 'center'}),
			html.P("https://github.com/",
				   style={'text-align': 'center'}),
			# html.H6('Thông Tin Cá Nhân', style={'text-align': 'center', 'background-color': '#99CCFF',
			# 						   'border': '1px solid black',
			# 						   'padding': '5px',
			# 						   'margin': '5px',
			# 						   'border-radius': '5px',
			# 						   'box-shadow': '0 0 10px',
			# 						   'color': 'black'})
		], className='row'),

		# bottom1(),

	], style={'text-align': 'center','background-color': 'white',
			  'border': '1px solid black',
			  'padding': '5px',
			  'margin': '5px',
			  'border-radius': '10px',
			  'box-shadow': '0 0 10px'
			  }),
	dcc.Interval(
		id='intervals1',
		interval=7200 * 1000, #cập nhập 2 giờ 1 lần
		n_intervals=0
	)
])


# Lưu trữ dữ liệu div ẩn

#covid19
@app.callback(
	Output('Store-Data', 'children'),
	[Input('data', 'value'), Input('intervals1', 'n_intervals')])
def cleaned_data(value, n):
	Country, state_wise = load_data()
	datasets = {
		'Country': Country.to_json(orient='split', date_format='iso'),
		'state_wise': state_wise.to_json(orient='split', date_format='iso')
	}
	return json.dumps(datasets) 

# @app.callback(
# 	Output('Store-Data-1', 'children'),
# 	[Input('data1', 'value'), Input('intervals1', 'n_intervals')])
# def cleaned_data_1(value, n):
# 	Countryvaccine,vaccine,type_vaccine=load_data_vaccine()
# 	datasets1 = {
# 		'Countryvaccine': Countryvaccine.to_json(orient='split'),
# 		'vaccine': vaccine.to_json(orient='split',date_format='iso'),
# 		'type_vaccine': type_vaccine.to_json(orient='split')
# 	}
# 	return json.dumps(datasets1)

#This callback helps to switch between the tabs(pages)


@app.callback(Output('page-content', 'children'),
			  [Input('url', 'pathname')])
def display_page(pathname):
	if pathname == '/apps/dashboard':
		return dashboard.layout
	elif pathname == '/apps/predictions':
		return predictions.layout  # trả về bố cục
	elif pathname == '/apps/News':
		return News.layout
	else:
		return dashboard.layout  # Tổng quan 


if __name__ == '__main__':
	app.run_server(debug=False)
