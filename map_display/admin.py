from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import LegislativeDistrict

# Register your models here.
@admin.register(LegislativeDistrict)
class LegislativeDistrictAdmin(ModelAdmin):
    model = LegislativeDistrict