from branca.colormap import linear
from django.views.generic import TemplateView
import folium
import json
import os
import pandas
import requests

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        def get_map(json_data_path):
            with open(json_data_path) as f:
                return json.load(f)
            
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = [[3,115],[25,135]]
        geo_json_data = get_map("static/map_coordinates/legis_dists.json")
        csv_data = pandas.read_csv("static/map_coordinates/districts_numbers.csv")

        figure = folium.Figure(width="100%", height="100%") # width and height of the figure that will contain the map
        
        ph_map = folium.Map(
            COORDINATES,
            width="100%", # width of the map
            height="100%", # height of the map
            zoom_start=6, # the starting zoom
            tiles=None, # desired tile for the map respresentation
            max_bounds=True, # whether to set max bounds to the map (False by default)
            max_zoom = 10,
            min_zoom = 5,
            min_lat=PH_BOUNDS[0][0],
            max_lat=PH_BOUNDS[1][0],
            min_lon=PH_BOUNDS[0][1],
            max_lon=PH_BOUNDS[1][1],
            zoom_control=False # controls for zoom level (True by default)
        )

        colormap = linear.YlGn_09.scale(
            csv_data.collected_signatures.min(),
            csv_data.collected_signatures.max()
        )

        csv_data_dict = csv_data.set_index('legis_dist')['collected_signatures']

        folium.features.GeoJson(
            geo_json_data,
            style_function=lambda feature: {
                "fillColor": colormap(csv_data_dict[feature["properties"]["legis_dist"]]),
                "color": "#0000ff",
                "weight": 0,
            },
            zoom_on_click=True,
        ).add_to(ph_map)

        # folium.Choropleth(
        #     geo_data=PH_COASTLINE,
        #     fill_color="#0000ff",
        #     fill_opacity=0.5,
        #     line_opacity=0,
        #     line_weight=0,
        #     nan_fill_color="white",
        #     nan_fill_opacity=1,
        # ).add_to(ph_map)

        ph_map.add_to(figure)
        figure.render()
        return {"map": figure}
    