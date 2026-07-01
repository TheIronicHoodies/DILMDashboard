from django.db import models
import folium

# Create your models here.

class LegislativeDistrict(models.Model):
    legis_dist = models.CharField(max_length=10, unique=True, primary_key=True, editable=False)
    collected_signatures = models.IntegerField()
    difficulty = models.CharField(max_length=6, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ])
    partners = models.CharField(max_length=100, blank=True, null=True)
    partner_mobilized = models.BooleanField(default=False)
    registered_voters = models.IntegerField(editable=False)
    geometry = models.JSONField(editable=False, null=True, blank=True)

    class Meta:
        verbose_name = "Legislative District"
        verbose_name_plural = "Legislative Districts"
    
    def __str__(self):
        return f"{self.legis_dist}"