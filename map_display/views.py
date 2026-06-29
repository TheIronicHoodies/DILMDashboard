from django.views.generic import TemplateView
import folium
import json
import plotly
import plotly.express
import os
import pandas
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        def get_map(json_data_path):
            absolute_path = os.path.join(BASE_DIR, json_data_path)
            with open(absolute_path) as f:
                return json.load(f)

        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = [[3,115],[25,135]]
        PH_COASTLINE = get_map(os.path.join("static", "map_coordinates", "legis_dists.json"))

        data = pandas.read_csv(os.path.join(BASE_DIR, "static", "map_coordinates", "districts_numbers.csv"))

        ph_map = plotly.express.choropleth(
            data_frame=data,
            geojson=PH_COASTLINE,
            featureidkey="properties.legis_dist",
            color="collected_signatures",
        )

        return {"map" : ph_map}
        
        # ph_map = folium.Map(
        #     COORDINATES,
        #     width="100%", # width of the map
        #     height="100%", # height of the map
        #     zoom_start=6, # the starting zoom
        #     tiles=None, # desired tile for the map respresentation
        #     max_bounds=True, # whether to set max bounds to the map (False by default)
        #     max_zoom = 10,
        #     min_zoom = 5,
        #     min_lat=PH_BOUNDS[0][0], 
        #     max_lat=PH_BOUNDS[1][0], 
        #     min_lon=PH_BOUNDS[0][1], 
        #     max_lon=PH_BOUNDS[1][1], 
        #     zoom_control=False # controls for zoom level (True by default)
        # )

        # features = PH_COASTLINE.get("features", [])
        # if not features:
        #     raise ValueError("The GeoJSON file does not contain any features.")

        # missing_property = any(
        #     not (feature.get("properties") or {}).get("legis_dist")
        #     for feature in features
        # )
        # if missing_property:
        #     raise ValueError(
        #         "Each GeoJSON feature must include 'properties.legis_dist' for Choropleth mapping."
        #     )

        # folium.Choropleth(
        #     geo_data=PH_COASTLINE,
        #     data=data,
        #     columns=['legis_dist', 'collected_signatures'],
        #     key_on='feature.properties.legis_dist',
        #     fill_color="PiYG",
        #     fill_opacity=0.5,
        #     line_opacity=0,
        #     line_weight=0,
        #     nan_fill_color="black",
        #     nan_fill_opacity=1,
        # ).add_to(ph_map)

        # # folium.GeoJson(PH_BOUNDS, name='philippines').add_to(ph_map)
        # # folium.LayerControl().add_to(ph_map)

        # figure.render()
        # return {"map": figure}
    