from django.contrib import admin
from .models import TrackedProduct, DailyPrice

admin.site.register(TrackedProduct)
admin.site.register(DailyPrice)
