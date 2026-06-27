from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import LoginForm

def login_view(request):
    context ={}
    context['form']= LoginForm(request.POST)
    return render(request, "home.html", context)