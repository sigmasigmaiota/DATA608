
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc

import seaborn as sns

import pandas as pd
import numpy as np

import plotly.graph_objs as go
import flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,server=server)


all_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=boroname,spc_common,count(spc_common)' +\
        '&$group=boroname,spc_common').replace(' ', '%20')
all_trees = pd.read_json(all_url)

all_trees = all_trees[all_trees['count_spc_common']!=0]

all_trees = all_trees.drop('count_spc_common',axis=1)

mn_trees = all_trees[all_trees['boroname']=='Manhattan']
bk_trees = all_trees[all_trees['boroname']=='Brooklyn']
qu_trees = all_trees[all_trees['boroname']=='Queens']
bx_trees = all_trees[all_trees['boroname']=='Bronx']
si_trees = all_trees[all_trees['boroname']=='Staten Island']

#soql2_trees = soql2_trees[soql2_trees['count_health']!=0]
fnameDict = {'Manhattan': mn_trees['spc_common'].tolist(),
             'Brooklyn': bk_trees['spc_common'].tolist(),
             'Queens': qu_trees['spc_common'].tolist(),
             'Bronx': bx_trees['spc_common'].tolist(),
             'Staten Island': si_trees['spc_common'].tolist()}

boro_names = list(fnameDict.keys())
nestedOptions = fnameDict[boro_names[0]]

app_name = 'Trees in NYC'

app.layout = html.Div([
    html.H1("2015 NYC Street Tree Census", style={"textAlign": "center"}),
    html.Div([html.Div([dcc.Dropdown(id='product-selected2',
                                     options=[{'label': i, 'value': i} for i in boro_names],
                                     value = list(fnameDict.keys())[0]),], 
                            style={"width": "40%", "float": "left"}),
              html.Div([dcc.Dropdown(id='product-selected1')],
                            style={"width": "40%", "float": "right"}),
              #html.Hr(),
              #html.Div(id='display-selected-values')
              ]
              , className="row", style={"padding": 50, "width": "60%", "margin-left": "auto", "margin-right": "auto"}),
    html.Div([html.Div([
        #html.H3('Column 1'),
        dcc.Graph(id='my-graph')
    ], className="six columns"),
    html.Div([
        #html.H3('Column 2'),
        dcc.Graph(id='my-graph2'),
    ], className="six columns"),
    ], className = "row"),
    html.Div([html.Div([
        #html.H3('Column 2'),
        dcc.Graph(id='my-graph4'),
    ], className="six columns"),
    html.Div([
        #html.H3('Column 2'),
        dcc.Graph(id='my-graph3'),
    ], className="six columns")
    ], className = "row")

    # dcc.Link('Go to Source Code', href='{}/code'.format(app_name))
], className="container")


@app.callback(

    dash.dependencies.Output('product-selected1','options'),
    [dash.dependencies.Input('product-selected2', 'value')])


def update_species_dropdown(selected_product2):
    return [{'label': n, 'value': n} for n in fnameDict[selected_product2]]

@app.callback(
    dash.dependencies.Output('product-selected1', 'value'),
    [dash.dependencies.Input('product-selected1', 'options')])

def set_species_value(available_options):
    return available_options[0]['value']

#@app.callback(
#    dash.dependencies.Output('display-selected-values', 'children'),
#    [dash.dependencies.Input('product-selected2', 'value'),
#    dash.dependencies.Input('product-selected1','value')])

#def set_display_children(product_selected1, product_selected2):
#    return u'You have selected the {} in {}'.format(product_selected2, product_selected1)

@app.callback(

    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('product-selected2', 'value'),
    dash.dependencies.Input('product-selected1','value')])


def update_graph(product_selected1, product_selected2):

    boro = product_selected1

    tree_sel = product_selected2

    soql_url2 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$select=spc_common,health,count(health)&$where=boroname=\''+\
        boro+'\''+'&$group=spc_common,health').replace(' ','%20')

    soql_trees2 = pd.read_json(soql_url2)
    soql_trees2['count_health'] = pd.to_numeric(soql_trees2['count_health'])
    soql_trees2 = soql_trees2[soql_trees2['count_health']!=0]

    #selects major type of species
    soql_trees3 = soql_trees2[soql_trees2['spc_common'].str.contains(tree_sel,na=False)]

    soql_trees3['pct'] = round(soql_trees3['count_health']*100/(soql_trees3['count_health'].sum()),2)


    trace1 = go.Pie(labels=soql_trees3['health'],values=soql_trees3['pct'])
    #trace2 = go.Bar(x=soql_trees3['health'],y=soql_trees3['count_health'])

    return {
        'data': [trace1],
        'layout': go.Layout(
  
            title=f'{product_selected2}, {product_selected1}'

        )
    }

@app.callback(

    dash.dependencies.Output('my-graph2', 'figure'),
    [dash.dependencies.Input('product-selected2', 'value'),
    dash.dependencies.Input('product-selected1','value')])


def update_graph2(product_selected1, product_selected2):

    boro = product_selected1

    #tree_sel = product_selected2

    url2 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$select=steward,health,count(health)' +\
        '&$where=boroname=\''+boro+'\''+\
        '&$group=steward,health').replace(' ', '%20')

    trees2 = pd.read_json(url2)
    trees2['count_health'] = pd.to_numeric(trees2['count_health'])
    trees2 = trees2[trees2['count_health']!=0]

    #selects major type of species
    #trees3 = trees2[trees2['spc_common'].str.contains(tree_sel,na=False)]

    trees2['pct'] = round(trees2['count_health']*100/(trees2['count_health'].sum()),2)
    contingency_table = trees2.pivot(index='steward',
                                     columns='health',
                                     values='pct')
    column_order = ['Poor','Fair','Good']

    con_table = contingency_table.reindex(column_order, axis=1)
    con_table = con_table.div(con_table.sum(axis=1), axis=0)
    #con_table = round(con_table*100,2)
    
    con_table = con_table.reset_index()


    #trace2 = go.Pie(labels=trees3['health'],values=trees3['pct'])
    trace4 = go.Bar(x=con_table['steward'],y=con_table['Poor'],name='Poor')
    trace3 = go.Bar(x=con_table['steward'],y=con_table['Fair'],name='Fair')
    trace2 = go.Bar(x=con_table['steward'],y=con_table['Good'],name='Good')
    

    return {
        'data': [trace2,trace3,trace4],
        'layout': go.Layout(

            barmode = 'stack',
            #showlegend=False,
  
            title=f'Stewardship, all species in {product_selected1}',
            xaxis={'title': "Stewardship Observed", 'titlefont': {'color': 'black', 'size': 14},
            'tickfont': {'size': 12, 'color': 'black'}},
            yaxis={'tickfont': {'color': 'black'}, 'tickformat':"%"}

        )
    }

@app.callback(

    dash.dependencies.Output('my-graph3', 'figure'),
    [dash.dependencies.Input('product-selected2', 'value'),
    dash.dependencies.Input('product-selected1','value')])


def update_graph3(product_selected1, product_selected2):

    #boro = product_selected1

    tree_sel = product_selected2

    urlb = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$select=steward,health,count(health)' +\
        '&$where=spc_common=\''+tree_sel+'\''+\
        '&$group=steward,health').replace(' ', '%20')

    trees2b = pd.read_json(urlb)
    trees2b['count_health'] = pd.to_numeric(trees2b['count_health'])
    trees2b = trees2b[trees2b['count_health']!=0]

    #selects major type of species
    #trees3 = trees2[trees2['spc_common'].str.contains(tree_sel,na=False)]

    trees2b['pct'] = round(trees2b['count_health']*100/(trees2b['count_health'].sum()),2)
    contingency_tableb = trees2b.pivot(index='steward',
                                     columns='health',
                                     values='pct')
    column_orderb = ['Poor','Fair','Good']

    con_tableb = contingency_tableb.reindex(column_orderb, axis=1)
    con_tableb = con_tableb.div(con_tableb.sum(axis=1), axis=0)
    #con_table = round(con_table*100,2)
    
    con_tableb = con_tableb.reset_index()


    #trace2 = go.Pie(labels=trees3['health'],values=trees3['pct'])
    trace7 = go.Bar(x=con_tableb['steward'],y=con_tableb['Poor'],name='Poor')
    trace6 = go.Bar(x=con_tableb['steward'],y=con_tableb['Fair'],name='Fair')
    trace5 = go.Bar(x=con_tableb['steward'],y=con_tableb['Good'],name='Good')
    

    return {
        'data': [trace5,trace6,trace7],
        'layout': go.Layout(

            barmode = 'stack',
            #showlegend=False,
  
            title=f'Stewardship, {product_selected2} in all Boroughs',
            xaxis={'title': "Stewardship Observed", 'titlefont': {'color': 'black', 'size': 14},
            'tickfont': {'size': 12, 'color': 'black'}},
            yaxis={'tickfont': {'color': 'black'}, 'tickformat':"%"}

        )
    }

@app.callback(

    dash.dependencies.Output('my-graph4', 'figure'),
    [dash.dependencies.Input('product-selected2', 'value'),
    dash.dependencies.Input('product-selected1','value')])


def update_graph4(product_selected1, product_selected2):

    boro = product_selected1

    #tree_sel = product_selected2

    urlt = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$select=spc_common,health,count(health)' +\
        '&$where=boroname=\''+boro+'\''+\
        '&$group=spc_common,health').replace(' ', '%20')

    trees2t = pd.read_json(urlt)
    trees2t['count_health'] = pd.to_numeric(trees2t['count_health'])
    trees2t = trees2t[trees2t['count_health']!=0]

    trees3t = trees2t.sort_values('count_health',ascending=False)
    trees4t = trees3t.head(5)

    trace8 = go.Bar(x=trees4t['count_health'],y=trees4t['spc_common'],orientation='h')
    

    return {
        'data': [trace8],
        'layout': go.Layout(

            #barmode = 'stack',
            showlegend=False,
  
            title=f'Top Five Most Populous Species in {product_selected1}',
            xaxis={'title': "Count", 'titlefont': {'color': 'black', 'size': 14},
            'tickfont': {'size': 12, 'color': 'black'}},
            yaxis={'title':"Species",'titlefont': {'color': 'black', 'size': 14},'tickfont': {'size':8,'color': 'black'}}

        )
    }
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run_server(host='0.0.0.0',port=port)