from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    country = models.CharField(max_length=100, null=True,blank=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    view_count = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.user.username}'s Profile"