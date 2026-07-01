from branca.colormap import linear
from django.views.generic import TemplateView
from folium.plugins import StripePattern
import folium
import geopandas
import json
import math
import os
import pandas
import requests
import struct

# Create your views here.
class MapView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # def get_map(json_data_path):
        #     with open(json_data_path) as f:
        #         return json.load(f)
        
        def compute_fill_style(feature):
            default_style = {
                "fillColor": '#000000',
                "fillOpacity": 1.0,
                "fillPattern": None,
                "weight": 0.0
            }
            district = feature['properties']['legis_dist']
            district_row = csv_data[csv_data['legis_dist'] == district]

            if district_row.empty:
                print("No data for district:", district)
                return default_style

            collected_signatures = district_row['collected_signatures'].iloc[0]
            collected_signatures = int(str(collected_signatures).replace(',', ''))

            difficulty = district_row['difficulty'].iloc[0] if 'difficulty' in district_row.columns else 'Medium'
            partners = district_row['partners'].iloc[0] if 'partners' in district_row.columns else None
            partner_mobilized = district_row['partner_mobilized'].iloc[0] if 'partner_mobilized' in district_row.columns else None
            registered_voters = district_row['registered_voters'].iloc[0]
            registered_voters = int(str(registered_voters).replace(',', ''))
            three_percent = math.ceil(registered_voters * 0.03)

            if pandas.isna(partners) or str(partners).strip() == '':
                return default_style

            default_style['fillOpacity'] = min(1.0, max(0.0, collected_signatures / max(three_percent, 1)))
            match difficulty:
                case 'Easy':
                    default_style['fillColor'] = blue
                    if not partner_mobilized:
                        default_style['fillPattern'] = stripes_blue
                case 'Hard':
                    default_style['fillColor'] = pink
                    if not partner_mobilized:
                        default_style['fillPattern'] = stripes_pink
                case _:
                    default_style['fillColor'] = yellow
                    if not partner_mobilized:
                        default_style['fillPattern'] = stripes_yellow

            if default_style['fillOpacity'] == 1.0:
                default_style['weight'] = 1.0
            elif default_style['fillOpacity'] == 0.0:
                default_style['weight'] = 0.0
            else:
                default_style['weight'] = 0.5
            
            return default_style
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = [[3,115],[25,135]]
        geo_json_data = geopandas.read_file("static/map_coordinates/legis_dists.json")
        csv_data = pandas.read_csv("static/map_coordinates/districts_numbers.csv", dtype={'partners': str})
        
        # Merge CSV data with GeoJSON data
        geo_json_data = geo_json_data.merge(csv_data, on="legis_dist")
        geo_json_data.to_file("static/map_coordinates/legis_dists.geojson", driver="GeoJSON")
        
        # drop unnecessary columns
        for col in ['date', 'validOn', 'validTo', 'ID_0', 'ISO', 'NAME_0', 'ID_1', 'NAME_1', 'ID_2', 'NAME_2', 'ID_3', 'NAME_3', 'NL_NAME_3',
                    'ADM0_EN', 'ADM1_EN', 'ADM2_EN', 'ADM3_EN', 'ADM0_PCODE', 'ADM1_PCODE', 'ADM2_PCODE', 'ADM3_PCODE', 'Shape_Leng', 'Shape_Area',
                    'AREA_SQKM', 'PROVINCE', 'REGION', 'ADM3_REF', 'ADM3ALT1EN', 'ADM3ALT2EN']:
            if col in geo_json_data.columns:
                geo_json_data = geo_json_data.drop(col, axis=1)

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

        # base layer
        folium.features.GeoJson(
            geo_json_data,
            fill_color='white',
            fill_opacity=1.0,
            weight=0,
        ).add_to(ph_map)

        pink = '#ff0088'
        yellow = '#ffcc00'
        blue = '#0099ff'
        stripes_pink = StripePattern(angle=-45, color=pink, opacity=1.0).add_to(ph_map)
        stripes_yellow = StripePattern(angle=-45, color=yellow, opacity=1.0).add_to(ph_map)
        stripes_blue = StripePattern(angle=-45, color=blue, opacity=1.0).add_to(ph_map)

        popup = folium.GeoJsonPopup(
            fields=['legis_dist', 'collected_signatures', 'difficulty', 'partners'],
            aliases=['Legislative District:', 'Collected Signatures:', 'Difficulty:', 'Partners:'],
            localize=True,
            labels=True,
            lazy=True,
            style="""
                background-color: indigo; 
                border: 1px solid black; 
                border-radius: 1em; 
                font-size: 1em;
                padding: 1em;
            """,
        )


        folium.features.GeoJson(
            geo_json_data,
            popup=popup,
            style_function=lambda feature: {
                **compute_fill_style(feature),
                "weight": 0,
            },
            zoom_on_click=False,
        ).add_to(ph_map)

        ph_map.add_to(figure)
        figure.render()
        return {"map": figure}
    