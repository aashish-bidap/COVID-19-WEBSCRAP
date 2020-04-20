import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import plotly.graph_objs as go
from plotly.plotly import iplot
import plotly as py
from datetime import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output,Input

app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def scrap_table(link,id):
    results = requests.get(link)
    print(results)
    src = results.content
    soup = BeautifulSoup(src,'lxml')
    table_tag = soup.find("table", {"id" : id})
    columns = [th.text for th in table_tag.findAll('th')]
    rows_tags = table_tag.tbody.findAll('tr')
    rows = []
    for row_tag in rows_tags:
        row = [col.text for col in row_tag.findAll('td')]
        rows.append(row)
    my_data = pd.DataFrame(rows,columns=columns)
    return my_data

def clean_my_data(to_clean_data):
    for i in to_clean_data:
        to_clean_data[i] = [x.strip('\n') for x in to_clean_data[i]]
        to_clean_data[i] = [x.strip('+') for x in to_clean_data[i]]
        to_clean_data[i] = to_clean_data[i].str.replace(',','')
        to_clean_data.loc[to_clean_data[i] == 'N/A',i] = 0
    to_clean_data = to_clean_data.replace(r'^\s*$', np.nan, regex=True)
    to_clean_data.replace(np.nan,0,inplace=True)
    return to_clean_data


my_data = scrap_table("https://www.worldometers.info/coronavirus/",'main_table_countries_today')
    
my_data = clean_my_data(my_data)

my_data = my_data[(my_data['Country,Other'] != 'World')]

my_data = my_data[(my_data['Country,Other'] != '0')]

for i in my_data:
    if i in ['TotalCases','NewCases','TotalDeaths','NewDeaths','TotalRecovered','ActiveCases','Serious,Critical','Deaths/1M pop','TotalTests']:
        my_data[i]= my_data[i].apply(pd.to_numeric)

ships = ['Diamond Princess','MS Zaandam']
my_data_ships = my_data[my_data['Country,Other'].isin(ships)]

my_data = my_data[~my_data['Country,Other'].isin(ships)]

my_data_Countries = my_data[my_data.TotalTests != 0]

my_data1 = my_data_Countries.sort_values('TotalCases',ascending=False).nlargest(10,'TotalCases')
my_data2 = my_data_Countries.sort_values('NewCases',ascending=False).nlargest(10,'NewCases')

Active_cases = my_data_Countries.ActiveCases.sum()
total_recover = my_data_Countries.TotalRecovered.sum()
total_deaths = my_data_Countries.TotalDeaths.sum()

total = ['Active Cases', 'Total Deaths', 'Total Recovered']
values = [Active_cases,total_deaths,total_recover]

data1 = {
   		"values": values,
   		"labels": total,
   		"domain": {"column": 0},
	    "name": "COVID-19 Cases",
	    #"hoverinfo":"label+percent+name",
	    "hole": .4,
	    "type": "pie"
		}
#print(my_data_Countries.head())
markdown_text0 = '''
The CORONAVIRUS COVID-19 has affected 210 countries across the world and its spread has created a major shift in the world economy. 
Below are statistics for the number of coronavirus incidents reported across the world.
'''

markdown_text1 = '''
Below graph shows the Total Active number,Total Deaths and Total Recovered coronavirus cases found across the Top 10 majorly impacted countries by total active cases.
'''

markdown_text2 = '''
Below graph shows the New Active Cases,New reported Deaths and Newly Recovered cases found across the Top 10 majorly impacted countries by newly found cases.
'''

markdown_text4 = '''
Below graph shows the COVID numbers for your selected country.
'''

markdown_text3 = '''
Below pie chart shows percentage distribution of the Total Cases of Coronovirus of over world.
'''

markdown_source = '''
Source:https://www.worldometers.info/coronavirus/country/
'''

app.layout = html.Div([
	html.Div(children=[
    html.H1(children='Learn More about COVID-19 Data.')
    ]),

    html.Div(children=[
    	html.H3(children=markdown_text0)
    	]),

	html.Div([
	dcc.Markdown(children=markdown_text1),
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                go.Bar(
                x = my_data1['Country,Other'],
                y = my_data1['TotalCases'],
                name = "TotalCases",
                marker = dict(color = 'rgb(227,26,28)',line=dict(color='rgb(227,26,28)',width=1.5)),
                ),
                go.Bar(
				x = my_data1['Country,Other'],
                y = my_data1['TotalDeaths'],
                name = "TotalDeaths",
                marker = dict(color = 'rgb(51,160,44)',line=dict(color='rgb(51,160,44)',width=1.5))
                ),
                go.Bar(
                x = my_data1['Country,Other'],
                y = my_data1['TotalRecovered'],
                name = "TotalRecovered",
                marker = dict(color = 'rgb(166,206,300)',
                             line=dict(color='rgb(166,206,227)',width=1.5))
                ),
            ],
            'layout': go.Layout(barmode = "group",title = 'Values for Top 10 Majorly Impacted Countries.')
        }
    )
],
style = {'display': 'inline-block', 'width': '48%'}),
	html.Div([
	dcc.Markdown(children=markdown_text2),
	dcc.Graph(
		id='abcd',
		figure={
			'data':[
				go.Bar(
            	x = my_data2['Country,Other'],
           		y = my_data2['NewCases'],
            	name = "NewCases",
            	marker = dict(color = 'rgb(227,26,28)',
            	line=dict(color='rgb(227,26,28)',width=1.5))
            	),
				go.Bar(
                x = my_data2['Country,Other'],
                y = my_data2['NewDeaths'],
                name = "NewDeaths",
                marker = dict(color = 'rgb(51,160,44)',
                             line=dict(color='rgb(51,160,44)',width=1.5)),
                text = my_data2['Country,Other']),
				],
				'layout':go.Layout(barmode = "group",title='Values for Top 10 Country Cases for Today.')
			}

		)	

	],
	style={'width': '48%', 'align': 'right', 'display': 'inline-block'}),
	
	html.Div([
	dcc.Markdown(children=markdown_text4),
	dcc.Dropdown(
		id='dropdown',
        options=[{'label': x,'value': x } for x in my_data_Countries['Country,Other']],
        multi=True,
        value=['USA','India'],
        
        
    ),
    dcc.Graph(
        id='life-exp-vs-gdp_dropdown',
        
    ),
	],
	style={'width': '48%', 'align': 'right', 'display': 'inline-block'}),
	
	html.Div([
	dcc.Markdown(children=markdown_text3),
	dcc.Graph(
		
		id='pie',
		figure={
			'data':[data1],
			'layout':go.Layout(
   			{
		      "title":"Total COVID-19 Cases",
		      "grid": {"rows": 1, "columns": 1},
		      "annotations": [
		      {
	            "font": {
	               "size": 18
	            },
	            "showarrow": False,
	            "text":'               Total Cases',
	            "x": 0.16,
	            "y": 0.5
	         },
	         {
	            "font": {
	               "size": 15
	            },
	            "showarrow": False,
	            "text": "",
	            "x": 0.6,
	            "y": 0.5
	         }
     	 ]}
		)}

	),
	],
	style={'width': '48%', 'display': 'inline-block'}),

	html.Div(children=[
    html.H4(children='Source:https://www.worldometers.info/coronavirus/country/')
    ]),

])


@app.callback(dash.dependencies.Output("life-exp-vs-gdp_dropdown","figure"),
    [dash.dependencies.Input("dropdown","value")]
    )

def update_graph(input_value):

    if input_value == []:
        df = my_data_Countries.loc[my_data_Countries['Country,Other'].isin('India','USA')]	
    else:
        df = my_data_Countries.loc[my_data_Countries['Country,Other'].isin(input_value)]    
    data=[]
    trace_close1 = go.Bar(
                    x = df['Country,Other'],
                    y = df['TotalCases'],
                    name = "TotalCases",
                    marker = dict(color = 'rgb(227,26,28)',line=dict(color='rgb(227,26,28)',width=2.5)),
                  )
   
    trace_close2 = go.Bar(
                    x = df['Country,Other'],
                    y = df['TotalDeaths'],
                    name = "TotalDeaths",
                    marker = dict(color = 'rgb(51,160,44)',line=dict(color='rgb(51,160,44)',width=5.5)),
                  )
    trace_close3 = go.Bar(
                    x = df['Country,Other'],
                    y = df['TotalRecovered'],
                    name = "TotalRecovered",
                    marker = dict(color = 'rgb(166,206,300)',line=dict(color='rgb(166,206,227)',width=0.5)),
                  )
    data.append(trace_close1)
    data.append(trace_close2)
    data.append(trace_close3)

    layout = {"barmode" : "group","title" : 'Values for the selected Country.'}
    
    return {
     "data" : data,
     "layout" : layout
     }


if __name__ == '__main__':
    app.run_server()	





