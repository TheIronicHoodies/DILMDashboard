from django.shortcuts import render
from django.views.generic import TemplateView
import folium
import requests

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = requests.get("https://raw.githubusercontent.com/faeldon/philippines-json-maps/refs/heads/master/2023/geojson/country/medres/country.0.01.json").json()
    
        figure = folium.Figure(width="100%", height="100%") # width and height of the figure that will contain the map
        ph_map = folium.Map(
            COORDINATES,
            width="100%", # width of the map
            height="100%", # height of the map
            zoom_start=8, # the starting zoom
            tiles=None, # desired tile for the map respresentation
            zoom_control=False # controls for zoom level (True by default)
        )
        
        ph_map.add_to(figure)

        folium.GeoJson(PH_BOUNDS, name='philippines').add_to(ph_map)
        folium.LayerControl().add_to(ph_map)

        figure.render()
        return {"map": figure}
    