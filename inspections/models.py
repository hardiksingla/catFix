from django.db import models

class Inspection(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    
    signature = models.ImageField(upload_to='signatures/')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    signature = models.ImageField(upload_to='signatures/')
    model_number = models.CharField(max_length=100, null=True, blank=True)  # Add model number
    serial_number = models.CharField(max_length=100, null=True, blank=True)  # Add serial number
    

    def __str__(self):
        return f'{self.customer_name} - {self.customer_id}'
    
class TyreInspection(models.Model):
    inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE)
    left_front_pressure = models.TextField()
    right_front_pressure = models.TextField()
    left_front_condition = models.CharField(max_length=100)
    right_front_condition = models.CharField(max_length=100)
    left_rear_pressure = models.TextField()
    right_rear_pressure = models.TextField()
    left_rear_condition = models.CharField(max_length=100)
    right_rear_condition = models.CharField(max_length=100)
    overall_summary = models.TextField()

class BatteryInspection(models.Model):
    inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE)
    battery_make = models.CharField(max_length=100)
    replacement_date = models.CharField(max_length=10)  # To store date as dd-mm-yyyy
    voltage = models.CharField(max_length=100)
    water_level = models.CharField(max_length=100)
    condition_damage = models.CharField(max_length=100)
    leak_rust = models.CharField(max_length=100)
    overall_summary = models.TextField()

class ExteriorInspection(models.Model):
    inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE)
    rust_damage = models.CharField(max_length=100)
    oil_leak = models.CharField(max_length=100)
    exterior_summary = models.TextField()

class BrakeInspection(models.Model):
    inspection = models.ForeignKey('Inspection', on_delete=models.CASCADE)
    brake_fluid_level = models.CharField(max_length=100)
    brake_condition_front = models.CharField(max_length=100)
    brake_condition_rear = models.CharField(max_length=100)
    emergency_brake = models.CharField(max_length=100)
    brake_summary = models.TextField()

class User(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('service_person', 'Service Person'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES) # You should hash passwords in a real application
    


    def _str_(self):
        return self.username