from typing import Dict

from django.contrib import admin
from django.db.models.functions import TruncDay
from django.shortcuts import redirect
from .models import Product, Market, DeliveryNote, DailySale, DeliveredProduct, ItemSale
from datetime import timezone, timedelta, datetime
from .views import AnalyticsView


admin.site.site_header = "Farm Gosasa"

class ItemSaleInline(admin.TabularInline):
    model = ItemSale


class DeliveredProductsInline(admin.TabularInline):
    model = DeliveredProduct
    readonly_fields = ['unsold_amount',]


class DailySaleInline(admin.TabularInline):
    model = DailySale


class DailySaleAdmin(admin.ModelAdmin):
    inlines = [ItemSaleInline,]


class DeliveryNoteAdmin(admin.ModelAdmin):
    inlines = [DeliveredProductsInline,]
    actions = ['add_daily_sale']
    change_list_template = "admin/delivery_note/change_list.html"

    def add_daily_sale(self, request, queryset):
        if queryset.count() > 1:
            raise Exception("Only select 1 Delivery Note")

        delivery_note = queryset.first()
        delivered_products = delivery_note.deliveredproduct_set.all()
        sale = DailySale.objects.create(delivery_note=delivery_note,sale_date=datetime.today())
        for delivered_product in delivered_products:
            ItemSale.objects.create(sale=sale, product=delivered_product.product, quantity=0, payment=0)
        return redirect(f"/admin/Sales/dailysale/{sale.id}/change/")

    add_daily_sale.short_description = "Add a sale to a delivery note."

    @staticmethod
    def _get_chart_data_last_month() -> Dict:
        last_4_weeks = datetime.now() - timedelta(weeks=4)
        last_4_weeks_qs = DeliveryNote.objects.filter(delivery_date__gte=last_4_weeks)
        return AnalyticsView.generate_chart_data(
            last_4_weeks_qs, TruncDay , last_4_weeks
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or self._get_chart_data_last_month()

        # Call the superclass changelist_view to render the page
        print(extra_context)
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Product)
admin.site.register(Market)
admin.site.register(DeliveryNote, DeliveryNoteAdmin)
admin.site.register(DailySale, DailySaleAdmin)

