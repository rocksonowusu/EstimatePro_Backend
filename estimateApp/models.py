from django.db import models
from django.conf import settings


# Create your models here.
class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    online_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.email
    
class BusinessProfile(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='business_profile'
    )
     # Business details from onboarding
    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    website = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    established = models.CharField(max_length=20, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # The uploaded letterhead image (used as the background for estimates)
    background_image = models.ImageField(upload_to='business_images/', null=True, blank=True)

    def __str__(self):
        return f"BusinessProfile for {self.user.email}"

class Estimate(models.Model):
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name="estimates")
    client_name = models.CharField(max_length=255)
    estimate_title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    workmanship = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total_materials = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estimate_title} for {self.client_name}" 
    
class MaterialDescription(models.Model):
    name = models.CharField(max_length=255, unique=True)
   

    def __str__(self):
        return self.name

class EstimateItem(models.Model):
    UNIT_CHOICES = [
        ('pieces', 'Pieces'),
        ('meters', 'Meters'),
        ('yards', 'Yards'),
        ('feet', 'Feet'),
        ('coils', 'Coils'),
        ('kg', 'Kilograms'),
        ('boxes', 'Boxes'),
        ('units', 'Units'),
    ]
    estimate = models.ForeignKey(Estimate,related_name="items",on_delete=models.CASCADE)
    chosen_material = models.ForeignKey(MaterialDescription, null=True,on_delete=models.SET_NULL)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2,default=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,default=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=2)

    def __str__(self):
        if self.description:
            return self.description
        elif self.chosen_material:
            return self.chosen_material.name
        else:
            return "Estimate Item"