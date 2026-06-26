from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.urls import reverse 

# Create your models here.

class CustomUser(AbstractUser):
    name = models.CharField(max_length=99)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name}"
    
    # def get_absolute_url(self):
    #     return reverse("profile-view", args=[self.username])