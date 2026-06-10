from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.urls import reverse 

# Create your models here.

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=99)
    nickname = models.CharField(max_length=20)

    def __str__(self):
        return self.fullname
    
    # def get_absolute_url(self):
    #     return reverse("profile-view", args=[self.username])