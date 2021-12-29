from django.core.management.base import BaseCommand
from Market.tasks import send_daily_prices_mail


class Command(BaseCommand):
    help = 'Send Daily Tracked Product Prices'

    def handle(self, *args, **options):
        send_daily_prices_mail()