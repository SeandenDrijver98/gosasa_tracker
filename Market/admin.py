import json
from datetime import datetime, timedelta
from typing import Dict, Callable, List

from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, QuerySet, Avg
from django.db.models.functions import TruncDay

from Sales.views import AnalyticsView
from .models import TrackedProduct, DailyPrice
from .tasks import crawl_market_products
admin.site.register(TrackedProduct)


@admin.action(description="Collect today's market prices")
def scrape_daily_prices(DailyPriceAdmin, request, queryset):
    crawl_market_products.delay()


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'product', 'price')
    list_filter = ('product',)
    change_list_template = 'admin/daily_price/change_list.html'
    actions = [scrape_daily_prices]

    @staticmethod
    def _get_product_data_last_month(product:TrackedProduct) -> str:
        last_4_weeks = datetime.now() - timedelta(weeks=4)
        last_4_weeks_qs = DailyPrice.objects.filter(product=product, date_created__gte=last_4_weeks)

        product_data = list(
            last_4_weeks_qs.annotate(x=TruncDay("date_created"))
                .values("x")
                .annotate(y=Avg("price"))
                .order_by("-x")
        )

        start_date = last_4_weeks.date()
        start_date_present = False
        for x_y in product_data:
            if x_y["x"] == start_date:
                start_date_present = True

        if not start_date_present:
            product_data.append({"x": start_date, "y": 0})

        context = json.dumps(product_data, cls=DjangoJSONEncoder)

        return context

    def changelist_view(self, request, extra_context=None):
        extra_context = []
        colours = ["#4f48e2", "#e24848", "#fbb117", "#ffa97e", "#007474", "#c5d165", "#aaaacc", "#99cccc", "#aa40ff"]
        for i, product in enumerate(TrackedProduct.objects.all()):
          extra_context.append((
              str(product), self._get_product_data_last_month(product), colours[i],
          ))

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context={"chart_data": extra_context})
