from django.shortcuts import render
from django.views.generic import TemplateView
import folium

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
    
        figure = folium.Figure(width="100%", height="100%") # width and height of the figure that will contain the map
        ph_map = folium.Map(
            COORDINATES,
            width="50%", # width of the map
            height="50%", # height of the map
            zoom_start=12, # the starting zoom
            tiles="OpenStreetMap", # desired tile for the map respresentation
            zoom_control=True # controls for zoom level (True by default)
        )
        
        ph_map.add_to(figure)

        figure.render()
        return {"map": figure}
    