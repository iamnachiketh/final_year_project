import panel as pn
pn.extension('plotly',template='fast')
import time
pn.state.template.title = "Current Oil Reserve Satellite Analysis"
def b(event):
    a = 'Clicked {0} times'.format(historical_oil_reserves_button.clicks)
    print(a)


portfolio_button = pn.widgets.Button(name='Identify Nudges', button_type='primary').servable(area='sidebar')
historical_oil_reserves_button =  pn.widgets.Button(name='Analyze Historical Oil Reserves', button_type='primary').servable(area='sidebar')
hawk_oil_reserves_button = pn.widgets.Button(name='Analyze Current Oil Reserves', button_type='primary').servable(area='sidebar')

historical_oil_reserves_button.on_click(b)

'''
with open('output.json','r') as f:
    oil_levels = f.read()
oil_levels = dict(oil_levels)
'''
oil_levels = {"uk":14.912937,"denmark":79.555449498,"italy":15.78222023,"romania":52.0124,"turkey":19.06636,"Test":""}
print(type(oil_levels))
menu_items = ['Denmark','Italy','Turkey','UK','Romania']
import os
menu_button = pn.widgets.MenuButton(name='Select Country', items=menu_items, button_type='primary')
analyze_button = pn.widgets.Button(name='Analyze', button_type='primary')
pn.Column(menu_button, height=200)
image_raw = pn.pane.PNG(width=300)
image_interim = pn.pane.PNG(width=300)
image_final = pn.pane.PNG(width=300)
capacity = pn.pane.Str("",style= {'font-size':'28px','padding-left':'50%','color':'red','font-weight':'bold'})
country = "Denmark"
def b(event):
    global country
    country = event.new.lower()
    file_name = os.path.join(os.getcwd(),'satellite_images',event.new+'_raw.png')
    image_raw.object = file_name
    image_interim.object =""
    image_final.object =""

def load_interim_image(event):
    time.sleep(5)
    print(country)
    interim_file_name = os.path.join(os.getcwd(),'satellite_images',country+'_contour.png')
    output_file_name = os.path.join(os.getcwd(),'satellite_images',country+'_final.png')
    print(interim_file_name)
    image_interim.object = interim_file_name
    image_final.object = output_file_name
    capacity.object = "Current Volume in Thousand Tons: " + str(oil_levels[country])

menu_button.on_click(b)
analyze_button.on_click(load_interim_image)
print(oil_levels[country.lower()])
pn.Column(pn.Row(menu_button,pn.Column(image_raw,analyze_button),pn.Row(image_interim,image_final)),pn.Row(capacity, height=300)).servable()