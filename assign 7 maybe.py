import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

Fine_df = pd.read_csv('https://raw.githubusercontent.com/JHiggins87/assign-4/main/finedata.csv')
Fine_df.rename(columns={'Industry (Exiobase)':'Industry'},inplace=True)

Fine_df['Total Environmental Cost'] = Fine_df['Total Environmental Cost'].str.replace('(', '').str.replace(')', '').str.replace(',', '')
Fine_df['Total Environmental Cost'] = pd.to_numeric(Fine_df['Total Environmental Cost'])

Fine_df.head()


df_main = Fine_df[['Year','Industry','Country','Company Name','Total Environmental Cost']]
df_main
df_sec = Fine_df[['Year','Industry','Country','Company Name','Total Environmental Cost']]

df_unique = df_main = df_main.groupby(['Year','Industry','Country','Total Environmental Cost']).nunique()
df_unique.reset_index(inplace = True)
df_unique = df_main.groupby(['Year','Industry','Country']).sum()
df_unique.reset_index(inplace=True)

df_comp = df_sec = df_sec.groupby(['Industry','Country','Total Environmental Cost','Company Name']).nunique()
df_comp.reset_index(inplace = True)
df_comp = df_sec.groupby(['Industry','Country','Company Name']).sum()
df_comp.reset_index(inplace=True)

df_unique
df_comp.head()

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.SANDSTONE],use_pages = True, pages_folder = '')

RowT = dbc.Row(
    children= [html.H1('Environmental Cost Explorer', style={'textAlign': 'center'}),
               html.P('Select Desired Industry & Country to see their Environmental Costs and the top 10 companies that attribute to the cost')]
)
rowc = dbc.Row(
    children=[
        html.P('sources:', style={'marginBottom': '5px'}),
        html.P( 'https://www.kaggle.com/datasets/mannmann2/corporate-environmental-impact/data',style={'marginBottom': '5px'}),
        html.P('“Freiberg, David and Park, DG and Serafeim, George and Zochowski, Rob. 2020. Corporate Environmental Impact: Measurement, Data and Information. Harvard Business School, Impact-Weighted Accounts Project report.” https://www.hbs.edu/impact-weighted-accounts/Pages/default.aspx',style={'marginBottom': '5px'}),
    ]
)
row1 = dbc.Row(
    children = [ 
        dbc.Col(
           
            children=[
                dbc.Select(
                Fine_df['Country'].unique(),
                placeholder = 'Country',
                id= 'Country',value = 'France')
            ]
        ),
        dbc.Col(
            children = [
                
                dbc.Select(
                
                
                placeholder='Industry',
                id= 'Industry', value= 'Activities auxiliary to financial intermediation (67)'

                )
            ]
            
        )
    ]
)
row3 = dbc.Row(
    children= [
        dbc.Col(
            children=[
                dbc.Col(
                    dcc.Slider(
			        min=df_unique['Year'].min(),
                    max=df_unique['Year'].max(),
                    step=None,
                    id='year_slider',
                    value=df_unique['Year'].max(),
                    marks={str(year): str(year) for year in df_unique['Year'].unique()},)
		),

            ]
        )
    ]
)      
    


indlist = ['Industry']
selectind = 'Activities auxiliary to financial intermediation (67)'
selectcount = 'Canada'
countlist = ['Country']



p1 = html.Div(
    style={'margin-left': '3%', 'margin-right': '3%'},
    children=[
        RowT,
        row1,
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(dcc.Graph(id='chart'),width = 6),
                dbc.Col(dcc.Graph(id='comp chart'),width = 6)
            ]
        ),
        rowc,
    ]
)
p2 = html.Div([
    html.H1('Environmental Impact Leaders per year', style={'textAlign': 'center'}),
    dbc.Row(
        children = [
        dbc.Col(dcc.Graph(id='totchart')),    
        
        ],
        
    ),row3
]
)

dash.register_page(
    'first',
    path= '/',
    layout = p1)
dash.register_page(
    'second',
    path = '/sec',
    layout = p2
)

    

app.layout = dbc.Container(
    children= [ 
        dbc.NavbarSimple(
            brand = 'BSAN 406',
            color = 'primary',
            dark = True,
            fluid = True, 
            children = [ 
                dbc.NavItem( dbc.NavLink('first', href= '/')),
                dbc.NavItem( dbc.NavLink('second', href='/sec'))
                ]
        ),
        dash.page_container,
    ]
)


@app.callback(
    Output('Industry','options'),
    Input('Country','value')
)

def update_sel(count_selection):
    return Fine_df.query('Country == @count_selection')['Industry'].unique()





@app.callback(
     Output('chart','figure'),
     Input("Industry",'value'),
     Input('Country','value')

)

def update_graph(ind_selection, count_selection):
    if ind_selection is None:
        return {}
    if count_selection is None:
        return {}
    mysub = df_unique[(df_unique['Industry'] == ind_selection) & (df_unique['Country'] == count_selection)]
    mysub['Year'] = mysub['Year'].astype(str)

    fig = px.bar(mysub, x='Year', y='Total Environmental Cost',title= ' Total Environmental cost per year')
    fig.update_yaxes( title = None)
    return fig 

   
    
@app.callback(
    Output('comp chart','figure'),
    Input("Industry",'value'),
    Input('Country','value')
)

def update_graph(ind_selection, count_selection):
    if ind_selection is None:
        return {}
    if count_selection is None:
        return {}
    newsub = df_comp[(df_comp['Industry'] == ind_selection) & (df_comp['Country'] == count_selection)]
    newsub['Company Name'] = newsub['Company Name'].astype(str)
    top_companies = newsub.nlargest(10, 'Total Environmental Cost')
    fig = px.bar(top_companies, x='Company Name', y='Total Environmental Cost', title= ' Total Environmental cost by Company')
    fig.update_yaxes( title = None)

    return fig 

@app.callback(
    Output('totchart','figure'),
    Input('year_slider','value'),
)
def update_chart(slider_input):
    subset_df = df_unique[df_unique.Year == slider_input]
    subset_df['Country'] = subset_df['Country'].astype(str)
    top_countries = subset_df.groupby('Country')['Total Environmental Cost'].sum().nlargest(10).reset_index()
    top_countries = top_countries.reindex(range(10), fill_value=0)  
    fig = px.bar(top_countries, x='Country', y='Total Environmental Cost')
    fig.update_yaxes(title=None)
    
    return fig



# @app.callback(
# 	Output('map', 'figure'),
# 	Input('year_slider', 'value'),
# )
# def update_chart(slider_input):

#     subset_df = df_comp[df_comp['Year'] == slider_input]
#     subset_df['Year'] = subset_df['Year'].astype(str)
    
#     # Sort countries by total environmental cost (descending order)
#     subset_df = subset_df.sort_values(by='Total Environmental Cost', ascending=False)
    
#     # Get the country with the highest total environmental cost
#     highest_cost_country = subset_df.iloc[0]['Country']
    
#     count_map = px.choropleth(
#         subset_df,
#         locations='Country',
#         locationmode='country names',
#         color='Total Environmental Cost',
#         hover_name='Country',
#         hover_data={'Total Environmental Cost': True},
#         projection='natural earth',
#         color_continuous_scale='RdYlGn',
#         range_color=(subset_df['Total Environmental Cost'].min(), subset_df['Total Environmental Cost'].max()),
#     )
#     count_map.update_traces(hovertemplate='<b>%{hovertext}</b><br>Total Environmental Cost: %{customdata:,.2f}')
    
#     count_map.update_layout(
#         annotations=[
#             dict(
#                 x=0.5,
#                 y=1.15,
#                 xref='paper',
#                 yref='paper',
#                 text=f"Highest Total Environmental Cost in {slider_input}: {highest_cost_country}",
#                 showarrow=False,
#                 font=dict(size=14),
#             )
#         ],
#         coloraxis_colorbar=dict(title='Total Environmental Cost'),
#         coloraxis_colorbar_len=0.75,
#         coloraxis_colorbar_x=-0.05,
#     )

#     return count_map


    
    
if __name__ == '__main__':
    app.run(debug=True)

