
import panel as pn
'''
with open('output.json','r') as f:
    oil_levels = f.read()
oil_levels = dict(oil_levels)
'''
oil_levels = {"uk":34881.0,"denmark":3630.0,"italy":3481.0,"romania":2590.0,"turkey":"2380.0","Test":""}
print(type(oil_levels))
menu_items = ['Denmark','Italy','Turkey','UK','Romania']
import os
menu_button = pn.widgets.MenuButton(name='Select Country', items=menu_items, button_type='primary')
analyze_button = pn.widgets.Button(name='Analyze', button_type='primary')
pn.Column(menu_button, height=200)
image_raw = pn.pane.PNG(width=300)
image_interim = pn.pane.PNG(width=300)
image_final = pn.pane.PNG(width=300)
capacity = pn.pane.Str("Hello")
country = "Denmark"
def b(event):
    global country
    country = event.new.lower()
    file_name = os.path.join(os.getcwd(),'satellite_images',event.new+'_raw.png')
    image_raw.object = file_name
    image_interim.object =""
    image_final.object =""

def load_interim_image(event):
    print(country)
    interim_file_name = os.path.join(os.getcwd(),'satellite_images',country+'_contour.png')
    output_file_name = os.path.join(os.getcwd(),'satellite_images',country+'_final.png')
    print(interim_file_name)
    image_interim.object = interim_file_name
    image_final.object = output_file_name
    capacity.object = "Current Volume in Barrels" + str(oil_levels[country])

menu_button.on_click(b)
analyze_button.on_click(load_interim_image)
print(oil_levels[country.lower()])
pn.Row(menu_button,pn.Column(image_raw,analyze_button),pn.Row(image_interim,image_final),capacity, height=300).servable()