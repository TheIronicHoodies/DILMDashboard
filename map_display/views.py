from django.shortcuts import render
from django.views.generic import TemplateView
import folium
import json
import os
import requests

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        def get_map(json_data_path):
            with open(json_data_path) as f:
                return json.load(f)
            
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        # PH_BOUNDS = requests.get("https://raw.githubusercontent.com/faeldon/philippines-json-maps/refs/heads/master/2023/geojson/country/medres/country.0.01.json", timeout=10).json()
        # PH_BOUNDS = {}
        PH_BOUNDS = get_map("static/map_coordinates/legis_dists.json")
        # PATH = "static/map_coordinates/"
    
        # for file in os.scandir(PATH):
        #     if file.is_file() and file.name.endswith('.json'):
        #         data=get_map(file)
        #         PH_BOUNDS = {**PH_BOUNDS, **data}

        figure = folium.Figure(width="100%", height="100%") # width and height of the figure that will contain the map
        ph_map = folium.Map(
            COORDINATES,
            width="100%", # width of the map
            height="100%", # height of the map
            zoom_start=6, # the starting zoom
            tiles=None, # desired tile for the map respresentation
            max_bounds=True, # whether to set max bounds to the map (False by default)
            max_zoom = 15,
            min_zoom = 5,
            zoom_control=False # controls for zoom level (True by default)
        )

        folium.Choropleth(
            geo_data=PH_BOUNDS,
            fill_opacity=0.5,
            line_opacity=1,
            line_weight=1,
        ).add_to(ph_map)
        
        ph_map.fit_bounds(ph_map.get_bounds())
        ph_map.add_to(figure)

        # folium.GeoJson(PH_BOUNDS, name='philippines').add_to(ph_map)
        # folium.LayerControl().add_to(ph_map)

        figure.render()
        return {"map": figure}
    