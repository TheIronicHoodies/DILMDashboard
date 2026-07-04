from django.db import models
import folium

# Create your models here.

class LegislativeDistrict(models.Model):
    legis_dist = models.CharField(max_length=99, unique=True, primary_key=True)
    collected_signatures = models.IntegerField()
    difficulty = models.CharField(max_length=6, choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard')
    ])
    partners = models.CharField(max_length=100, blank=True, null=True)
    partner_mobilized = models.BooleanField(default=False)
    registered_voters = models.IntegerField()

    class Meta:
        verbose_name = "legislative_district"
        verbose_name_plural = "legislative_districts"
    
    def __str__(self):
        return f"{self.legis_dist}"