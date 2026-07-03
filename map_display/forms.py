from django import forms
from .models import LegislativeDistrict
import csv

class DistrictUpdateForm(forms.ModelForm):
    class Meta:
        model = LegislativeDistrict
        fields = ['collected_signatures', 'difficulty', 'partners', 'partner_mobilized']
