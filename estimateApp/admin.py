from django.contrib import admin
from .models import BusinessProfile,Estimate,EstimateItem,MaterialDescription,UserProfile

# Register your models here.
admin.site.register(BusinessProfile)
admin.site.register(Estimate)
admin.site.register(EstimateItem)
admin.site.register(MaterialDescription)
admin.site.register(UserProfile)
