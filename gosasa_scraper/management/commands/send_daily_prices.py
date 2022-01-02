from django.core.management.base import BaseCommand
from Market.tasks import send_daily_prices_mail
from datetime import datetime

class Command(BaseCommand):
    help = 'Send Daily Tracked Product Prices'

    def handle(self, *args, **options):
        weekday = datetime.weekday()
        if weekday > 4:
            return
        
        send_daily_prices_mail()