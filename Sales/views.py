import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncMinute, TruncHour, TruncDay, TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic.base import TemplateView
from typing import Dict, Callable, Any
from .models import DailySale,DeliveryNote

# Create your views here.
def sale_view(self,request):
    products = request.body
    for product in products:
        print('product:', product)
    return HttpResponse(status=201)


class AnalyticsView(TemplateView):
    template_name = "admin_analytics/auto_price_analytics.html"

    def dispatch(self, request, *args, **kwargs):
        """
        if user is authenticated and is_staff allow access.
        otherwise permission denied
        """
        user = request.user
        if not user.is_authenticated:
            return HttpResponse(status=401)
        if not user.is_staff:
            return HttpResponse(status=403)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> Dict[str, Dict[str, Any]]:
        context = super().get_context_data(**kwargs)

        last_year = timezone.now() - relativedelta(years=1)

        last_year_qs = DeliveryNote.objects.filter(delivery_date__gt=last_year)

        context["last_year"] = self.generate_chart_data(
            last_year_qs, TruncMonth, last_year
        )

        return context

    @staticmethod
    def generate_chart_data(
        queryset: QuerySet, trunc_size: Callable, start_date: datetime,
    ) -> Dict:
        chart_data = list(
            queryset.annotate(x=trunc_size("delivery_date"))
            .values("x")
            .annotate(y=Count("id"))
            .order_by("-x")
        )

        total_logs = int(queryset.aggregate(Count("id"))["id__count"])

        current_minute_iso = (
            datetime.now().replace(microsecond=0, second=0).isoformat() + "Z"
        )
        current_minute_already_present = False
        for x_y in chart_data:
            if x_y["x"] == current_minute_iso:
                current_minute_already_present = True

        start_minute_iso = start_date.replace(microsecond=0, second=0).isoformat() + "Z"
        start_minute_already_present = False
        for x_y in chart_data:
            if x_y["x"] == start_minute_iso:
                start_minute_already_present = True

        if not start_minute_already_present:
            chart_data.append({"x": start_minute_iso, "y": 0})

        if not current_minute_already_present:
            chart_data.append({"x": current_minute_iso, "y": 0})

        context = {
            "chart_data": json.dumps(chart_data, cls=DjangoJSONEncoder),
            "total_logs": total_logs,
        }
        return context
