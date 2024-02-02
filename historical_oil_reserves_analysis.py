import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import holoviews as hv
import panel as pn
import param
import seaborn as sns
pn.extension('plotly',template='fast')
import json
import folium as fm
import plotly.express as px
from branca.element import Element, Figure, Html, MacroElement
from jinja2 import Template
from folium.plugins import AntPath
import plotly.io as pio
import base64
pn.state.template.title = "Historical Oil Reserves Analysis"

# Layout code
portfolio_button = pn.widgets.Button(name='Identify Nudges', button_type='primary').servable(area='sidebar')
historical_oil_reserves_button =  pn.widgets.Button(name='Analyze Historical Oil Reserves', button_type='primary').servable(area='sidebar')
hawk_oil_reserves_button = pn.widgets.Button(name='Analyze Current Oil Reserves', button_type='primary').servable(area='sidebar')




oil_level_df = pd.read_excel('nrg_cb_oil__custom_2059893_page_spreadsheet.xlsx',index_col=0)
oil_by_country_df = oil_level_df
#oil_level_df[cols_list] = oil_level_df[cols_list].apply(pd.to_numeric, errors='coerce', axis=1)
oil_level_df = oil_level_df.melt(ignore_index=False).reset_index()
oil_level_df.rename(columns={'variable':'year','TIME':'country Name'},inplace=True)

continent_items = ['Asia','Europe','North America','South America','Antarctica','Africa','Australia']
country_items = ['India',"Pakistan"]
continent_button = pn.widgets.MenuButton(name='Country', items=continent_items, button_type='primary')
continent_selector = pn.widgets.Select(value='Asia', options= continent_items, css_classes=['panel-widget-box'])
country_selector = pn.widgets.Select(value='India', options= country_items, css_classes=['panel-widget-box'])

print("Continent",continent_selector.value)

def extract_geojson():
    with open('world-countries.json','r') as f:
        return json.loads(f.read())

country_geo = extract_geojson()
def filter_by_country(country_name):
    for country in country_geo['features']:
        if country['properties']['name'] == country_name:
            return country

def get_latitude_longitude_data():
    df = pd.read_excel('latitude_longitude.xlsx')
    return df

def plot_oil_levels(country):
        if country in ['Belgium', 'Bulgaria', 'Czechia', 'Denmark', 'Germany', 'Estonia','Ireland', 'Greece', 'Spain', 'France', 'Croatia', 'Italy', 'Cyprus','Latvia', 'Lithuania', 'Luxembourg', 'Hungary', 'Malta', 'Netherlands','Austria', 'Poland', 'Portugal', 'Romania', 'Slovenia', 'Slovakia','Finland', 'Sweden', 'Iceland', 'Liechtenstein', 'Norway','United Kingdom', 'Montenegro', 'North Macedonia', 'Albania', 'Serbia','Türkiye', 'Bosnia and Herzegovina','Kosovo','Moldova', 'Ukraine', 'Georgia']:
            plt.figure(figsize=(15,3))
            print(oil_by_country_df.loc[country])
            ax = sns.lineplot(oil_by_country_df.loc[country])
            ax.set(xlabel='Year', ylabel='Production barrels')
            return ax

class CustomMapViewer(param.Parameterized):
    continent_items = ['Asia','Europe','North America','South America','Antarctica','Africa','Australia']
    continent = param.ObjectSelector(default='Asia', objects=continent_items)
    country = param.ObjectSelector(default='Afghanistan', objects= ['Afghanistan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Burma (Myanmar)', 'Cambodia', 'China', 'East Timor', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Korea, North', 'Korea, South', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Nepal', 'Oman', 'Pakistan', 'Philippines', 'Qatar', 'Russian Federation', 'Saudi Arabia', 'Singapore', 'Sri Lanka', 'Syria', 'Tajikistan', 'Thailand', 'Turkey', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'])

    def get_countries_dict():
        df = pd.read_excel('continents_countries.xlsx')
        print(df.columns)
        grouped_df = df.groupby('Continent')["Country"].apply(lambda x:list(x))
        return grouped_df.to_dict()

    def get_map(lat=20.5936832, long=78.962883, zoom_start=5):
        return fm.Map(location=[lat,long], zoom_start=zoom_start)

    _countries = get_countries_dict()
    print(_countries)

    @param.depends('continent', watch=True)
    def _update_countries(self):
        countries = self._countries[self.continent]
        self.param['country'].objects = countries
        self.country = countries[0]

    map = get_map()

    @param.depends('country')
    def view(self):
        print(self.country)
        lat_long_info = get_latitude_longitude_data()
        lat_info = lat_long_info[lat_long_info['name'] == self.country]['latitude'].item()
        long_info = lat_long_info[lat_long_info['name'] == self.country]['longitude'].item()
        print(lat_info,long_info)
        map = fm.Map(location=[lat_info,long_info], zoom_start=5)
        res = plot_oil_levels(self.country)
        print(res)
        html = '''<p> Info available for EU countries only at this time. Please select any EU country to see the status of Crude oil reserves. </p>'''

        if res is not None:
            #res.show()
            print("Hello")
            fig = res.get_figure()
            #return fig
            name = self.country+'.png'
            fig.savefig('images/'+name)
            print("Jp")
            #res.write_html(self.country+'.html')
            #with open(self.country+'.html','r') as f:
            #    html = f.read()
            encoded =  base64.b64encode(open('images/'+name, 'rb').read())
            html = '<img src="data:image/png;base64,{}">'.format
            print(html)
            iframe = fm.IFrame(html(encoded.decode('UTF-8')), width=500, height=400)
            popup = fm.Popup(iframe,max_width=800)
            marker = fm.Marker([lat_info, long_info],popup=popup).add_to(map)
        else:
            iframe = fm.IFrame(html, width=400, height=80)
            popup = fm.Popup(iframe,max_width=500)
            marker = fm.Marker([lat_info, long_info],popup=popup).add_to(map)

        fm.Choropleth(
        geo_data= filter_by_country(self.country),
        name="choropleth",
        key_on="feature.properties.name",
        fill_color="YlGn",
        fill_opacity=0.2,
        line_opacity=0.9,
        legend_name="Unemployment Rate (%)",
        ).add_to(map)
        fm.LayerControl().add_to(map)
        return map

the_map = fm.Map(tiles="cartodbpositron")
fm.Choropleth(
    geo_data=country_geo,
    name='choropleth',
    columns=['country', 'orders'],
    key_on='feature.id',
    fill_color='Blues',
    nan_fill_color='white',
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(the_map)

def plot_plotly_express(continent):
    print("Plotly",continent)
    fig = px.choropleth(oil_level_df,
                    locations = "country Name",
                    locationmode="country names",
                    color = 'value',
                    color_continuous_scale="Viridis",
                    scope=continent,
                    animation_frame='year') #make sure 'period_begin' is string type and sorted in ascending order
    fig.update_layout(
        autosize=True,
        width=700,
        height=500,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=10,
            pad=1
        ),
    )
    return fig

def update_value(event):
    continent = event.new
    print(event.new)
    plot_plotly_express(event.new.lower())

viewer = CustomMapViewer()
s = pn.panel(viewer.view,height=400,width=650,min_width=550)
n = pn.panel(plot_plotly_express('europe'))
continent_selector = pn.widgets.Select(value='Europe',options = continent_items, disabled_options= ['Asia','Africa','North America','South America','Antarctica','Australia'], css_classes=['panel-widget-box'])
continent_selector.param.watch(update_value,'value')

pn.Row(pn.Column(pn.pane.Markdown('# Oil Inventory Levels by Country', style={'font-family': "serif",'font-size':'14px','color':'#1a53ff'}),viewer.param,s,background='WhiteSmoke',sizing_mode='stretch_width'),pn.layout.Spacer(width=5),pn.Column(pn.pane.Markdown('# Running Map of Oil Reserves at Continent', style={'font-family': "serif",'padding-left':'15%','font-size':'14px','color':'#1a53ff'}),continent_selector,n,background='WhiteSmoke',sizing_mode='stretch_width'),sizing_mode='stretch_width').servable(area='main')