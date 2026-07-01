from django import forms
from .models import FeatureModel
import csv

class FeatureUpdateForm(forms.ModelForm):
    class Meta:
        model = FeatureModel
        fields = ['attribute_name', 'collected_signatures', 'difficulty', 'partners', 'partner_mobilized', 'registered_voters'] 
