import math
import struct

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
        
        def compute_fill_style(feature):
            district = feature['properties']['legis_dist']
            district_row = csv_data[csv_data['legis_dist'] == district]

            if district_row.empty:
                print("No data for district:", district)
                return {"fillColor": '#000000', "fillOpacity": 1.0}

            collected_signatures = district_row['collected_signatures'].iloc[0]
            collected_signatures = int(str(collected_signatures).replace(',', ''))

            difficulty = district_row['difficulty'].iloc[0] if 'difficulty' in district_row.columns else 'Medium'
            partners = district_row['partners'].iloc[0] if 'partners' in district_row.columns else None
            registered_voters = district_row['registered_voters'].iloc[0]
            registered_voters = int(str(registered_voters).replace(',', ''))
            three_percent = math.ceil(registered_voters * 0.03)

            if pandas.isna(partners) or str(partners).strip() == '':
                return {"fillColor": '#000000', "fillOpacity": 1.0}

            opacity = min(1.0, max(0.0, collected_signatures / max(three_percent, 1)))
            color = '#ffcc00'
            match difficulty:
                case 'Easy':
                    color = '#0099ff'
                case 'Medium':
                    color = '#ffcc00'
                case 'Hard':
                    color = '#ff0088'
                case _:
                    color = '#ffcc00'

            if opacity == 1.0:
                border_weight = 1.0
            elif opacity == 0.0:
                border_weight = 0.0
            else:
                border_weight = 0.5

            return {"fillColor": color, "fillOpacity": opacity, "weight": border_weight}
            
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = [[3,115],[25,135]]
        geo_json_data = get_map("static/map_coordinates/legis_dists.json")
        csv_data = pandas.read_csv("static/map_coordinates/districts_numbers.csv", 
                                   dtype={'partners': str})
        csv_data['partners'] = csv_data['partners'].apply(lambda x: x if pandas.isnull(x) else str(x))

        figure = folium.Figure(width="100%", height="100%") # width and height of the figure that will contain the map
        
        ph_map = folium.Map(
            COORDINATES,
            width="100%", # width of the map
            height="100%", # height of the map
            zoom_start=6, # the starting zoom
            color='white', # background color of the map
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

        # colormap = linear.YlGn_09.scale(
        #     csv_data.collected_signatures.min(),
        #     csv_data.collected_signatures.max()
        # )

        # csv_data_dict = csv_data.set_index('legis_dist')['collected_signatures']

        # base layer
        folium.features.GeoJson(
            geo_json_data,
            fill_color='white',
            fill_opacity=1.0,
            weight=0,
        ).add_to(ph_map)

        folium.features.GeoJson(
            geo_json_data,
            style_function=lambda feature: {
                **compute_fill_style(feature),
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
    