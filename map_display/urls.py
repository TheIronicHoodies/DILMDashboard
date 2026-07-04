from django.urls import path
from .views import MapView, MapUpdateView

urlpatterns = [
    path('', MapView.as_view(), name='map_display'),
    path('', MapUpdateView.as_view(), name='map_update'),
]
app_name = 'map_display'