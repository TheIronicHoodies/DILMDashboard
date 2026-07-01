from django.db import models
import folium

# Create your models here.

class FeatureModel(models.Model):
    attribute_name = models.CharField(max_length=100)
    geometry = models.JSONField()

    collected_signatures = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=6, default='Medium')
    partners = models.CharField(max_length=2047, default='', blank=True)
    partner_mobilized = models.BooleanField(default=False)
    registered_voters = models.IntegerField(default=0)