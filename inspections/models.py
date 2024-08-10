from django.db import models

class Inspection(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    signature = models.ImageField(upload_to='signatures/')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer_name} - {self.customer_id}'
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # You should hash passwords in a real application

    def _str_(self):
        return self.username