from django.contrib import admin
from .models import TrackedProduct, DailyPrice

admin.site.register(TrackedProduct)


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'product', 'price')
    list_filter = ('product',)
