from django.db import models
import folium

# Create your models here.
map = folium.Map(location=[45.5236, -122.6750], zoom_start=13)
map.save("templates/map_display/home.html")