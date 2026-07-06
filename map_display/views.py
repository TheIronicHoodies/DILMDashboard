from branca.colormap import linear
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from folium.plugins import StripePattern
from .forms import DistrictUpdateForm
from .models import LegislativeDistrict
import folium
import geopandas
import json
import math
import os
import pandas
import requests
import struct

# Create your views here.
class MapView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def post(self, request, *args, **kwargs):
        district = request.POST.get('legis_dist')
        district_obj = LegislativeDistrict.objects.filter(legis_dist=district).first()
        context = self.get_context_data()

        if district_obj is None:
            context['form'] = DistrictUpdateForm(request.POST)
            return render(request, self.template_name, context)

        form = DistrictUpdateForm(request.POST, instance=district_obj)

        if form.is_valid():
            form.save()
            context['form'] = DistrictUpdateForm()
        else:
            context['form'] = form

        context['legislative_districts'] = LegislativeDistrict.objects.all()
        return render(request, self.template_name, context)

    def _compute_fill_style(self, feature, districts_by_name=None, blue=None, yellow=None, pink=None, stripes_blue=None, stripes_yellow=None, stripes_pink=None):
        '''Computes the fill styles for each district based on the latest saved values.'''
        default_style = {
            "fillColor": '#000000',
            "fillOpacity": 1.0,
            "fillPattern": None,
            "weight": 0.0
        }
        district_name = feature['properties']['legis_dist']
        district = None

        if districts_by_name is not None:
            district = districts_by_name.get(district_name)
        elif LegislativeDistrict.objects.filter(legis_dist=district_name).exists():
            district = LegislativeDistrict.objects.get(legis_dist=district_name)

        if district is None:
            return default_style

        collected_signatures = int(getattr(district, 'collected_signatures', 0) or 0)
        difficulty = getattr(district, 'difficulty', 'Medium') or 'Medium'
        partners = getattr(district, 'partners', None)
        partner_mobilized = bool(getattr(district, 'partner_mobilized', False))
        registered_voters = int(feature['properties']['registered_voters'] or 0)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        def parse_geojson_to_db(geojson):
            '''Helper function to parse GeoJSON data and update Django's internal database.'''
            # we'll reformat the data such that it's by legislative district, and
            # not by feature
            districts = []
            for feature in geojson['features']:
                properties = feature['properties']
                legis_dist = properties.get('legis_dist')
                collected_signatures = properties.get('collected_signatures', 0)
                difficulty = properties.get('difficulty', 'Medium')
                partners = properties.get('partners', None)
                partner_mobilized = properties.get('partner_mobilized', False)
                registered_voters = properties.get('registered_voters', 0)

                if not any(dist['legis_dist'] == legis_dist for dist in districts):
                    districts.append({
                        'legis_dist': legis_dist,
                        'collected_signatures': collected_signatures,
                        'difficulty': difficulty,
                        'partners': [partners] if partners else [],
                        'partner_mobilized': partner_mobilized,
                        'registered_voters': registered_voters
                    })

            for district in districts:
                LegislativeDistrict.objects.update_or_create(
                    #TODO: Look into update_or_create documentation
                    legis_dist=district['legis_dist'],
                    collected_signatures=district['collected_signatures'],
                    difficulty=district['difficulty'],
                    partners=district['partners'],
                    partner_mobilized=district['partner_mobilized'],
                    registered_voters=district['registered_voters'],
                    defaults={
                        'collected_signatures': 0,
                        'difficulty': 'Medium',
                        'partners': [],
                        'partner_mobilized': False,
                        'registered_voters': 0
                    }
                )
        
        def parse_db_to_geojson(geojson):
            '''Helper function to parse Django's internal database and update the GeoJSON data.'''
            for district in LegislativeDistrict.objects.all():
                for feature in geojson['features']:
                    if feature['properties']['legis_dist'] == district.legis_dist:
                        feature['properties']['collected_signatures'] = district.collected_signatures
                        feature['properties']['percentage_collected'] = f'{district.collected_signatures / feature["properties"]["registered_voters"] * 100:.2f}%'
                        feature['properties']['difficulty'] = district.difficulty
                        feature['properties']['partners'] = district.partners
                        feature['properties']['partner_mobilized'] = district.partner_mobilized

            return geojson

        def write_geojson_to_file(geojson, output_path):
            '''Write the merged GeoJSON object to disk so the file is updated.'''
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(geojson, file, ensure_ascii=False)
        
        COORDINATES = [12.8797, 121.7740] # Coordinates to the centre of the Philippines
        PH_BOUNDS = [[3,115],[25,135]]

        # Read the GeoJSON and CSV data
        geo_json_data = geopandas.read_file("static/map_coordinates/legis_dists.json")
        csv_data = pandas.read_csv("static/map_coordinates/districts_numbers.csv", dtype={'partners': str})
        csv_data['partners'] = csv_data['partners'].apply(lambda x: x if pandas.isnull(x) else str(x))
        
        # Merge CSV data with GeoJSON data
        geo_json_data = geo_json_data.merge(csv_data, on="legis_dist", how="left")

        # Filter the columns to keep only the necessary ones for the GeoJSON file
        columns_to_keep = [
            "geometry",
            "legis_dist",
            "registered_voters",
            "collected_signatures",
            "percentage_collected",
            "difficulty",
            "partners",
            "partner_mobilized",
        ]
        columns_to_keep = [col for col in columns_to_keep if col in geo_json_data.columns]
        geo_json_data = geo_json_data[columns_to_keep]

        geo_json_data.to_file("static/map_coordinates/legis_dists.geojson", driver="GeoJSON")

        # Upload the data to the database if it does not exist yet
        # This is to ensure all districts exist in the database, but do not
        # overwrite existing data if it already exists
        if not LegislativeDistrict.objects.exists():
            print("Database not yet populated")
            parse_geojson_to_db(json.loads(geo_json_data.to_json()))

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
        stripes_pink = StripePattern(angle=-45, color=pink).add_to(ph_map)
        stripes_yellow = StripePattern(angle=-45, color=yellow).add_to(ph_map)
        stripes_blue = StripePattern(angle=-45, color=blue).add_to(ph_map)

        popup = folium.GeoJsonPopup(
            fields=['legis_dist', 
                    'percentage_collected',
                    'collected_signatures', 
                    'registered_voters', 
                    'difficulty', 
                    'partners'],
            aliases=['Legislative District:', 
                     'Percent Collected:',
                     'Collected Signatures:', 
                     'Registered Voters:', 
                     'Difficulty:', 
                     'Partners:'],
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

        geo_json_data = parse_db_to_geojson(json.loads(geo_json_data.to_json()))
        write_geojson_to_file(geo_json_data, 'static/map_coordinates/legis_dists.geojson')

        districts_by_name = {
            district.legis_dist: district
            for district in LegislativeDistrict.objects.all()
        }

        folium.features.GeoJson(
            geo_json_data,
            popup=popup,
            style_function=lambda feature: {
                **self._compute_fill_style(
                    feature,
                    districts_by_name=districts_by_name,
                    blue=blue,
                    yellow=yellow,
                    pink=pink,
                    stripes_blue=stripes_blue,
                    stripes_yellow=stripes_yellow,
                    stripes_pink=stripes_pink,
                ),
                "weight": 0,
            },
            zoom_on_click=False,
        ).add_to(ph_map)

        ph_map.add_to(figure)
        figure.render()

        context['map'] = figure
        context['form'] = DistrictUpdateForm()
        context['legislative_districts'] = LegislativeDistrict.objects.all()
        return context
    


        



        