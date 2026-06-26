"""This file sets up the urls for the user_management app."""
from django.urls import path
from .views import DILMLoginView

urlpatterns = [
    path('', DILMLoginView.as_view(), name='login'),
]
app_name = 'user_management'